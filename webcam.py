import argparse
import asyncio
import json
import logging
import os
import platform
import ssl
from motor_virtual import MotorCtrl
from pathlib import Path
from aiohttp import web
from virtual_track import VirtualTrack
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay, MediaStreamTrack
from aiortc.rtcrtpsender import RTCRtpSender

ROOT = os.path.dirname(__file__)
ROOT_PATH = Path(__file__)
PROJECT_PATH = Path(__file__).parent


relay = None
webcam = None
motor = None
ssl_context = None

def create_local_tracks(play_from, decode):
    global relay, webcam

    if play_from:
        player = MediaPlayer(play_from)
        return player.audio, player.video
    else:
        options = {"framerate": "15", "video_size": "320x240"}
        if relay is None:
            if platform.system() == "Windows":
                webcam = MediaPlayer("video=HP Wide Vision HD Camera", format="dshow", options=options)
            else:
                webcam = MediaPlayer("/dev/video0", format="v4l2", options=options)
            relay = MediaRelay()
        return None, relay.subscribe(webcam.video)

def create_animation() -> MediaStreamTrack:
    global relay
    relay = MediaRelay()
    return relay.subscribe(VirtualTrack())

def force_codec(pc, sender, forced_codec):
    kind = forced_codec.split("/")[0]
    codecs = RTCRtpSender.getCapabilities(kind).codecs
    transceiver = next(t for t in pc.getTransceivers() if t.sender == sender)
    transceiver.setCodecPreferences([codec for codec in codecs if codec.mimeType == forced_codec])


async def index(request):
    content = open(os.path.join(ROOT, "index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)


async def javascript(request):
    content = open(os.path.join(ROOT, "client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)


async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print(f"[[[CONNECTION STATE {pc.connectionState.upper()}]]]")
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    @pc.on('datachannel')
    def on_datachannel(channel):
        global dc
        dc = channel
        print(f"[REMOTE DATACHANNEL]")
        
        @channel.on('message')
        def on_message(message):
            if isinstance(message, str):
                print(f"-> {message}")
                motor_cmd(message)

        @channel.on('close')
        def on_close():
            global channel_open
            channel_open = False
            print(f"[DATACHANNEL CLOSED]")
            motor.stop()

    video = create_animation()

    if video:
        video_sender = pc.addTrack(video)
        force_codec(pc, video_sender, video_codec)


    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    return web.Response(content_type="application/json", text=json.dumps({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}),)

pcs = set()

def motor_cmd(cmd: str):
    if cmd == "front":
        motor.forward()
    elif cmd == "back":
        motor.backward()
    elif cmd == "left":
        motor.left()
    elif cmd == "right":
        motor.right()
    else:
        motor.stop()

async def on_shutdown(app):
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


if __name__ == "__main__":
    motor = MotorCtrl()
    parser = argparse.ArgumentParser(prog="CAMERA TANK", description="WebRTC")
    args = parser.parse_args()
    #if args.cert_file:
    #    ssl_context = ssl.SSLContext()
    #    ssl_context.load_cert_chain(args.cert_file, args.key_file)
    #else:
    ssl_context = None
    video_codec = "video/brg24"
    app = web.Application()
    print(f"ROOT: {ROOT}")
    print(f"PROJECT_PATH: {PROJECT_PATH}")
    print(f"ROOT_PATH: {ROOT_PATH}")
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/client.js", javascript)
    app.router.add_post("/offer", offer)
    app.add_routes([web.static('/static', path=ROOT)])
    web.run_app(app, host="172.31.16.1", port=8090, ssl_context=ssl_context)
    #web.run_app(app, host="192.168.0.96", port=8090, ssl_context=ssl_context)

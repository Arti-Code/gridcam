
var pc = null;
var dc = null;
var socket;
var btn_r;
var cmd = null;

function init() {
    //socket = new WebSocket('ws://127.0.0.1:8080');
    btn_r = document.getElementById("btn-r");
    btn_l = document.getElementById("btn-l");
    btn_f = document.getElementById("btn-f");
    btn_b = document.getElementById("btn-b");
    btn_r.ontouchstart = rightStart;
    btn_l.ontouchstart = leftStart;
    btn_f.ontouchstart = frontStart;
    btn_b.ontouchstart = backStart;
    btn_r.ontouchend = rightEnd;
    btn_l.ontouchend = leftEnd;
    btn_f.ontouchend = frontEnd;
    btn_b.ontouchend = backEnd;
    
    btn_r.onmousedown = rightStart;
    btn_l.onmousedown = leftStart;
    btn_f.onmousedown = frontStart;
    btn_b.onmousedown = backStart;
    btn_r.onmouseup = rightEnd;
    btn_l.onmouseup = leftEnd;
    btn_f.onmouseup = frontEnd;
    btn_b.onmouseup = backEnd;
    cmd = document.getElementById("cmd");
};


function negotiate() {
    pc.addTransceiver('video', {direction: 'recvonly'});
    pc.addTransceiver('audio', {direction: 'recvonly'});
    return pc.createOffer().then(function(offer) {
        return pc.setLocalDescription(offer);
    }).then(function() {
        // wait for ICE gathering to complete
        return new Promise(function(resolve) {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                function checkState() {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                }
                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(function() {
        var offer = pc.localDescription;
        return fetch('/offer', {
            body: JSON.stringify({
                sdp: offer.sdp,
                type: offer.type,
            }),
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST'
        });
    }).then(function(response) {
        return response.json();
    }).then(function(answer) {
        return pc.setRemoteDescription(answer);
    }).catch(function(e) {
        alert(e);
    });
}

function start() {
    init()
    var config = {
        sdpSemantics: 'unified-plan'
    };
    config.iceServers = [{urls: ['stun:stun.l.google.com:19302']}];

    /* if (document.getElementById('use-stun').checked) {
    } */

    pc = new RTCPeerConnection(config);
    var parameters = JSON.parse('{"ordered": true}').value;
    dc = pc.createDataChannel('link', parameters);
    dc.onopen = function() {
        console.log("open channel");
    };
    dc.onmessage = function(evt) {
        console.log("->"+evt.data);
    };

    pc.addEventListener('track', function(evt) {
        if (evt.track.kind == 'video') {
            document.getElementById('video').srcObject = evt.streams[0];
        } else {
            document.getElementById('audio').srcObject = evt.streams[0];
        }
    });

    document.getElementById('start').style.display = 'none';
    negotiate();
    document.getElementById('stop').style.display = 'inline-block';
}

function stop() {
    document.getElementById('stop').style.display = 'none';
    document.getElementById('start').style.display = 'inline-block';

    // close peer connection
    setTimeout(function() {
        pc.close();
    }, 500);
}


function rightStart() {
    dc.send("right");
    cmd.innerHTML = ("right");
    console.log("right");
}

function leftStart() {
    dc.send("left");
    cmd.innerHTML = "left";
    console.log("left");
}

function frontStart() {
    dc.send("front");
    cmd.innerHTML = "front";
    console.log("front");
}

function backStart() {
    dc.send("back");
    cmd.innerHTML = "back";
    console.log("back");
}

function rightEnd() {
    dc.send("stop");
    cmd.innerHTML = "stop";
    console.log("stop");
}

function leftEnd() {
    dc.send("stop");
    cmd.innerHTML = "stop";
    console.log("stop");
}

function frontEnd() {
    dc.send("stop");
    cmd.innerHTML = "stop";
    console.log("stop");
}

function backEnd() {
    dc.send("stop");
    cmd.innerHTML = "stop";
    console.log("stop");
}
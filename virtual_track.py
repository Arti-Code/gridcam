import math
import cv2
import numpy as np
from av import VideoFrame
from aiortc import VideoStreamTrack


class VirtualTrack(VideoStreamTrack):

    def __init__(self):
        super().__init__()
        self.counter = 0
        height, width = 240, 320
        data = np.ones((height, width, 3), dtype=np.uint8)
        data[0:80, :] = [0, 1, 0]
        data[80:160, :] = [1, 0, 0]
        data[160:241, :] = [0, 0, 1]
        self.frames = []
        for k in range(25):
            self.frames.append(VideoFrame.from_ndarray(data*k*10, format="bgr24"))
        for k in range(25, 0, -1):
            self.frames.append(VideoFrame.from_ndarray(data*k*10, format="bgr24"))

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        frame = self.frames[self.counter % 50]
        frame.pts = pts
        frame.time_base = time_base
        self.counter += 1
        return frame

    def _create_rectangle(self, width, height, color):
        data_bgr = np.zeros((height, width, 3), np.uint8)
        data_bgr[:, :] = color
        return data_bgr
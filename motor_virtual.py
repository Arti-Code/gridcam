from time import sleep


class MotorCtrl():
    
    def __init__(self):
        print("configuring system...")
        self.setup()
        sleep(2)

    def setup(self):
        pass

    def backward(self):
        print("backward")

    def forward(self):
        print("forward")

    def left(self):
        print("left")

    def right(self):
        print("right")

    def stop(self):
        print("stop")

    def finish(self):
        print("cleaningup gpio...")
        sleep(1)

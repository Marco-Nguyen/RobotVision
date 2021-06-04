from threading import Thread

import cv2
from imutils.video import FPS


class VideoGet:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        self.w = self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.h = self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                (self.grabbed, self.frame) = self.stream.read()

    def stop(self):
        self.stopped = True

    def get_size(self):

        return self.w, self.h


class VideoShow:
    def __init__(self, frame=None):
        self.frame = frame
        self.stopped = False

    def start(self):
        Thread(target=self.show, args=()).start()
        return self

    def show(self):
        while not self.stopped:
            cv2.imshow("Video", self.frame)
            if cv2.waitKey(1) == 27:
                self.stopped = True

    def stop(self):
        self.stopped = True


def threadBoth(source=0):
    video_getter = VideoGet(source).start()
    video_shower = VideoShow(video_getter.frame).start()
    fps = FPS().start()
    delay = 0
    while True:
        if video_getter.stopped or video_shower.stopped:
            video_shower.stop()
            video_getter.stop()
            break

        frame = video_getter.frame
        # output_img, cond = myYolo.detector(frame, 0.3, 0.5, delay)
        # if cond:
        #     delay = delay + 1 if delay <= 3 else 0
        cv2.putText(frame, f'{fps.fps()}', (0, 0 +20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, [0,255,255], 1, lineType=cv2.LINE_AA)
        video_shower.frame = frame
        fps.update()
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))


if __name__ == "__main__":
    threadBoth()

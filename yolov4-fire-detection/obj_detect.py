import os
import time
from typing import Any
from ultis.utils.measuring import theta

import cv2
import numpy as np
from imutils.video import FPS
from videoAccelerate import *
from ultis import *


class Yolov4:
    def __init__(self, net_path, config, label) -> None:
        self.net_path = net_path
        self.config = config
        self.label = label
        self.old_indices = []
        self.old_boxes = []
        self.old_id = []
        self.old_conf = []
        self.net = self.create_net(self.config, self.net_path)

    def detector(self, image, confidence_threshold, nms_threshold) -> Any:

        h, w, _ = image.shape
        layer_names = self.net.getLayerNames()
        output_layers = [layer_names[i[0] - 1]
                         for i in self.net.getUnconnectedOutLayers()]

        blob = cv2.dnn.blobFromImage(
            image, 1 / 255., (416, 416), [0, 0, 0], swapRB=True, crop=False)

        self.net.setInput(blob)
        layer_outputs = self.net.forward(output_layers)

        # class_names = []
        # with open(self.label, "r") as f:
        #     class_names = [line.strip() for line in f.readlines()]

        class_names = ["Fire"]
        colors = [[0, 255, 255]]

        boxes = []
        confidences = []
        class_ids = []

        for output in layer_outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > confidence_threshold:
                    centerX, centerY, width, height = list(
                        map(int, detection[0:4] * [w, h, w, h]))

                    top_leftX, top_leftY = int(
                        centerX - width / 2), int(centerY - height / 2)
                    width, height = int(width), int(height)

                    boxes.append([top_leftX, top_leftY, width, height])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indices = cv2.dnn.NMSBoxes(
            boxes, confidences, confidence_threshold, nms_threshold)
        self.num_obj = len(indices)

        # # draw boxes
        list_coor = []
        font = cv2.FONT_HERSHEY_SIMPLEX
        for i in range(len(boxes)):
            if i in indices:
                x, y, w, h = boxes[i]
                tag = f"{class_names[class_ids[i]]}:{int(confidences[i]*100)}%"
                color = colors[class_ids[i]]

                cv2.rectangle(image, (x, y), (x + w, y + h),
                              color, thickness=2)
                cv2.putText(image, tag, (x, y - 5), font, 0.6,
                            color, 1, lineType=cv2.LINE_AA)
                cv2.circle(image, (x + w//2, y + h//2), radius=0,
                           color=(0, 0, 255), thickness=3)

                list_coor.append([x, y, w, h])
        cv2.circle(image, (image.shape[1]//2, image.shape[0]//2), radius=0,
                   color=(0, 0, 255), thickness=3)

        return image, list_coor

    def create_net(self, config, net_path):
        net = cv2.dnn.readNetFromDarknet(config, net_path)
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        print("[INFO] Done reading net!")
        return net


# test image


def test_image(path):
    test_img = myYolo.load_image(path)
    t = time.time()
    coor, output_img = myYolo.detector(test_img, 0.7, 0.3)
    print(coor)
    print(time.time() - t, "s")

    cv2.imshow("res", output_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def test_video(path=0):

    # test video
    cap = cv2.VideoCapture(path)
    fps = FPS().start()

    delay = 0
    while cap.isOpened():
        _, frame = cap.read()
        h, w, _ = frame.shape
        # print(h, w)
        # tx = w/1080
        output_img, list_coor = myYolo.detector(frame, 0.4, 0.6)
        # print(output_img.shape)
        # print(list_coor)
        if len(list_coor) == 0:
            x = 0
        else:
            x = w/2 - list_coor[0][0] + list_coor[0][2]//2
        if theta(x, 640, 0.5) != 0.0:
            print(theta(x, 640, 1/3))
        cv2.imshow("result", output_img)
        fps.update()
        if cv2.waitKey(1) == 27:
            break

    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
    cap.release()
    cv2.destroyAllWindows()


def test_video_thread(source=0):
    video_getter = VideoGet(source).start()
    video_shower = VideoShow(video_getter.frame).start()
    fps = FPS().start()
    delay = 0
    try:
        while True:
            if video_getter.stopped or video_shower.stopped:
                video_shower.stop()
                video_getter.stop()
                break

            frame = video_getter.frame
            output_img = myYolo.detector(frame, 0.3, 0.5, delay)
            video_shower.frame = output_img
            fps.update()
        fps.stop()
    except Exception:
        video_shower.stop()
        video_getter.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))


if __name__ == "__main__":
    label = r"backup/obj.names"
    config = r"yolov4-tiny-custom.cfg"
    net_path = r"yolov4-tiny-custom_best.weights"

    print("[INFO] Loading net...")
    t = time.time()
    myYolo = Yolov4(net_path=net_path, config=config, label=label)
    print(f"[INFO] Done in {round(time.time() - t, 2)} s")
    # test_video_thread()
    test_video()

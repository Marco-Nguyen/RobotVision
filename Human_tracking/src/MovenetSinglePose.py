import os
import time

import cv2
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

import utils

MODEL_DIR = r'F:\Laboratories\Lab Robotics&AI\RobotVision\Human_tracking\backup\movenet_model'
model_list = os.listdir(MODEL_DIR)
if len(model_list) == 0:
    raise "no model path in directory"


class MoveNet(object):
    def __init__(self, mode='tflite', model_name='lighting') -> None:
        super().__init__()
        self.mode = mode
        self.model_name = model_name
        self.image_size = 192 if self.model_name == 'lighting' else 256  # if thunder is 256
        self.load_model()

    def load_model(self):
        t = time.time()
        if self.mode == 'super':
            if self.model_name == 'lighting':
                module = hub.load("https://tfhub.dev/google/movenet/singlepose/lightning/3")
            elif self.model_name == 'thunder':
                module = hub.load("https://tfhub.dev/google/movenet/singlepose/thunder/3")
            self.model = module.signatures['serving_default']
            print("load model time: %.2fs" % (time.time() - t))

        elif self.mode == 'tflite':
            if self.model_name == 'lighting':
                model_path = os.path.join(MODEL_DIR, 'lite-model_movenet_singlepose_lightning_3.tflite')
            elif self.model_name == 'thunder':
                model_path = os.path.join(MODEL_DIR, 'lite-model_movenet_singlepose_thunder_3.tflite')
            self.interpreter = tf.lite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            print("load model time: %.2fs" % (time.time() - t))

    def infer(self, image):
        if self.mode == 'super':
            image = tf.convert_to_tensor(image, dtype=tf.uint8)
            image = tf.expand_dims(image, axis=0)
            image = tf.cast(tf.image.resize_with_pad(image, self.image_size, self.image_size), dtype=tf.int32)
            outputs = self.model(image)
            keypoints = outputs['output_0']
            return outputs, keypoints
        elif self.mode == 'tflite':
            image = tf.expand_dims(image, axis=0)
            image = tf.cast(tf.image.resize_with_pad(image, self.image_size, self.image_size), dtype=tf.float32)
            input_details = self.interpreter.get_input_details()
            output_details = self.interpreter.get_output_details()
            self.interpreter.set_tensor(input_details[0]['index'], np.array(image))
            # Invoke inference.
            self.interpreter.invoke()
            # Get the model prediction.
            keypoints_with_scores = self.interpreter.get_tensor(output_details[0]['index'])
            return keypoints_with_scores


def test_video(source=0):
    cap = None
    if source == 'realsense':
        return
    else:
        movenet = MoveNet(model_name='lighting')
        cap = cv2.VideoCapture(source)
        while cap.isOpened():
            ret, frame = cap.read()

            # Reshape image
            img = frame.copy()
            keypoints_with_scores = movenet.infer(img)
            print(keypoints_with_scores)

            # Rendering
            utils.draw_connections(frame, keypoints_with_scores, utils.EDGES, 0.4)
            utils.draw_keypoints(frame, keypoints_with_scores, 0.4)

            cv2.imshow('MoveNet Lightning', frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    test_video()

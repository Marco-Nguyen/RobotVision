import tensorflow as tf
import numpy as np
# from matplotlib import pyplot as plt
import cv2
from realsense_depth import *
import time

# Initialize
# dc = DepthCamera()
focal = 875.81
frame_height = 720
frame_width = 1280

# Which connect to which (17 key points)
#  [nose, left eye, right eye, left ear, right ear, left shoulder, right shoulder, left elbow, right elbow, left wrist,
#  right wrist, left hip, right hip, left knee, right knee, left ankle, right ankle]
EDGES = {
    (0, 1): 'm',
    (0, 2): 'c',
    (1, 3): 'm',
    (2, 4): 'c',
    (0, 5): 'm',
    (0, 6): 'c',
    (5, 7): 'm',
    (7, 9): 'm',
    (6, 8): 'c',
    (8, 10): 'c',
    (5, 6): 'y', # Main body from here
    (5, 11): 'm',
    (6, 12): 'c',
    (11, 12): 'y', # to here
    (11, 13): 'm',
    (13, 15): 'm',
    (12, 14): 'c',
    (14, 16): 'c'
}

# Load model
path = r"D:\Python\Pycharm\Murtaza's workshop\Intermediate\YOLO v3\Depth Camera" \
       r"\lite-model_movenet_singlepose_lightning_3.tflite"
interpreter = tf.lite.Interpreter(model_path=path)
interpreter.allocate_tensors()


# Draw keypoints
def draw_keypoints(frame, keypoints, confidence_threshold, draw=True):
    y, x, c = frame.shape
    shaped = np.squeeze(np.multiply(keypoints, [y, x, 1]))
    body = []
    for idx, kp in enumerate(shaped):
        ky, kx, kp_conf = kp
        if draw:
            if kp_conf > confidence_threshold:
                cv2.circle(frame, (int(kx), int(ky)), 4, (0, 255, 0), -1)
        body.append([int(kx), int(ky)])
    x_c, y_c = np.average(body[0]), np.average(body[1])
    return int(x_c), int(y_c), body


# Draw edges
def draw_connections(frame, keypoints, edges, confidence_threshold, draw=True):
    y, x, c = frame.shape
    shaped = np.squeeze(np.multiply(keypoints, [y, x, 1]))

    for edge, color in edges.items():
        p1, p2 = edge
        y1, x1, c1 = shaped[p1]
        y2, x2, c2 = shaped[p2]
        if draw:
            if (c1 > confidence_threshold) & (c2 > confidence_threshold):
                cv2.line(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 40)


# Calculate angle
def angle_calculation(x, y, dist, x_c=frame_width//2, y_c=frame_height//2):
    hor_angle = np.arcsin((x_c - x)/focal)*180/np.pi
    ver_angle = np.arcsin(np.abs(y_c - y)/focal)*180/np.pi
    dia_angle = np.arcsin(np.sqrt((x_c - x)**2 + (y_c - y)**2)/focal)*180/np.pi
    return hor_angle, ver_angle, dia_angle


# Make predictions
def run():
    cap = cv2.VideoCapture(0)
    pTime = 0
    while True:
        ret, color_frame = cap.read()
        # ret, depth_frame, color_frame = dc.get_frame()


        ## Reshape image
        img = color_frame.copy()
        img = tf.image.resize_with_pad(np.expand_dims(img, axis=0), 192, 192)
        input_image = tf.cast(img, dtype=tf.float32)

        ## Setup input and output
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        ## Make predictions
        interpreter.set_tensor(input_details[0]['index'], np.array(input_image))
        interpreter.invoke()
        keypoints_with_scores = interpreter.get_tensor(output_details[0]['index'])
        # print(keypoints_with_scores)

        ## Rendering
        draw_connections(color_frame, keypoints_with_scores, EDGES, 0.4, draw=False)
        xc, xy, body = draw_keypoints(color_frame, keypoints_with_scores, 0.4, draw=False)

        ## Bounding box
        if len(body) != 0:
            body = np.array(body)
            max_x, min_x = np.max(body[:, 0]), np.min(body[:, 0])
            max_y, min_y = np.max(body[:, 1]), np.min(body[:, 1])
            width, height = max_x - min_y, max_y - min_y
            cv2.rectangle(color_frame, (min_x, min_y), (max_x, max_y), (0, 0, 255), 2)
            print(body)

        ## Get distance and angle
        # distance = depth_frame[ybc, xbc]
        # ha, va, da = angle_calculation(xbc, ybc, distance)
        # distance_hor = distance*np.cos(va)
        # cv2.putText(color_frame, "{:.2f}mm".format(np.abs(distance_hor)), (20, 20),
        #             cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 4)
        # cv2.putText(color_frame, "Angle: {:.2f}".format(ha), (20, 60),
        #             cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 4)
        cv2.imshow('Pose estimation', color_frame)

        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime
        print(fps)
        if cv2.waitKey(1) & 0xFF == 27:
            break


if __name__ == "__main__":
    run()

# X = np.array([[1,-1], [1,1]])
# y = np.array([1,5])
# a, b = np.linalg.inv(X).dot(y)
# print(a, b)
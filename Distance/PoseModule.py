import csv
import cv2
import mediapipe as mp
import numpy as np
import time

from realsense_depth import *

W, H = 1280, 720
focal = 875.81
PATH_TO_CSV = r'F:\Laboratories\Lab Robotics&AI\Dowload\Output_app\modbus_core\backup\values_update.csv'
PATH_TO_MODEL = r"F:\Laboratories\Lab Robotics&AI\RobotVision\Distance\DL_distance\dnn\frozen_inference_graph_coco.pb"


class pose_Detector():
    def __init__(self, mode=False, upBody=False, smooth=True, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.upBody = upBody
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(self.mode, self.upBody, self.smooth, self.detectionCon, self.trackCon)

    def findPose(self, frame, draw=True):
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(frameRGB)
        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(frame, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
        return frame

    def findPosition(self, frame, draw=True):
        lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = frame.shape
                # print(id, lm)
                cx, cy, cz = int(lm.x * w), int(lm.y * h), lm.z
                if (0 <= cx <= W) and (0 <= cy <= H):
                    lmList.append([int(id), cx, cy, float(cz)])
                if draw:
                    cv2.circle(frame, (cx, cy), 2, (0, 0, 255), -1)
        return lmList


# Calculate angle
def angle_calculation(x, y, dist, x_c=W // 2, y_c=H // 2):
    hor_angle = np.arcsin((x_c - x) / focal) * 180 / np.pi
    ver_angle = np.arcsin(np.abs(y_c - y) / focal) * 180 / np.pi
    dia_angle = np.arcsin(np.sqrt((x_c - x)**2 + (y_c - y)**2) / focal) * 180 / np.pi
    return hor_angle, ver_angle, dia_angle


# Update value
def updateValue(line, dist, angle):
    temp_list = []
    line_to_override = {}
    # Read all data from the csv file.
    with open(PATH_TO_CSV, 'r') as b:
        data = csv.reader(b)
        temp_list.extend(data)

    # data to override in the format {line_num_to_override:data_to_write}.
    if line == 1:
        line_to_override = {line: ['dis', 6, 'reg', dist]}
    elif line == 2:
        line_to_override = {line: ['angle', 7, 'reg', angle]}

    # Write data to the csv file and replace the lines in the line_to_override dict.
    with open(PATH_TO_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        for line, row in enumerate(temp_list):
            data = line_to_override.get(line, row)
            writer.writerow(data)


def main():
    """Choose camera"""
    # cap = cv2.VideoCapture(0)
    cap = DepthCamera()
    pTime = 0
    detector = pose_Detector()
    # prev_area = 0
    # prev_max_x, prev_min_y, prev_max_y, prev_min_y = 0, 0, 0, 0
    distance = []
    angle = []
    t0 = time.time()
    while True:
        """Camera"""
        # ret, color_frame = cap.read()
        ret, depth_frame, color_frame = cap.get_frame()
        # print(color_frame.shape)
        frame = detector.findPose(color_frame, draw=False)
        lmList = detector.findPosition(color_frame, draw=False)
        # print(lmList)
        if len(lmList) != 0:
            lmList = np.array(lmList)
            print(lmList)
            max_x, min_x, max_y, min_y = int(np.max(lmList[:, 1])), int(np.min(lmList[:, 1])), \
                int(np.max(lmList[:, 2])), int(np.min(lmList[:, 2]))

            # width, height = max_x - min_y, max_y - min_y
            box_xc, box_yc = int((max_x + min_x) // 2), int((max_y + min_y) // 2)

            if time.time() - t0 >= 0:
                cv2.rectangle(color_frame, (min_x, min_y), (max_x, max_y), (0, 0, 255), 2)
                cv2.circle(color_frame, (box_xc, box_yc), 1, (0, 0, 255), 5)
                """Calculate distacne"""
                # min_z = np.min(lmList[:, 3])

                distance = depth_frame[box_yc, box_xc]
                ha, va, da = angle_calculation(box_xc, box_yc, distance)
                true_dist_hor = distance * np.cos(va)
                cv2.putText(color_frame, "{:.2f}mm".format(np.abs(true_dist_hor)), (20, 20),
                            cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 4)
                cv2.putText(color_frame, "Angle: {:.2f}".format(ha), (20, 60),
                            cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 4)
                t0 = time.time()
            # updateValue(1, true_dist_hor, ha)
            # updateValue(2, true_dist_hor, ha)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(color_frame, str(int(fps)), (20, 100), cv2.FONT_ITALIC, 1, (0, 0, 255), 2)
        cv2.line(color_frame, (W // 2, 0), (W // 2, H - 1), (255, 255, 255), 1)
        cv2.line(color_frame, (0, H // 2), (W - 1, H // 2), (255, 255, 255), 1)

        cv2.imshow("Magic", color_frame)
        key = cv2.waitKey(1)
        if key & 0xFF == 27:
            break


if __name__ == "__main__":
    main()

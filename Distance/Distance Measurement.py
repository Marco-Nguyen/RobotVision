import cv2
import numpy as np
import pyrealsense2 as rs
from realsense_depth import *
import csv

point = (400, 300)
focal = 875.81


def show_distance(event, x, y, args, params):
    global point
    point = (x, y)


def angle_calculation(x_c, y_c, x, y, dist):
    hor_angle = np.arcsin(np.abs(x_c - x)/focal)*180/np.pi
    ver_angle = np.arcsin(np.abs(y_c - y)/focal)*180/np.pi
    dia_angle = np.arcsin(np.sqrt((x_c - x)**2 + (y_c - y)**2)/focal)*180/np.pi
    return hor_angle, ver_angle, dia_angle


# Initialize Camera Intel Realsense
dc = DepthCamera()

# Create a mouse event
cv2.namedWindow('Color frame')
cv2.setMouseCallback("Color frame", show_distance)

# Read csv file
def updateValue(line, dist, angle):
    temp_list = []
    # Read all data from the csv file.
    with open('setpoints.csv', 'r') as b:
        data = csv.reader(b)
        temp_list.extend(data)

    # data to override in the format {line_num_to_override:data_to_write}.
    if line == 4:
        line_to_override = {line: ['dis',6,'reg',dist]}
    elif line == 5:
        line_to_override = {line: ['angle',7,'reg',angle]}

    # Write data to the csv file and replace the lines in the line_to_override dict.
    with open('setpoints.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        for line, row in enumerate(temp_list):
            data = line_to_override.get(line, row)
            writer.writerow(data)


while True:

    ret, depth_frame, color_frame = dc.get_frame()
    # Center point of the frame
    xc = 640
    yc = 360

    # Show distance for a specific point
    cv2.circle(color_frame, (point[0], point[1]), 4, (255, 0, 255), -1)
    cv2.circle(color_frame, (640, 360), 4, (0, 0, 255), -1)
    distance = depth_frame[point[1], point[0]]

    cv2.putText(color_frame, "{}mm".format(distance), (point[0], point[1] + 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 2)
    # cv2.putText(color_frame, "{}, {}".format(point[0], 450), (point[0], 250 - 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 2)

    # Calculate angle
    ha, va, da = angle_calculation(xc, yc, point[0], point[1], distance)
    cv2.putText(color_frame, "Angle: {}".format(ha), (20, 700), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)

    cv2.imshow('Color frame', color_frame)
    # cv2.imshow('Depth frame', depth_frame)

    # Update in csv
    # with open('setpoints.csv', 'w', encoding='UTF8', newline='') as f:
    # lines[4][3] = distance
    # lines[5][3] = ha
    # writer = csv.writer(open('setpoints.csv', 'w'))
    # writer.writerows(lines)
    updateValue(4, distance, ha)
    updateValue(5, distance, ha)

    key = cv2.waitKey(1)
    if key == 27:
        break


import cv2
from realsense_camera import *
from mask_rcnn import *

# Load the Realsense camera
rs = RealsenseCamera()
mrcnn = MaskRCNN()

while True:

    ret, bgr_frame, depth_frame = rs.get_frame_stream()

    # Get object mask
    boxes, classes, contours, centers = mrcnn.detect_objects_mask(bgr_frame)

    # Draw object mask
    bgr_frame = mrcnn.draw_object_mask(bgr_frame)

    # Show depth info of the objects
    mrcnn.draw_object_info(bgr_frame, depth_frame)

    #point_X, point_y = 250, 100
    #distance_mm = depth_frame[point_y, point_X]

    #cv2.circle(bgr_frame, (point_X, point_y), 8, (0, 0, 255), -1)
    #cv2.putText(bgr_frame, "{} mm".format(distance_mm), (point_X, point_y - 20), 0, 1, (0, 0, 255), 2)

    cv2.imshow("Depth frame", depth_frame)
    cv2.imshow("BGR frame", bgr_frame)
    cv2.waitKey(1)

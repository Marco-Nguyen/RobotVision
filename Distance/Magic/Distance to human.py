import cv2
from realsense_depth import *
import csv
import numpy as np
import tensorflow as tf
import pickle

# Initialize
focal = 875.81
dc = DepthCamera()
W, H = 1280, 720


class DetectorAPI:
    def __init__(self, path_to_ckpt):
        self.path_to_ckpt = path_to_ckpt

        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.compat.v1.GraphDef()
            with tf.compat.v1.gfile.GFile(self.path_to_ckpt, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        self.default_graph = self.detection_graph.as_default()
        self.sess = tf.compat.v1.Session(graph=self.detection_graph)

        # Definite input and output Tensors for detection_graph
        self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
        self.detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        self.detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

    def processFrame(self, image):
        # Expand dimensions since the trained_model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image, axis=0)
        # Actual detection.
        # start_time = time.time()
        (boxes, scores, classes, num) = self.sess.run(
            [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: image_np_expanded})
        # end_time = time.time()

        # print("Elapsed Time:", end_time-start_time)

        im_height, im_width, _ = image.shape
        boxes_list = [None for i in range(boxes.shape[1])]
        for i in range(boxes.shape[1]):
            boxes_list[i] = (int(boxes[0,i,0] * im_height),
                        int(boxes[0, i, 1] * im_width),
                        int(boxes[0, i, 2] * im_height),
                        int(boxes[0, i, 3] * im_width))

        return boxes_list, scores[0].tolist(), [int(x) for x in classes[0].tolist()], int(num[0])

    def close(self):
        self.sess.close()
        self.default_graph.close()


def angle_calculation(x_c, y_c, x, y, dist):
    hor_angle = np.arcsin(np.abs(x_c - x)/focal)*180/np.pi
    ver_angle = np.arcsin(np.abs(y_c - y)/focal)*180/np.pi
    dia_angle = np.arcsin(np.sqrt((x_c - x)**2 + (y_c - y)**2)/focal)*180/np.pi
    return hor_angle, ver_angle, dia_angle


def updateValue(line, dist, angle):
    temp_list = []
    line_to_override = {}
    # Read all data from the csv file.
    with open('distance, angle update.csv', 'r') as b:
        data = csv.reader(b)
        temp_list.extend(data)

    # data to override in the format {line_num_to_override:data_to_write}.
    if line == 4:
        line_to_override = {line: ['dis', 6, 'reg', dist]}
    elif line == 5:
        line_to_override = {line: ['angle', 7, 'reg', angle]}

    # Write data to the csv file and replace the lines in the line_to_override dict.
    with open('distance, angle update.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        for line, row in enumerate(temp_list):
            data = line_to_override.get(line, row)
            writer.writerow(data)


# def command(dis, ang, x):
#     if dis > 800:
#         cv2.putText(color_frame, "MOVE!", (20, 20),
#                     cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)
#     else:
#         cv2.putText(color_frame, "STOP", (20, 20),
#                     cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)
#     if ang > 20 and x > 640:
#         cv2.putText(color_frame, "TURN RIGHT", (20, 40),
#                     cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)
#     elif ang > 20 and x < 640:
#         cv2.putText(color_frame, "TURN LEFT", (20, 40),
#                     cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)
#     else:
#         cv2.putText(color_frame, "NO TURN", (20, 40),
#                     cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)


# def update_Pickle(dist, angle):
#     val_update = open("Val_update.pickle", "w")
#     pickle.dump(dist, val_update)
#     pickle.dump(angle, val_update)


def overlap_area(x1, y1, x2, y2):
    top_left = [np.max(x1, x2), np.max(y1, y1)]
    bottom_right = [np.max(x1, x2), np.max(y1, y1)]



if __name__ == "__main__":
    model_path = r"D:\Python\Pycharm\Murtaza's workshop\Intermediate\YOLO v3\Human detection" \
                 r"\faster_rcnn_inception_v2_coco_2018_01_28/frozen_inference_graph.pb"
    odapi = DetectorAPI(path_to_ckpt=model_path)
    threshold = 0.8

    xc = 640
    yc = 360
    dist_array = []
    distance = 0
    while True:
        ret, depth_frame, color_frame = dc.get_frame()

        boxes, scores, classes, num = odapi.processFrame(color_frame)

        # Visualization of the results of a detection.
        prev_box = [0, 0, 1, 1]
        for i in range(len(boxes)):
            # Class 1 represents human
            if classes[i] == 1 and scores[i] > threshold:
                box = boxes[i]
                # overlap_area =
                cv2.rectangle(color_frame, (box[1], box[0]), (box[3], box[2]), (0, 0, 255), 2)
                x_c_human = np.abs(int(box[1] + (box[3] - box[1])/2))
                y_c_human = np.abs(int(box[0] + (box[2] - box[0])/2))
                dist = depth_frame[y_c_human, x_c_human]
                dist_array.append(dist)
                if len(dist_array) == 7:
                    distance = np.average(dist_array)
                    dist_array = []
                ha, va, da = angle_calculation(xc, yc, x_c_human, y_c_human, distance)
                # command(distance, ha, x_c_human)
                cv2.putText(color_frame, "{:.2f}mm".format(distance), (box[1] + 20, box[0] + 20),
                            cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)
                cv2.putText(color_frame, "Angle: {:.2f}".format(ha), (box[1] + 20, box[0] + 40),
                            cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)
                updateValue(4, distance, ha)
                updateValue(5, distance, ha)

        cv2.line(color_frame, (W//2, 0), (W//2, H-1), (255, 255, 255), 1)
        cv2.line(color_frame, (0, H//2), (W-1, H//2), (255, 255, 255), 1)
        cv2.imshow("preview", color_frame)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break




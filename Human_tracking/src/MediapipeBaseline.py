import os

import cv2

try:
    import mediapipe as mp

    # print(mediapipe.__version__)
except Exception as e:
    print(e)
    os.system("pip install mediapipe")


class Pose_model(object):
    def __init__(self,
                 static_image_mode=False,
                 model_complexity=1,
                 smooth_landmarks=True,
                 min_detection_confidence=0.5,
                 min_tracking_confidence=0.5) -> None:
        """Initializes a MediaPipe Pose object.
        Args:
        static_image_mode: Whether to treat the input images as a batch of static
            and possibly unrelated images, or a video stream.
        model_complexity: Complexity of the pose landmark model: 0, 1 or 2.
        smooth_landmarks: Whether to filter landmarks across different input
            images to reduce jitter.
        min_detection_confidence: Minimum confidence value ([0.0, 1.0]) for person
            detection to be considered successful.
        min_tracking_confidence: Minimum confidence value ([0.0, 1.0]) for the
            pose landmarks to be considered tracked successfully.
        """
        super().__init__()
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.model = self.mp_pose.Pose(static_image_mode,
                                       model_complexity,
                                       smooth_landmarks,
                                       min_detection_confidence,
                                       min_tracking_confidence)

    def infer(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.results = self.model.process(image)
        return self.results

    def draw_landmarks(self, image, results):
        self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

    def plot_landmarks(self, image, results):
        self.mp_drawing.plot_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)


def test_video(source=0):
    pose_model = Pose_model(model_complexity=0)
    # model = pose_model.model
    # For webcam input:
    cap = cv2.VideoCapture(source)
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue

        # Flip the image horizontally for a later selfie-view display, and convert
        # the BGR image to RGB.
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        results = pose_model.infer(image)

        # Draw the pose annotation on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        pose_model.mp_drawing.draw_landmarks(
            image, results.pose_landmarks, pose_model.mp_pose.POSE_CONNECTIONS)
        cv2.imshow('MediaPipe Pose', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break
    cap.release()


if __name__ == '__main__':
    test_video()

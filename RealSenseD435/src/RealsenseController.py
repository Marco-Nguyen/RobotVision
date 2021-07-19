import numpy as np
import pyrealsense2 as rs

from threading import Thread
##
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
DEFAULT_FPS = 30
CLIPPING_DISTANCE = 1.5


def spatial_filtering(depth_frame, magnitude=2, alpha=0.5, delta=20, holes_fill=0):
    spatial = rs.spatial_filter()
    spatial.set_option(rs.option.filter_magnitude, magnitude)
    spatial.set_option(rs.option.filter_smooth_alpha, alpha)
    spatial.set_option(rs.option.filter_smooth_delta, delta)
    spatial.set_option(rs.option.holes_fill, holes_fill)
    return spatial.process(depth_frame)


def hole_filling(depth_frame):
    hole_filling = rs.hole_filling_filter()
    depth_frame = hole_filling.process(depth_frame)
    return depth_frame


def temporal_filtering(depth_frame, alpha=0.05, delta=80, holes=5):
    temp_filter = rs.temporal_filter()
    temp_filter.set_option(rs.option.filter_smooth_alpha, alpha)
    temp_filter.set_option(rs.option.filter_smooth_delta, delta)
    temp_filter.set_option(rs.option.hole_filling_filter, holes)
    return temp_filter.process(depth_frame)


class Controller_noThread():
    '''
    Class for convenient control of the RealSense camera
    '''

    def __init__(self, bag_file=None):
        '''
        Constructor, store camera configuration and pipeline
        '''
        self.bag_file = bag_file
        self.setup_config()
        self.config_streamline()
        self.running = True
        pass

    def get_frames(self, need_filter=False):
        '''
        Get frames from camera as numpy arrays
        returns: (rgb, depth) tuple of numpy arrays containing the RGB and the depth images
        '''
        try:
            frames = self.pipeline.wait_for_frames()
            frames = self.align.process(frames)

            self.color_frame = frames.get_color_frame()
            self.depth_frame = frames.get_depth_frame()

            if need_filter:
                self.depth_frame = spatial_filtering(self.depth_frame)
                self.depth_frame = temporal_filtering(self.depth_frame)
                self.depth_frame = hole_filling(self.depth_frame)

            self.depth_color_frame = rs.Colorizer().colorize(self.depth_frame)

            rgb = np.asanyarray(self.color_frame)
            depth = np.asanyarray(self.depth_frame)

            return (rgb, depth)
        except Exception as e:
            raise e

    def setup_config(self):
        config = rs.config()
        if self.bag_file is None:
            config.enable_stream(rs.stream.depth, CAMERA_WIDTH, CAMERA_HEIGHT, rs.format.z16, DEFAULT_FPS)
            config.enable_stream(rs.stream.color, CAMERA_WIDTH, CAMERA_HEIGHT, rs.format.bgr8, DEFAULT_FPS)
        else:
            try:
                config.enable_device_from_file(f"bag_files/{self.bag_file}")
            except Exception as e:
                print(f"Cannot enable device from: {self.bag_file} error: {e}")

        self.config = config

    def config_streamline(self, delay=5):
        # Configure video streams
        self.pipeline = rs.pipeline()
        # Skip 5 first frames to give the Auto-Exposure time to adjust
        for i in range(delay):
            self.pipeline.wait_for_frames()
        # Start streaming
        self.profile = self.pipeline.start(self.config)
        self.align = rs.align(rs.stream.color)
        pass

    def stop(self):
        self.pipeline.stop()
        self.running = False

    def get_intrinsic(self):
        depth_intri = self.depth_frame.profile.as_video_stream_profile().intrinsics
        color_intri = self.color_frame.profile.as_video_stream_profile().intrinsics
        return depth_intri, color_intri

    def get_depth_scale(self):
        return self.profile.get_device().first_depth_sensor().get_depth_scale()

    def get_bg_removal(self):
        """remove background from depth image

        Returns:
            [type]: [description]
        """
        rgb, depth = self.get_frames()
        depth_scale = self.get_depth_scale()
        grey_color = 0
        depth_3d = np.dstack([depth] * 3)
        clipping_distances = CLIPPING_DISTANCE / depth_scale
        bg_removed = np.where((depth_3d > clipping_distances) | (depth_3d <= 0), grey_color, rgb)
        return bg_removed


class Controller_withThread():
    """
    Video streamer that takes advantage of multi-threading, and continuously is reading frames.
    Frames are then ready to read when program requires.
    """

    def __init__(self, video_file=None):
        """
        When initialized, VideoStreamer object should be reading frames
        """
        self.setup_image_config(video_file)
        self.configure_streams()
        self.stopped = False

    def start(self):
        """
        Initialise thread, update method will run under thread
        """
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        """
        Constantly read frames until stop() method is introduced
        """
        while True:

            if self.stopped:
                return

            frames = self.pipeline.wait_for_frames()
            frames = self.align.process(frames)

            color_frame = frames.get_color_frame()
            depth_frame = frames.get_depth_frame()

            self.depth_intrinsic = depth_frame.profile.as_video_stream_profile().intrinsics

            # Convert image to numpy array and initialise images
            self.color_image = np.asanyarray(color_frame.get_data())
            self.depth_image = np.asanyarray(depth_frame.get_data())

    def stop(self):
        self.pipeline.stop()
        self.stopped = True

    def read(self):
        return (self.color_image, self.depth_image)

    def setup_image_config(self, video_file=None):
        """
        Setup config and video steams. If --file is specified as an argument, setup
        stream from file. The input of --file is a .bag file in the bag_files folder.
        .bag files can be created using d435_to_file in the tools folder.
        video_file is by default None, and thus will by default stream from the
        device connected to the USB.
        """
        config = rs.config()

        if video_file is None:

            config.enable_stream(rs.stream.depth, CAMERA_WIDTH, CAMERA_HEIGHT, rs.format.z16, DEFAULT_FPS)
            config.enable_stream(rs.stream.color, CAMERA_WIDTH, CAMERA_HEIGHT, rs.format.bgr8, DEFAULT_FPS)
        else:
            try:
                config.enable_device_from_file("bag_files/{}".format(video_file))
            except:
                print("Cannot enable device from: '{}'".format(video_file))

        self.config = config

    def configure_streams(self):
        # Configure video streams
        self.pipeline = rs.pipeline()

        # Start streaming
        self.profile = self.pipeline.start(self.config)
        self.align = rs.align(rs.stream.color)

    def get_depth_scale(self):
        return self.profile.get_device().first_depth_sensor().get_depth_scale()

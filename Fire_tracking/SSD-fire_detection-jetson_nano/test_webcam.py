import cv2
import os
import time
import torch

from imutils.video import FPS
from nanodet.data.transform import Pipeline
from nanodet.model.arch import build_model
from nanodet.util import Logger
from nanodet.util import cfg
from nanodet.util import load_config
from nanodet.util import load_model_weight


cam_id = 0
config_path = 'fire/nanodet_fire.yml'
model_path = 'fire/model_last.pth'


class Predictor(object):
    def __init__(self, cfg, model_path, logger, device='cuda:0'):
        self.cfg = cfg
        self.device = device if torch.cuda.is_available() else "cpu"
        print(self.device)
        model = build_model(cfg.model)
        ckpt = torch.load(
            model_path, map_location=lambda storage, loc: storage)
        load_model_weight(model, ckpt, logger)
        self.model = model.to(self.device).eval()
        self.pipeline = Pipeline(
            cfg.data.val.pipeline, cfg.data.val.keep_ratio)

    def inference(self, img):
        img_info = {}
        height, width = img.shape[:2]
        img_info['height'] = height
        img_info['width'] = width
        meta = dict(img_info=img_info, raw_img=img, img=img)
        meta = self.pipeline(meta, self.cfg.data.val.input_size)
        meta['img'] = torch.from_numpy(meta['img'].transpose(
            2, 0, 1)).unsqueeze(0).to(self.device)
        with torch.no_grad():
            # set to true to show the timing results
            results = self.model.inference(meta, show=True)
        return meta, results

    def visualize(self, dets, meta, class_names, score_thres, wait=0):
        time1 = time.time()
        bboxes = self.model.head.show_result(
            meta['raw_img'], dets, class_names, score_thres=score_thres, show=True)
        print('viz time: {:.3f}s'.format(time.time() - time1))
        # print(bboxes)


if __name__ == '__main__':
    torch.backends.cudnn.enabled = True
    torch.backends.cudnn.benchmark = True
    load_config(cfg, config_path)
    logger = Logger(-1, use_tensorboard=False)
    predictor = Predictor(cfg, model_path, logger, device='cuda:0')
    logger.log('Press "Esc" to exit.')
    cap = cv2.VideoCapture(cam_id)  # str for video
    # fps = FPS().start()
    t0 = time.time()
    fps = 0
    while True:
        ret_val, frame = cap.read()
        if ret_val is False:
            continue  # skip if capture fail
        meta, res = predictor.inference(frame)
        predictor.visualize(res, meta, cfg.class_names, 0.35)
        # fps.update()
        fps = 1 / (time.time() - t0)
        t0 = time.time()
        ch = cv2.waitKey(1)
        if ch == 27:
            break
    # print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    # print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
    print("[INFO] approx. FPS: {:.2f}".format(fps))

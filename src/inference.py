import torch
import cv2
import numpy as np
from utils.general import non_max_suppression
from utils.downloads import attempt_download

''' 
Class Labels 
Num : 80
'''

classnames = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
        'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
        'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
        'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
        'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
        'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
        'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
        'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
        'hair drier', 'toothbrush']


label = {}
for i, name in enumerate(classnames):
    label[i]=name



# load pre-trained model
weights = './weights/yolov5n.pt'
attempt_download(weights)

try:
    model = torch.load(weights)['model'].float()
    model.eval()
except:
    print('[ERROR] check the model')


def image_loader(img,imsize):
    '''
    processes input image for inference 
    '''
    h, w = img.shape[:2]
    img = cv2.resize(img,(imsize,imsize))
    img = img[:, :, ::-1].transpose(2, 0, 1) 
    img = np.ascontiguousarray(img)
    img = torch.from_numpy(img)
    img = img.float()
    img /= 255.0
    img = img.unsqueeze(0)
    return img, h, w 


def get_pred(img):
    '''
    returns prediction in numpy array
    '''
    imsize = 320
    img, h, w = image_loader(img,imsize)
    pred = model(img)[0]
    pred = non_max_suppression(pred, conf_thres=0.50, iou_thres=0.45,classes=None,agnostic=False,multi_label=False,labels=(),max_det=300,nm=0) # conf_thres is confidence thresold
    if pred[0] is not None:
        gain = imsize / max(h,w)
        pad = (imsize - w * gain) / 2, (imsize - h * gain) / 2  # wh padding
        pred = pred[0]

        pred[:, [0, 2]] -= pad[0]  # x padding
        pred[:, [1, 3]] -= pad[1]  # y padding
        pred[:, :4] /= gain
        pred[:, 0].clamp_(0, w)  # x1
        pred[:, 1].clamp_(0, h)  # y1
        pred[:, 2].clamp_(0, w)  # x2
        pred[:, 3].clamp_(0, h)  # y2

        pred = pred.detach().numpy()

    return pred
                
cam = cv2.VideoCapture(0)

while True:
    check, image = cam.read()
    if image is not None:
        prediction = get_pred(image)

        if prediction is not None:
            for pred in prediction:
                x1 = int(pred[0])
                y1 = int(pred[1])
                x2 = int(pred[2])
                y2 = int(pred[3])

                start = (x1,y1)
                end = (x2,y2)

                pred_data = f'{label[pred[-1]]} {str(pred[-2]*100)[:5]}%'
                print(pred_data)
                color = (0,255,0)
                image = cv2.rectangle(image, start, end, color)
                image = cv2.putText(image, pred_data, (x1,y1+25), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA) 

        cv2.imshow('video', image)

        key = cv2.waitKey(1)
        if key == 27:
            break

cam.release()
cv2.destroyAllWindows()

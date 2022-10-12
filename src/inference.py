import cv2
from component.helper import *



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

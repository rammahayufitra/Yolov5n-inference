import cv2
import requests  # NOTE: Only used for forceful reconnection
import time  # NOTE: Only used for throttling down printing when connection is lost
from component.helper import *


class IPVideoCapture:
    def __init__(self, cam_address, cam_force_address=None, blocking=False):
        """
        :param cam_address: ip address of the camera feed
        :param cam_force_address: ip address to disconnect other clients (forcefully take over)
        :param blocking: if true read() and reconnect_camera() methods blocks until ip camera is reconnected
        """

        self.cam_address = cam_address
        self.cam_force_address = cam_force_address
        self.blocking = blocking
        self.capture = None

        self.RECONNECTION_PERIOD = 0.5  # NOTE: Can be changed. Used to throttle down printing

        self.reconnect_camera()

    def reconnect_camera(self):
        while True:
            try:
                if self.cam_force_address is not None:
                    requests.get(self.cam_force_address)

                self.capture = cv2.VideoCapture(self.cam_address)

                if not self.capture.isOpened():
                    raise Exception("Could not connect to a camera: {0}".format(self.cam_address))

                print("Connected to a camera: {}".format(self.cam_address))

                break
            except Exception as e:
                print(e)

                if self.blocking is False:
                    break

                time.sleep(self.RECONNECTION_PERIOD)

    def read(self):
        """
        Reads frame and if frame is not received tries to reconnect the camera

        :return: ret - bool witch specifies if frame was read successfully
                 frame - opencv image from the camera
        """

        ret, frame = self.capture.read()

        if ret is False:
            self.reconnect_camera()

        return ret, frame


if __name__ == "__main__":
    CAM_ADDRESS = "https://10.162.1.15:8080/video"  # NOTE: Change
    CAM_FORCE_ADDRESS = "http://10.162.1.15:8080/override"  # NOTE: Change or omit
    cam = IPVideoCapture(CAM_ADDRESS, CAM_FORCE_ADDRESS, blocking=True)
    # cap = IPVideoCapture(CAM_ADDRESS)  # Minimal init example

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


            if check is True:
                cv2.imshow(CAM_ADDRESS, image)

            if cv2.waitKey(1) == ord("q"):
                break

cam.release()
cv2.destroyAllWindows()

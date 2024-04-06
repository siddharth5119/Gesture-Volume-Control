import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
import pycaw
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER

wCam, hCam = 640,480

cap = cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.7)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volText = 0


while True:
    success, img =cap.read()
    img = detector.findHands(img)
    lmlist = detector.findPositions(img, draw=False)
    if len(lmlist) !=0:
        #print(lmlist[4], lmlist[8])

        x1,y1 = lmlist[4][1],lmlist[4][2]
        x2,y2 = lmlist[8][1],lmlist[8][2]
        cx,cy = (x1+x2)//2,(y1+y2)//2

        cv2.circle(img, (x1,y1), 15,(255,0,255),cv2.FILLED)
        cv2.circle(img, (x2,y2), 15,(255,0,255),cv2.FILLED)
        #line between index and thump
        cv2.line( img, (x1,y1),(x2,y2),(255,0,255),3)
        #circle in the middle of the line
        cv2.circle(img, (cx,cy), 15,(255,0,255),cv2.FILLED)

        length = math.hypot(x2-x1,y2-y1)
        #print(length)

        #Hand range  20 - 210
        #vol range -63.5 - 0

        vol = np.interp(length,[25,180],[minVol, maxVol])
        volBar = np.interp(length,[25,180],[400,150])
        volText = np.interp(vol,[-100,0],[0,100])

        #print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)

        if length<50:
            cv2.circle(img, (cx,cy), 15,(0,255,0),cv2.FILLED)

    cv2.rectangle(img,(50,150),(85,400), (0,255,0), 3)
    cv2.rectangle(img,(50,int(volBar)),(85,400),(0,255,0),cv2.FILLED)
    cv2.putText(img,f'VOL:{int(volText)}%',(40,90),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),3)


    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}',(40,50),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0),3)
    cv2.imshow("Img",img)
    cv2.waitKey(1)
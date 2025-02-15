import cv2
from pynput.keyboard import Controller
from cvzone.HandTrackingModule import HandDetector
from time import sleep
import numpy as np
import cvzone

# Initialize webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Initialize hand detector with a higher confidence threshold
#detector = HandDetector(detectionCon=0.8, maxHands=1)
detector = HandDetector(detectionCon=int(0.8), maxHands=1)

keys = [["Q", "W", "E", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]]

finalText = ""
keyboard = Controller()

class Button:
    def _init_(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text

def drawALL(img, buttonList):
    imgNew = np.zeros_like(img, np.uint8)
    for button in buttonList:
        x, y = button.pos
        cvzone.cornerRect(imgNew, (x, y, button.size[0], button.size[1]), 20, rt=0)
        cv2.rectangle(imgNew, button.pos, (x + button.size[0], y + button.size[1]), (255, 0, 255), cv2.FILLED)
        cv2.putText(imgNew, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

    out = img.copy()
    alpha = 0.5
    mask = imgNew.astype(bool)
    out[mask] = cv2.addWeighted(img, alpha, imgNew, 1 - alpha, 0)[mask]
    return out

buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
      buttonList.append(Button([100 * j +50, 100 * i +50],key))


while True:
    success, img = cap.read()
    if not success:
        print("Failed to capture image")
        break

    img = detector.findHands(img)
    lmList, bboxInfo = detector.findPosition(img)

    if lmList is None or len(lmList) == 0:
        print("No hand landmarks detected")
        continue

    img = drawALL(img, buttonList)

    if lmList:
        for button in buttonList:
            x, y = button.pos
            w, h = button.size

            if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                cv2.rectangle(img, button.pos, (x + w, y + h), (175, 0, 175), cv2.FILLED)
                cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                l, _, _ = detector.findDistance(8, 12, img, draw=False)
                print(f"Distance: {l}")

                if l < 30:
                    keyboard.press(button.text)
                    cv2.rectangle(img, button.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
                    cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                    finalText += button.text
                    sleep(0.15)

    cv2.rectangle(img, (50, 350), (750, 450), (175, 0, 175), cv2.FILLED)
    cv2.putText(img, finalText, (60, 425), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
import cv2
import numpy as np

cap = cv2.VideoCapture(0)

def nothing(x):
    pass

# ----- สร้างหน้าต่างและกำหนดขนาด -----
cv2.namedWindow("Trackbars", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Trackbars", 400, 300)

cv2.namedWindow("Original", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Original", 480, 360)

cv2.namedWindow("Mask", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Mask", 480,  360)

cv2.namedWindow("Result", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Result", 480, 360)

# ----- สร้าง Trackbars -----
cv2.createTrackbar("H_min", "Trackbars", 0, 179, nothing)
cv2.createTrackbar("H_max", "Trackbars", 179, 179, nothing)
cv2.createTrackbar("S_min", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("S_max", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("V_min", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("V_max", "Trackbars", 255, 255, nothing)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    h_min = cv2.getTrackbarPos("H_min", "Trackbars")
    h_max = cv2.getTrackbarPos("H_max", "Trackbars")
    s_min = cv2.getTrackbarPos("S_min", "Trackbars")
    s_max = cv2.getTrackbarPos("S_max", "Trackbars")
    v_min = cv2.getTrackbarPos("V_min", "Trackbars")
    v_max = cv2.getTrackbarPos("V_max", "Trackbars")

    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])

    mask = cv2.inRange(hsv, lower, upper)
    result = cv2.bitwise_and(frame, frame, mask=mask)

    cv2.imshow("Original", frame)
    cv2.imshow("Mask", mask)
    cv2.imshow("Result", result)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
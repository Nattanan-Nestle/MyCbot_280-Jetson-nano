import cv2
import numpy as np

# ค่าเริ่มต้น (จะถูก calibrate ทีหลัง)
SCALE = 1.0  # mm/pixel (สมมติ)
CX = 320     # กึ่งกลางภาพ x (สำหรับ 640x480)
CY = 240     # กึ่งกลางภาพ y

# โหมด calibrate: ถ้า True จะคำนวณ scale จากวัตถุที่ detect
CALIBRATE_MODE = True
KNOWN_WIDTH_MM = 25  # ขนาดจริงของวัตถุอ้างอิง (mm) เช่น สี่เหลี่ยมกว้าง 50 mm

cap = cv2.VideoCapture(0)  # เปลี่ยน index ตามกล้องที่ใช้
cap.set(3, 640)
cap.set(4, 480)

# เก็บค่า scale ที่ calibrate ได้
calibrated_scales = []

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # หมุนภาพถ้าจำเป็น (ตามการติดตั้งกล้อง)
    # frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    color_ranges = {
        "Red": [(169,192,90), (175,255,255)],
        "Green": [(0,153,100), (77,225,145)],
        "Blue": [(110,146,107), (118,220,171)],
        "Yellow": [(0,210,80), (30,242,255)]
    }

    for color_name, (lower, upper) in color_ranges.items():
        lower = np.array(lower)
        upper = np.array(upper)
        mask = cv2.inRange(hsv, lower, upper)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 1000:
                continue

            approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)
            sides = len(approx)

            shape = ""
            if sides == 4:
                x, y, w, h = cv2.boundingRect(approx)
                ratio = float(w) / h
                if 0.9 <= ratio <= 1.1:
                    shape = "Square"
            elif sides == 6:
                shape = "Hexagon"

            if shape != "":
                # วาด contour
                cv2.drawContours(frame, [approx], -1, (0,255,0), 3)
                cv2.putText(frame, f"{color_name} {shape}",
                            (approx[0][0][0], approx[0][0][1]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

                # คำนวณ centroid
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                else:
                    x, y, w, h = cv2.boundingRect(cnt)
                    cX = x + w//2
                    cY = y + h//2

                # ถ้าอยู่ในโหมด calibrate และ object เป็นสี่เหลี่ยม (หรือมีขนาดรู้ค่า)
                if CALIBRATE_MODE and shape == "Square":
                    # ใช้ bounding box หาขนาดใน pixel
                    x, y, w_pix, h_pix = cv2.boundingRect(cnt)
                    size_pix = (w_pix + h_pix) / 2.0  # ค่าเฉลี่ยความกว้าง-สูง
                    scale = KNOWN_WIDTH_MM / size_pix
                    calibrated_scales.append(scale)
                    # แสดงค่าที่คำนวณได้
                    cv2.putText(frame, f"scale: {scale:.3f} mm/px",
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                                0.7, (0,0,255), 2)
                    # เมื่อ calibrate ไปสักพัก ให้ใช้ค่าเฉลี่ย
                    if len(calibrated_scales) > 10:
                        SCALE = np.mean(calibrated_scales[-10:])
                        cv2.putText(frame, f"Avg scale: {SCALE:.3f} mm/px",
                                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.7, (255,0,0), 2)

                # คำนวณพิกัดโลกโดยใช้ scale ปัจจุบัน
                world_x = (cX - CX) * SCALE
                world_y = (cY - CY) * SCALE

                # แสดงจุด centroid และพิกัด
                cv2.circle(frame, (cX, cY), 5, (0,0,255), -1)
                cv2.putText(frame, f"({world_x:.1f}, {world_y:.1f}) mm",
                            (cX+10, cY-10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0,255,255), 2)

    cv2.imshow("Calibration", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()

# สรุปค่า scale สุดท้าย
if calibrated_scales:
    final_scale = np.mean(calibrated_scales)
    print(f"Calibration complete. Average scale = {final_scale:.4f} mm/pixel")
    print(f"Recommended SCALE value for your code: {final_scale:.4f}")
else:
    print("No calibration data collected.")
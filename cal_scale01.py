#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np

# ------------------------------------------------------------------
# กำหนดค่าคงที่
# ------------------------------------------------------------------
KNOWN_SIZE_MM = 25.0          # ขนาดจริงของวัตถุ (mm) - แก้ไขตามวัตถุของคุณ
CX = 320                      # กึ่งกลางภาพ (สำหรับอ้างอิง)
CY = 240

# ช่วงสี HSV (สามารถปรับได้ตามสภาพแสง)
COLOR_RANGES = {
    "Red":    [(168, 136, 195),  (175, 255, 255)],
    "Green":  [(75, 224, 164),   (86, 255, 199)],
    "Blue":   [(110, 146, 107), (118, 220, 171)],
    "Yellow": [(0, 210, 80),    (30, 242, 255)]
}

# ------------------------------------------------------------------
# ฟังก์ชันตรวจจับวัตถุและคืนค่าขนาด pixel
# ------------------------------------------------------------------
def detect_object_with_size(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    for color_name, (lower, upper) in COLOR_RANGES.items():
        lower = np.array(lower)
        upper = np.array(upper)
        mask = cv2.inRange(hsv, lower, upper)

        # ลด noise
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 500:
                continue

            approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)
            sides = len(approx)

            # ตรวจสอบว่าเป็นสี่เหลี่ยม (อาจเป็นสี่เหลี่ยมจัตุรัสหรือสี่เหลี่ยมผืนผ้า)
            if sides == 4:
                x, y, w, h = cv2.boundingRect(approx)
                ratio = float(w) / h
                # ยอมรับสี่เหลี่ยมที่ใกล้เคียงจัตุรัส (ปรับได้)
                if 0.8 <= ratio <= 1.2:
                    # คำนวณ centroid
                    M = cv2.moments(cnt)
                    if M["m00"] != 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                    else:
                        cX, cY = x + w//2, y + h//2

                    # ขนาดเฉลี่ย (px)
                    size_pix = (w + h) / 2.0
                    # world_x, world_y คำนวณคร่าวๆ (แต่ไม่จำเป็น)
                    world_x = (cX - CX) * 1.0
                    world_y = (cY - CY) * 1.0
                    return world_x, world_y, color_name, "Square", cX, cY, size_pix

    return None

# ------------------------------------------------------------------
# ฟังก์ชันหลัก
# ------------------------------------------------------------------
def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    print("=== Calibrate Scale ===")
    print(f"วางวัตถุขนาด {KNOWN_SIZE_MM} mm ในระยะเดียวกับตอนทำงาน")
    print("กด Space เพื่อคำนวณ scale จากวัตถุที่ตรวจจับได้")
    print("กด ESC เพื่อออกและแสดงค่าเฉลี่ย")
    print("กด 't' เพื่อเปิด/ปิดโหมดปรับ HSV ด้วย trackbar")

    # สร้าง trackbar สำหรับปรับ HSV (optional)
    cv2.namedWindow("Calibrate Scale")
    cv2.createTrackbar("Low H", "Calibrate Scale", 0, 179, lambda x: None)
    cv2.createTrackbar("Low S", "Calibrate Scale", 0, 255, lambda x: None)
    cv2.createTrackbar("Low V", "Calibrate Scale", 0, 255, lambda x: None)
    cv2.createTrackbar("High H", "Calibrate Scale", 179, 179, lambda x: None)
    cv2.createTrackbar("High S", "Calibrate Scale", 255, 255, lambda x: None)
    cv2.createTrackbar("High V", "Calibrate Scale", 255, 255, lambda x: None)

    # ตั้งค่าเริ่มต้นให้ตรงกับสีแดง (อาจต้องปรับ)
    cv2.setTrackbarPos("Low H", "Calibrate Scale", 169)
    cv2.setTrackbarPos("Low S", "Calibrate Scale", 192)
    cv2.setTrackbarPos("Low V", "Calibrate Scale", 90)
    cv2.setTrackbarPos("High H", "Calibrate Scale", 175)
    cv2.setTrackbarPos("High S", "Calibrate Scale", 255)
    cv2.setTrackbarPos("High V", "Calibrate Scale", 255)

    use_trackbar = False
    scales = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # ถ้าใช้ trackbar ให้ใช้ค่าจาก trackbar แทน COLOR_RANGES
        if use_trackbar:
            l_h = cv2.getTrackbarPos("Low H", "Calibrate Scale")
            l_s = cv2.getTrackbarPos("Low S", "Calibrate Scale")
            l_v = cv2.getTrackbarPos("Low V", "Calibrate Scale")
            u_h = cv2.getTrackbarPos("High H", "Calibrate Scale")
            u_s = cv2.getTrackbarPos("High S", "Calibrate Scale")
            u_v = cv2.getTrackbarPos("High V", "Calibrate Scale")
            lower = np.array([l_h, l_s, l_v])
            upper = np.array([u_h, u_s, u_v])
            # ใช้เฉพาะสีที่ปรับ
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, lower, upper)
            # หา contour
            kernel = np.ones((5,5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            result = None
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < 500: continue
                approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(approx)
                    ratio = float(w)/h
                    if 0.8 <= ratio <= 1.2:
                        M = cv2.moments(cnt)
                        if M["m00"] != 0:
                            cX = int(M["m10"] / M["m00"])
                            cY = int(M["m01"] / M["m00"])
                        else:
                            cX, cY = x + w//2, y + h//2
                        size_pix = (w + h) / 2.0
                        world_x = (cX - CX) * 1.0
                        world_y = (cY - CY) * 1.0
                        result = (world_x, world_y, "Selected", "Square", cX, cY, size_pix)
                        break
        else:
            result = detect_object_with_size(frame)

        # วาดกากบาทตรงกลางภาพ (หลังจากตรวจจับ เพื่อไม่ให้รบกวน)
        cv2.line(frame, (0, CY), (frame.shape[1]-1, CY), (0, 0, 255), 1)  # แนวนอน สีแดง
        cv2.line(frame, (CX, 0), (CX, frame.shape[0]-1), (0, 0, 255), 1)  # แนวตั้ง สีแดง

        if result:
            world_x, world_y, color_name, shape, cX, cY, size_pix = result
            # แสดงผล
            cv2.circle(frame, (cX, cY), 5, (0,0,255), -1)
            cv2.putText(frame, f"{color_name} {shape}", (cX+10, cY-20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
            cv2.putText(frame, f"Size: {size_pix:.1f} px", (cX+10, cY+5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 2)

            # แสดงค่า scale เฉลี่ย
            if scales:
                avg_scale = np.mean(scales)
                cv2.putText(frame, f"Avg scale: {avg_scale:.4f} mm/px", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        # แสดงจำนวนตัวอย่าง
        cv2.putText(frame, f"Samples: {len(scales)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)
        cv2.putText(frame, f"Trackbar: {use_trackbar}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)

        cv2.imshow("Calibrate Scale", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == ord(' '):  # Space
            if result:
                size_pix = result[6]
                scale = KNOWN_SIZE_MM / size_pix
                scales.append(scale)
                print(f"scale = {scale:.4f} mm/px (size_pix={size_pix:.1f})")
            else:
                print("ไม่พบวัตถุ")
        elif key == ord('t'):
            use_trackbar = not use_trackbar
            print(f"Use trackbar: {use_trackbar}")

    cap.release()
    cv2.destroyAllWindows()

    if scales:
        final_scale = np.mean(scales)
        print("\n=== ผลลัพธ์ ===")
        print(f"ค่า scale เฉลี่ย = {final_scale:.4f} mm/pixel")
        print(f"แนะนำให้ใช้ SCALE = {final_scale:.4f}")
    else:
        print("ไม่มีข้อมูล")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import time
from pymycobot.mycobot280 import MyCobot280

# ------------------------------------------------------------------
# กำหนดค่าคงที่ (ต้องปรับตามผล calibration ของคุณ)
# ------------------------------------------------------------------
SCALE = 0.3744           # mm/pixel (จาก calibration scale)
CX = 320               # กึ่งกลางภาพ x
CY = 240               # กึ่งกลางภาพ y

# ค่า offset จาก hand‑eye calibration (แก้ไขตามที่วัดได้)
OFFSET_X = 280     # mm
OFFSET_Y = -59      # mm

# ค่า orientation คงที่ (rx, ry, rz) จากท่าที่ใช้ calibrate
# ให้เปลี่ยนเป็นค่าที่อ่านได้จาก mc.get_coords() ขณะ calibrate
FIXED_RX = -178.69  # แก้เป็นค่าจริง
FIXED_RY = -0.29
FIXED_RZ = -45.26

# ความสูงปลอดภัยและความสูงเป้าหมาย (mm)
#SAFE_Z = 250           # สูงกว่าวัตถุ
#TARGET_Z = 200         # ความสูงที่ต้องการให้ปลายแขนอยู่เหนือพื้น (ตอนหยิบ)

# ช่วงสี HSV (จาก detect_cal_codr01.py)
COLOR_RANGES = {
    "Red":    [(168, 136, 195),  (175, 255, 255)],
    "Green":  [(75, 224, 164),   (86, 255, 199)],
    #"Blue":   [(110, 146, 107), (118, 220, 171)],
    #"Yellow": [(0, 210, 80),    (30, 242, 255)]
}

# ความเร็วในการเคลื่อนที่ (0~100)
SPEED = 20

# ------------------------------------------------------------------
# ฟังก์ชันตรวจจับวัตถุ (คืนค่า world_x, world_y, color, shape, cX, cY)
# ------------------------------------------------------------------
def detect_object(frame, scale):
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
            if area < 250:      # ปรับตามขนาดวัตถุ
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

            if shape == "":
                continue

            # คำนวณ centroid
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                x, y, w, h = cv2.boundingRect(cnt)
                cX = x + w//2
                cY = y + h//2

            # คำนวณพิกัดโลกในระบบกล้อง (หน่วย mm)
            world_x = - (cX - CX) * scale
            world_y = (cY - CY) * scale

            return world_x, world_y, color_name, shape, cX, cY

    return None

# ------------------------------------------------------------------
# ฟังก์ชันหลัก
# ------------------------------------------------------------------
def main():
    print("เชื่อมต่อหุ่นยนต์...")
    mc = MyCobot280("/dev/ttyTHS1", 1000000)
    time.sleep(2)

    # 1. ขยับไปท่า home [0,0,0,0,0,0]
    print("กำลังขยับไปท่า home...")
    mc.send_angles([0, 0, 0, 0, 0, 0], SPEED)
    time.sleep(5)

    # 2. ขยับไปท่าที่กล้องมองลง (ตามที่กำหนด)
    print("กำลังขยับไปท่า calibration...")
    mc.send_angles([0, -20, -65, 0, 0, -45], SPEED)
    time.sleep(5)

    # 3. ถ่ายภาพหนึ่งครั้ง
    print("กำลังถ่ายภาพ...")
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)
    for i in range (100):
        ret, frame = cap.read()

    if not ret:
        print("ไม่สามารถอ่านภาพจากกล้องได้")
        return

    cap.release()

    # 4. ตรวจจับวัตถุ
    result = detect_object(frame, SCALE)
    if result is None:
        print("ไม่พบวัตถุในภาพ")
        return
    world_x, world_y, color_name, shape, cX, cY = result
    print(f"พบวัตถุ: {color_name} {shape}")
    print(f"พิกัดจากกล้อง (cam): ({world_x:.1f}, {world_y:.1f}) mm")

    # 5. คำนวณตำแหน่งเป้าหมาย
    target_x = world_x + OFFSET_X
    target_y = world_y + OFFSET_Y
    print(f"ตำแหน่งเป้าหมาย (base): ({target_x:.1f}, {target_y:.1f}")


    # ตรวจสอบว่า target_x, target_y อยู่ใน workspace หรือไม่? (optional)
    # สมมติว่า workspace ประมาณ x: 0~400, y: -300~300
    if target_x < 0 or target_x > 400 or target_y < -300 or target_y > 300:
        print("Warning: ตำแหน่งเป้าหมายอาจอยู่นอก workspace")

    # 6. เคลื่อนที่ไปยังตำแหน่งเหนือวัตถุที่ความสูงปลอดภัยก่อน
    print("เคลื่อนที่ไปยังตำแหน่งเหนือวัตถ (ความสูงปลอดภัย)...")
    mc.send_coords([target_x, target_y, 150.0, FIXED_RX, FIXED_RY, FIXED_RZ], SPEED)
    time.sleep(3)  # รอให้เคลื่อนที่เสร็จ (ควรปรับตามระยะทาง)

    print("สั่ง gripper กางออก...")
    mc.set_gripper_state(0, 100)  # 0 = เปิดสุด, 100 = ความเร็ว
    time.sleep(5)

    ## 7. ตรวจสอบตำแหน่งปัจจุบันก่อนลด Z
    current_coords = mc.get_coords()
    if current_coords:
        print(f"ตำแหน่งปัจจุบัน: x={current_coords[0]:.1f}, y={current_coords[1]:.1f}, z={current_coords[2]:.1f}")

    # 8. ลด Z ลงไปยัง TARGET
    print("ลด Z ลงไปยังตำแหน่งหยิบ...")
    mc.send_coords([target_x , target_y, 95.0, FIXED_RX, FIXED_RY, FIXED_RZ], SPEED)
    time.sleep(3)

    # 9. สั่ง gripper หุบเข้า 
    print("สั่ง gripper หนีบ...")
    mc.set_gripper_state(1, 100)  # 1 = ปิดสุด, 100 = ความเร็ว
    time.sleep(5)


    mc.send_coords([261.7, -60.8, 150.0, FIXED_RX, FIXED_RY, FIXED_RZ], SPEED)


    mc.send_coords([250.7, -60.8, 200.0, FIXED_RX, FIXED_RY, FIXED_RZ], SPEED)

    print("เสร็จสิ้น")

    # (optional) แสดงภาพที่ตรวจจับได้
    cv2.circle(frame, (cX, cY), 5, (255,255,255), -1)
    cv2.putText(frame, f"{color_name} {shape}", (cX+40, cY-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)
    cv2.imshow("Detection", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

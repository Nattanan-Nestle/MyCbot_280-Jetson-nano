#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arm_controller.py

โปรแกรมเชื่อมต่อกับแขนกล MyCobot ผ่าน WiFi (Socket) และส่งคำสั่ง angles หลายท่าตามที่กำหนด
"""

from pymycobot import MyCobotSocket
import time

def main():
    # กำหนด IP และ port ของแขน (แก้ไขให้ตรงกับ IP จริงของแขน)
    ARM_IP = "192.168.137.119"   # ตัวอย่าง
    PORT = 9000                # port เริ่มต้นของ MyCobotSocket

    print(f"กำลังเชื่อมต่อไปยังแขนที่ {ARM_IP}:{PORT}...")
    try:
        arm = MyCobotSocket(ARM_IP, PORT)
        print("เชื่อมต่อสำเร็จ!")
    except Exception as e:
        print(f"เชื่อมต่อล้มเหลว: {e}")
        return

    # กำหนดชุดท่าทาง (angles) ที่ต้องการให้แขนขยับตามลำดับ
    # แต่ละท่าเป็น list [j1, j2, j3, j4, j5, j6] หน่วยองศา
    waypoints = [
        [0, 0, 0, 0, 0, 0],        # ท่า home (0,0,0,...)
        [90, 0, 0, 0, 0, 0],        # หมุนแกน 1 ไป 90°
        [90, -45, 0, 0, 0, 0],      # งอแกน 2
        [0, -90, 0, 0, 0, 0],       # เหยียดแขนออก
        [0, 0, 0, 0, 0, 0],         # กลับบ้าน
    ]

    speed = 50   # ความเร็ว 0-100

    for i, angles in enumerate(waypoints):
        print(f"\nกำลังเคลื่อนที่ไปยังท่าที่ {i+1}: {angles}")
        arm.sync_send_angles(angles, speed)   # รอจนเคลื่อนที่เสร็จ
        time.sleep(1)   # พักระหว่างท่า

    print("\nเสร็จสิ้นทุกท่าทาง")

if __name__ == "__main__":
    main()
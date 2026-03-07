from pymycobot.mycobot280 import MyCobot280
import time

SPEED = 20

mc = MyCobot280("/dev/ttyTHS1", 1000000)

# เคลื่อนที่ไปตำแหน่งแรก และรอจนกว่าจะเสร็จ
mc.sync_send_angles([0, 45, -120, -13, 0, -45], SPEED)
print("ถึงตำแหน่งแรกแล้ว")

# สั่งกริปเปอร์กางออก (เปิด)
print("สั่ง gripper กางออก...")
mc.set_gripper_state(0, 100)   # 0 = เปิด
time.sleep(2)  # รอให้กริปเปอร์ทำงานจริง (อาจใช้ loop ตรวจสอบสถานะได้ แต่โดยทั่วไปสั้น)

# สั่งกริปเปอร์หนีบ (ปิด)
print("สั่ง gripper หนีบ...")
mc.set_gripper_state(1, 100)   # 1 = ปิด
time.sleep(2)

# อ่านตำแหน่งปัจจุบัน
current = mc.get_coords()
if current:
    print(f"ตำแหน่งปัจจุบัน: x={current[0]:.1f}, y={current[1]:.1f}, z={current[2]:.1f}")

# ลด Z ลง (ส่งพิกัดแรก แล้วรอให้เสร็จ)
print("ลด Z ลง...")
mc.sync_send_coords([257.6, -60.4, 300.0, 177.34, 0.57, -45.28], SPEED)

# ลด Z ลงอีก (ส่งพิกัดที่สอง แล้วรอให้เสร็จ)
mc.sync_send_coords([257.6, -60.4, 100.0, 177.34, 0.57, -45.28], SPEED)
print("ถึงตำแหน่งวางแล้ว")

# ปล่อย gripper
print("สั่ง gripper กางออก...")
mc.set_gripper_state(0, 100)
time.sleep(2)

# กลับสู่ท่าเริ่มต้น (หรือท่าที่ต้องการ)
mc.sync_send_angles([0, 45, -120, -13, 0, -45], SPEED)
print("เสร็จสิ้น")
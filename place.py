from pymycobot.mycobot280 import MyCobot280
import time

SPEED = 20

mc = MyCobot280("/dev/ttyTHS1", 1000000)

mc.send_angles([0, 45, -120, -13, 0, -45], SPEED)
time.sleep(5)
print("สั่ง gripper กางออก...")
mc.set_gripper_state(0, 100)   # 0 = เปิด
time.sleep(3)
print("สั่ง gripper หนีบ...")
mc.set_gripper_state(1, 100)   # 0 = เปิด
time.sleep(3)
current = mc.get_coords()
if current:
    print(f"ตำแหน่งปัจจุบัน: x={current[0]:.1f}, y={current[1]:.1f}, z={current[2]:.1f}")

print("ลด Z ลงไปวาง...")
mc.send_coords([257.6, -60.4, 300.0, 177.34, 0.57, -45.28], SPEED)
time.sleep(3)
mc.send_coords([257.6, -60.4, 98.0, 177.34, 0.57, -45.28], SPEED)
time.sleep(3)
print("สั่ง gripper กางออก...")
mc.set_gripper_state(0, 100)   # 0 = เปิด
time.sleep(3)
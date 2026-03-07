# MyCbot_280-Jetson-nano
โค้ดนี้ เป็นโค้ดการทดสอบใช้งาน Cobot 6 DOF MyCobot_280 ในการใช้งานร่วมกับกล้องที่ติดเเบบ Eye in Hand ในการตรวจจับเเละหยิบชิ้นงาน 

วิธีการใช้งานกับ Mycobot280JN 

โหลดโปรเเกรม MobaXtrem  https://mobaxterm.mobatek.net/download.html 

1. เชื่อมต่อจอ เมาส์ คีย์บอร์ดให้เรียบร้อย 
2. เมื่อเชื่อมต่อเสร็จให้เชื่อมต่อ Internet ให้เรียบร้อย 
3. ให้เช็ค IP ของเเขนให้เรียบร้อย ด้วยการเปิด Terminal เเล้วพิมพ์ ip addr 
4. เข้าไปที่ cd catkin/src/mycobot280/mycobot_280jn/script
5. ใช้คำสั่ง git clone https://github.com/Nattanan-Nestle/MyCbot_280-Jetson-nano.git
6. จะได้โฟลเดอร์ MyCbot_280-Jetson-nano มา 
7. เข้าไปที่ cd MyCbot_280-Jetson-nano
8. เชื่อมกล้องเข้าที่เเขน เเล้วลองทดสอบโค้ด ตรวจจับสี color_picker.py
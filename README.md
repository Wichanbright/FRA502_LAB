# FRA502-LAB-6651

**wichan wichayanuparp 6651 (bright)**

โปรเจกต์นี้เป็นงาน LAB ของวิชา FRA502 โดยใช้ ROS2, turtlesim_plus และโหนดสำหรับ Lab2 (eater, killer, turtlesim_pose)

---

## 🔧 ขั้นตอนการติดตั้งและเตรียมโปรเจกต์

### ✅ ขั้นตอนที่ 1: โคลนโปรเจกต์จาก GitHub

```bash
git clone -b LAB2 https://github.com/Wichanbright/FRA502_LAB.git
```

### ✅ ขั้นตอนที่ 2: เข้าสู่ไดเรกทอรีโปรเจกต์

```bash
cd FRA502_LAB
```

### ✅ ขั้นตอนที่ 3: Build โปรเจกต์

```bash
colcon build
```

### ✅ ขั้นตอนที่ 4: ตั้งค่า Workspace

```bash
source install/setup.bash
```

---

# 🚀 การรันโปรเจกต์ (เปิดหลาย Terminal พร้อมกัน)

> แต่ละบล็อกคำสั่งให้เปิดไว้ใน **Terminal แยกกัน** เพื่อให้โหนดทำงานพร้อมกัน

## 🐢 Terminal 1 – รัน turtlesim_plus

```bash
cd FRA502_LAB
source install/setup.bash
ros2 run turtlesim_plus turtlesim_plus_node.py
```

## 🍏 Terminal 2 – รัน eater

```bash
cd FRA502_LAB
source install/setup.bash
ros2 run lab2 eater.py
```

## 💀 Terminal 3 – รัน killer

```bash
cd FRA502_LAB
source install/setup.bash
ros2 run lab2 killer.py
```

## 📍 Terminal 4 – รัน turtlesim_pose

```bash
cd FRA502_LAB
source install/setup.bash
ros2 run lab2 turtlesim_pose.py
```

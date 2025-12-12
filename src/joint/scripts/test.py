import math

# --- ค่าคงที่ของลิงก์ ---
L1 = 0.2         
L2 = 0.25        
L3 = 0.28        
PI = math.pi 
TOLERANCE = 1e-9 # กำหนดค่าความคลาดเคลื่อนเล็กน้อย

# *** แก้ไข: ลบ 'self' ออกจากพารามิเตอร์ฟังก์ชัน ***
def solve_ik_3dof_only(x, y, z, elbow_flag=1):
    
    R_eff_sq = x**2 + y**2
    R_eff = math.sqrt(R_eff_sq)
    Z_eff = z - L1 
    D_sq = R_eff_sq + Z_eff**2
    D = math.sqrt(D_sq)
    
    # ------------------- REACHABILITY CHECK -------------------
    max_reach = L2 + L3 
    min_reach = abs(L2 - L3) 
    
    if D > (max_reach + TOLERANCE) or D < (min_reach - TOLERANCE):
        return None 

    # 2. แก้ Q1 (Yaw)
    q1 = math.atan2(y, x)
    
    # 3. แก้ Q3 (Elbow) (ใช้ Law of Cosines)
    cos_q3 = (D_sq - L2**2 - L3**2) / (2 * L2 * L3)
    cos_q3 = max(min(cos_q3, 1.0), -1.0) 
    sin_q3 = elbow_flag * math.sqrt(1.0 - cos_q3**2)
    q3 = math.atan2(sin_q3, cos_q3)
    
    # 4. แก้ Q2 (Shoulder)
    alpha = math.atan2(Z_eff, R_eff)
    
    # ใช้ Law of Cosines เพื่อหา Beta
    cos_q_B = (D_sq + L2**2 - L3**2) / (2 * D * L2)
    cos_q_B = max(min(cos_q_B, 1.0), -1.0)
    sin_q_B = -elbow_flag * math.sqrt(1.0 - cos_q_B**2)
    beta = math.atan2(sin_q_B, cos_q_B)
    
    q2 = alpha + beta 
    
    return {
        'q1': q1, 
        'q2': q2, 
        'q3': q3
    }

# =================================================================
# --- ตัวอย่างการใช้งาน ---
# =================================================================

# ตำแหน่งเป้าหมาย
XT = 0.2; YT = 0.1; ZT = 0.6
ELBOW = 1 # ศอกขึ้น

# *************************************************************
# *** เรียกใช้ฟังก์ชันที่แก้ไขแล้ว (ไม่มี self ในพารามิเตอร์) ***
# *************************************************************
joint_angles_rad = solve_ik_3dof_only(XT, YT, ZT, ELBOW)

if joint_angles_rad is not None:
    # แปลงเรเดียนเป็นองศา
    q1_deg = math.degrees(joint_angles_rad['q1'])
    q2_deg = math.degrees(joint_angles_rad['q2'])
    q3_deg = math.degrees(joint_angles_rad['q3'])
    
    print(f"✅ IK Solution Found for ({XT:.4f}, {YT:.4f}, {ZT:.4f}):")
    print(f"   Q1 (rad/deg): {joint_angles_rad['q1']:.6f} / {q1_deg:.2f}°")
    print(f"   Q2 (rad/deg): {joint_angles_rad['q2']:.6f} / {q2_deg:.2f}°")
    print(f"   Q3 (rad/deg): {joint_angles_rad['q3']:.6f} / {q3_deg:.2f}°")
else:
    print(f"❌ Target ({XT:.4f}, {YT:.4f}, {ZT:.4f}) is UNREACHABLE. Cannot prepare values.")
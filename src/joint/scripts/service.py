#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from call.srv import Setposi 
from geometry_msgs.msg import PoseStamped
import math
import random
L1 = 0.2         
L2 = 0.25        
L3 = 0.28        
TOLERANCE = 1e-9 
PI = math.pi 
class SimpleMotionSolver(Node):

    def __init__(self):
        super().__init__('randam_node_service')
        
        # สร้าง Service Server โดยใช้ชื่อ 'setposi_service'
        self.srv = self.create_service(Setposi, 'setposi_service', self.setposi_callback)
        self.publisherR = self.create_publisher(PoseStamped, '/target', 10)
        self.publisherF = self.create_publisher(PoseStamped, '/end_effector', 10)
        self.get_logger().info('Setposi Service Server is ready and waiting for requests.')
        self.timer = self.create_timer(0.01, self.timer_callback)
        self.timerR = self.create_timer(10, self.publish_joint_state)
        self.m=0
        self.ran=0
        self.q1=0
        self.q2=0
        self.q3=0
        self.point=[[0.7,1.5,0.5],[1.2,0.2,0.2],[0.1,1.0,0.3],[1.0,1.0,1.0],[-1.2,1.0,1.0]]
    def publish_joint_state(self):
        self.ran=random.randint(0,4)
        # print(self.ran)
    def timer_callback(self):
        # print(self.ran)
        if self.m == 1 :
            self.publish_end_effector_pose(self.q1,self.q2,self.q3)
        elif self.m == 2 :
            pass
        elif self.m == 3 :
            self.publish_end_effector_ran(self.point[self.ran][0],self.point[self.ran][1],self.point[self.ran][2])
        else :
            self.publish_end_effector_pose(0.0,0.0,0.0)
    def setposi_callback(self, request, response):
     
        # 1. ดึงข้อมูลจาก Request (ต้องเข้าถึงผ่าน .data)
        self.m = request.mode.data
        X = request.x.data
        Y = request.y.data
        Z = request.z.data
        vx = request.vx.data
        vy = request.vy.data
        vz = request.vz.data
        if self.m == 1 :
            joint_angles_rad = self.solve_ik_3dof_only(X,Y,Z,1)
            if joint_angles_rad is not None:
                print(joint_angles_rad)
                if self.m==1 :
                    self.q1=joint_angles_rad['q1']
                    self.q2=joint_angles_rad['q2']
                    self.q3=joint_angles_rad['q3']
                response.aram.data = f"state: True  Q1 = {self.q1} rad, Q2 = {self.q2} rad , Q3 = {self.q3} rad"
            else:
                print(f"❌ Target is UNREACHABLE. Cannot prepare values.")
                response.aram.data = '❌ Target is UNREACHABLE. Cannot prepare values.'
        elif self.m == 2 :
            response.aram.data = 'Mode 2 : Teleop Control'
        elif self.m == 3 :
            response.aram.data = 'Mode 3 : Auto Ran Dom Position'  
        else :
            response.aram.data = 'Invalid mode selected. No action taken.'
        return response
    def solve_ik_3dof_only(self,x, y, z, elbow_flag=1):
        # ... (ส่วนคำนวณ R_eff, Z_eff, D)
        R_eff_sq = x**2 + y**2
        R_eff = math.sqrt(R_eff_sq)
        Z_eff = z - L1 
        D_sq = R_eff_sq + Z_eff**2
        D = math.sqrt(D_sq)
        
        # ------------------- REACHABILITY CHECK (แก้ไข) -------------------
        max_reach = L2 + L3 
        min_reach = abs(L2 - L3) 
        
        # *** การแก้ไขที่สำคัญ ***
        # D ต้องไม่เกิน Max Reach + Tolerance
        # D ต้องไม่น้อยกว่า Min Reach - Tolerance
        if D > (max_reach + TOLERANCE) or D < (min_reach - TOLERANCE):
            return None # คืนค่า None เมื่อเข้าถึงไม่ได้

        # ... (โค้ด IK ที่เหลือ)
        # 2. แก้ Q1 (Yaw)
        q1 = math.atan2(y, x)
        
        # 3. แก้ Q3 (Elbow)
        cos_q3 = (D_sq - L2**2 - L3**2) / (2 * L2 * L3)
        
        # การ Clamp ค่า cos_q3 (ยังคงจำเป็นอย่างยิ่ง)
        cos_q3 = max(min(cos_q3, 1.0), -1.0) 
        # ... (โค้ดที่เหลือ)
        sin_q3 = elbow_flag * math.sqrt(1.0 - cos_q3**2)
        q3 = math.atan2(sin_q3, cos_q3)
        
        # 4. แก้ Q2 (Shoulder)
        alpha = math.atan2(Z_eff, R_eff)
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
    def publish_end_effector_pose(self, x, y, z, qx=0.0, qy=0.0, qz=0.0, qw=1.0, frame_id='base_link'):
        msg = PoseStamped()
        
        # --- 1. Header ---
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = frame_id 
        
        # --- 2. Position ---
        msg.pose.position.x = x
        msg.pose.position.y = y
        msg.pose.position.z = z
        
        # --- 3. Orientation (Quaternion) ---
        msg.pose.orientation.x = qx
        msg.pose.orientation.y = qy
        msg.pose.orientation.z = qz
        msg.pose.orientation.w = qw
        
        # 4. เผยแพร่ข้อความ
        self.publisherF.publish(msg)

    def publish_end_effector_ran(self, x, y, z, qx=0.0, qy=0.0, qz=0.0, qw=1.0, frame_id='base_link'):
        msg = PoseStamped()
        
        # --- 1. Header ---
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = frame_id 
        
        # --- 2. Position ---
        msg.pose.position.x = x
        msg.pose.position.y = y
        msg.pose.position.z = z
        
        # --- 3. Orientation (Quaternion) ---
        msg.pose.orientation.x = qx
        msg.pose.orientation.y = qy
        msg.pose.orientation.z = qz
        msg.pose.orientation.w = qw
        
        # 4. เผยแพร่ข้อความ
        self.publisherR.publish(msg)
def main(args=None):
    rclpy.init(args=args)
    simple_solver = SimpleMotionSolver()
    rclpy.spin(simple_solver)
    simple_solver.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
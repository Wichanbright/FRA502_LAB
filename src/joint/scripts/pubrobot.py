#!/usr/bin/python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
from geometry_msgs.msg import PoseStamped
import time

class JointStatePublisher(Node):

    def __init__(self):
        # 1. ตั้งชื่อ Node
        super().__init__('JointState_Publisher_Node')
        self.publisher_ = self.create_publisher(JointState, '/joint_states', 10)
        timer_period = 0.05  
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.x=0
        self.y=0
        self.z=0
        self.joint_names = ['joint_1', 'joint_2', 'joint_3']
        self.subscriptionF = self.create_subscription(PoseStamped,'/end_effector', self.pose_callbackF, 10)
        self.subscriptionR = self.create_subscription(PoseStamped,'/target', self.pose_callbackR, 10)
        
        
        self.get_logger().info('JointState Publisher Node Started (Rate: 20 Hz)')

    def pose_callbackF(self,msg):
        frame_id = msg.header.frame_id
        timestamp_sec = msg.header.stamp.sec
        
        # ดึงข้อมูลตำแหน่ง (Position)
        self.x = msg.pose.position.x
        self.y = msg.pose.position.y
        self.z = msg.pose.position.z
        
        # ดึงข้อมูลการวางแนว (Orientation - Quaternion)
        qx = msg.pose.orientation.x
        qy = msg.pose.orientation.y
        qz = msg.pose.orientation.z
        qw = msg.pose.orientation.w
    def pose_callbackR(self,msg):
        frame_id = msg.header.frame_id
        timestamp_sec = msg.header.stamp.sec
        
        # ดึงข้อมูลตำแหน่ง (Position)
        self.x = msg.pose.position.x
        self.y = msg.pose.position.y
        self.z = msg.pose.position.z
        
        # ดึงข้อมูลการวางแนว (Orientation - Quaternion)
        qx = msg.pose.orientation.x
        qy = msg.pose.orientation.y
        qz = msg.pose.orientation.z
        qw = msg.pose.orientation.w
    def timer_callback(self):
        """ฟังก์ชันที่จะถูกเรียกทุกๆ 0.05 วินาที"""
        self.joint_positions = [float(self.x), (3.1459/2)-float(self.y), -1*float(self.z)] 
        # 1. สร้างข้อความ JointState
        msg = JointState()
        
        # 2. กำหนด Header (สำคัญสำหรับการแสดงผลใน Rviz)
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = '' # เฟรมว่างเปล่าตามที่คุณกำหนด
        
        # 3. กำหนดชื่อและตำแหน่งข้อต่อ
        msg.name = self.joint_names
        msg.position = self.joint_positions
        
        # ไม่ต้องระบุ velocity และ effort ถ้าไม่ได้ใช้ (ค่าดีฟอลต์จะเป็น [] อยู่แล้ว)

        # 4. เผยแพร่ข้อความ
        self.publisher_.publish(msg)
        
        # ตัวอย่างการแสดงผลใน Console (ไม่บังคับ)
        # self.get_logger().info('Publishing Joint State: "%s"' % msg.position)


def main(args=None):
    rclpy.init(args=args)
    joint_state_publisher = JointStatePublisher()
    
    # รัน Node จนกว่าจะถูกปิด
    rclpy.spin(joint_state_publisher)

    # ทำความสะอาด (Destroy) เมื่อ Node ถูกปิด
    joint_state_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
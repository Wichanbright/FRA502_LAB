#!/usr/bin/python3

# =========================
# Imports / Dependencies
# =========================
from universe_1.dummy_module import dummy_function, dummy_var
import numpy as np
import rclpy
import math
import yaml
from rclpy.node import Node
from std_msgs.msg import Int64,Bool
from geometry_msgs.msg import Twist
from std_srvs.srv import Empty
from turtlesim.msg import Pose
from turtlesim.srv import Spawn, Kill
from controller_interfaces.srv import SetParam


# =========================
# Node Definition
# =========================
class EraserNode(Node):
    def __init__(self):
        super().__init__('eraser_node')

        # ---------- Namespace / Topics / Services ----------
        self.name_space = self.get_namespace()
        # Subscriptions
        self.create_subscription(Bool,'/shutdown',self.shut_down,10)
        self.create_subscription(Pose,  self.name_space + '/turtle222/pose',self.pose_callback1,   10)
        self.create_subscription(Pose,  self.name_space + '/teleop/pose',self.pose_callback2,   10)
        self.create_subscription(Pose,  '/Dejavu/pose',self.pose_callback3,   10)
        self.create_subscription(Int64, self.name_space + '/pizza_count',  self.pizza,  10)
        self.create_subscription(Bool, '/status_makeup',                   self.killer, 10)

        #Pub
        self.cmd_vel_pub= self.create_publisher(Twist,self.name_space+'/turtle222/cmd_vel',10)
        self.status_pub= self.create_publisher(Bool,'/status_kill',10)

        # Clients
        self.spawn_turtle_client = self.create_client(Spawn, self.name_space + '/spawn_turtle')
        self.eat_turtle_client   = self.create_client(Kill,  self.name_space + '/remove_turtle')
        self.eat_pizza_client =self.create_client(Empty,self.name_space + '/turtle222/eat')
        # Service server
        self.setparam = self.create_service(SetParam, '/set_controller_param', self.set_param_callback)

        self.create_timer(0.02, self.timer_callback)

        # ---------- Internal State ----------
        self.spawned = False
        self.kill = False
        self.check = False
        self.robot_pose  = np.array([0.0, 0.0, 0.0])
        self.robot_pose2 = np.array([0.0, 0.0, 0.0])
        self.robot_pose3 = np.array([0.0, 0.0, 0.0])
        self.control_robot = np.array([0.0]*12)
        self.data = 0
        self.pizza_count = 0
        self.kp = 2.5
        self.kp_a = 5
        self.c = 0
        self.life = 1
        self.flag =1
        self.warp = 0
        self.statuskill = False
    def shut_down(self,msg):
        if msg.data == True :
            self.shut = True
            self.get_logger().info(f"shutdown eraser: {msg.data}")
            self.destroy_node()
            rclpy.shutdown()
    # =========================
    # Service Callbacks
    # =========================
    def set_param_callback(self, request: SetParam.Request, response: SetParam.Response):
        # รับค่า Kp linear / angular จาก service
        self.kp = request.kp_linear.data
        self.kp_a = request.kp_angular.data
        return response

    # =========================
    # One-shot Spawner / Killer
    # =========================
    def spawnturtle_once(self):
        if self.spawned:
            return
        if not self.spawn_turtle_client.service_is_ready():
            return
        self.spawn_turtle()
        self.spawned = True

    def spawn_turtle(self):
        # ส่งคำขอ spawn เต่าใหม่
        position_requst = Spawn.Request()
        position_requst.x = 0.0
        position_requst.y = 0.0
        position_requst.name = 'turtle222'
        self.spawn_turtle_client.call_async(position_requst)

    def killer_turtle(self):
        # ส่งคำขอ kill เต่าเดิม
        eat_request = Kill.Request()
        eat_request.name = 'teleop'
        self.eat_turtle_client.call_async(eat_request)
    def killself(self):
        # ส่งคำขอ kill เต่าเดิม
        eat_request = Kill.Request()
        eat_request.name = 'turtle222'
        self.eat_turtle_client.call_async(eat_request)

    # =========================
    # Pose Callbacks (อ่านท่า)
    # =========================
    def pose_callback1(self, msg):
        # อัปเดต pose ตัวแรก
        self.robot_pose[0] = msg.x
        self.robot_pose[1] = msg.y
        self.robot_pose[2] = msg.theta

    def pose_callback2(self, msg):
        # อัปเดต pose ตัวที่สอง
        self.robot_pose2[0] = msg.x
        self.robot_pose2[1] = msg.y
        self.robot_pose2[2] = msg.theta

    def pose_callback3(self, msg):
        # อัปเดต pose ตัวที่สาม
        self.robot_pose3[0] = msg.x
        self.robot_pose3[1] = msg.y
        self.robot_pose3[2] = msg.theta
    def start_u2_kill (self):
        msg = Bool()
        msg.data = True
        self.status_pub.publish(msg)
        self.statuskill = True
    # =========================
    # Publishers / Commands
    # =========================
    def cmdvel(self, v, w):
        # ส่งคำสั่งความเร็วให้ตัวหุ่น
        msg = Twist()
        msg.linear.x = v
        msg.angular.z = w
        self.cmd_vel_pub.publish(msg)

    # =========================
    # Misc Callbacks / Data
    # =========================
    def killer(self, msg):
        # อัปเดตสถานะสั่ง kill/spawn จาก Bool
        self.kill = msg.data
        if self.kill:
            self.spawnturtle_once()
            self.path1=self.load_path(1)
            self.path2=self.load_path(2)
            self.path3=self.load_path(3)
            self.path4=self.load_path(4)
            self.pizza_pose = self.path1 + self.path2 + self.path3 + self.path4
            if self.pizza_count == 0 and self.flag:
                self.pizza_count = len(self.pizza_pose)
                self.flag = 0
        # print(self.kill)

    def pizza(self, msg):
        # นับจำนวน pizza
        self.pizza_count = msg.data
    def eat_pizza(self):
         eat_request = Empty.Request()
         self.eat_pizza_client.call_async(eat_request)
    # =========================
    # Control Law
    # =========================
    def control(self):
        
        # คุมตาม delta pose ระหว่างหุ่นสองตัว
        # print(self.control_robot[0])
        print(self.pizza_count)
        if self.pizza_count> 0 :
            self.control_robot[0] = self.pizza_pose[self.c][0] - self.robot_pose[0]  # delta_x
            self.control_robot[1] = self.pizza_pose[self.c][1] - self.robot_pose[1]  # delta_y
        elif (self.pizza_count<= 0 and self.life == 0 ):
            self.control_robot[0] = self.robot_pose3[0]- self.robot_pose[0]  # delta_x
            self.control_robot[1] = self.robot_pose3[1]- self.robot_pose[1]  # delta_y
        else:
            self.control_robot[0] = self.robot_pose2[0] - self.robot_pose[0]  # delta_x
            self.control_robot[1] = self.robot_pose2[1] - self.robot_pose[1]  # delta_y
        self.control_robot[2] = math.atan2(self.control_robot[1], self.control_robot[0])  # theta
        self.control_robot[3] = math.sqrt((self.control_robot[0]**2) + (self.control_robot[1]**2)) # d
        t = self.control_robot[2] - self.robot_pose[2]  # etheta
        self.control_robot[7] = math.atan2(math.sin(t), math.cos(t))  # etheta (wrap)
        self.control_robot[5] = (self.kp)   * (self.control_robot[3])
        self.control_robot[6] = (self.kp_a) * (self.control_robot[7])
        self.cmdvel(self.control_robot[5], self.control_robot[6])
        if self.control_robot[3] <= 0.1:
            if self.life == 0 and self.statuskill == False :
                self.killself()
                self.start_u2_kill()
            if self.pizza_count <= 0 and self.statuskill == False:
                self.killer_turtle()
                self.life = 0
            else :
                self.eat_pizza()
                self.pizza_count -=1
                self.c += 1

    # =========================
    # YAML Loader
    # =========================
    def load_path(self, path_index: int):
        # โหลดพาธเป้าหมายจากไฟล์ YAML
        file_name = f'path{path_index}.yaml'
        try:
            with open(file_name, 'r') as f:
                data = yaml.safe_load(f)
                self.pose_pizza = data.get("pizza_path", [])
        except FileNotFoundError:
            self.get_logger().error(f"File {file_name} not found!")
        except Exception as e:
            self.get_logger().error(f"Error loading {file_name}: {e}")
        return self.pose_pizza

    # =========================
    # Timer
    # =========================
    def timer_callback(self):
        # trigger spawn หนึ่งครั้งเมื่อ kill เป็นจริง
        if self.kill:
            # print(self.pizza_pose)
            self.control()


# =========================
# Main Entrypoint
# =========================
def main(args=None):
    rclpy.init(args=args)
    node = EraserNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

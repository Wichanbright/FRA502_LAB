#!/usr/bin/python3
import os
import rclpy
import yaml
import math
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from controller_interfaces.msg import Keyboard
from turtlesim_plus_interfaces.srv import GivePosition
from std_msgs.msg import Int64,Bool
from std_srvs.srv import Empty
from controller_interfaces.srv import SetMaxPizza
import numpy as np

class Control(Node):
    def __init__(self):
        super().__init__('controller_node')

        self.name_space = self.get_namespace()


        # self.create_subscription(Int64, self.name_space + '/teleop/pizza_count',self.pizza,10)
        self.create_subscription(Keyboard, '/keyboard', self.key_cb, 10)
        self.create_subscription(Bool,'/shutdown',self.shut_down,10)
        self.pose_sub = self.create_subscription(Pose, f'{self.name_space}/teleop/pose', self.pose_cb, 10)
        self.cmd_pub  = self.create_publisher(Twist, f'{self.name_space}/teleop/cmd_vel', 10)
        self.status_start_u2 = self.create_publisher(Bool,'/status_spawn',10)
        self.setpizza = self.create_service(SetMaxPizza,'/set_max_pizza',self.set_pizza_callback)
        self.spawn_cli = self.create_client(GivePosition, f'{self.name_space}/spawn_pizza')
        self.eat_pizza_client =self.create_client(Empty,self.name_space + '/teleop/eat')
        self.cmd_vel_pub= self.create_publisher(Twist,self.name_space+'/teleop/cmd_vel',10)

        self.spawn_cli.wait_for_service(timeout_sec=2.0)
        self.shut = False
        self.state = False
        self.keybool = Keyboard()
        self.keybool.keyboard = [False]*9
        self.pose = np.zeros(3)
        self.num_path = 1
        self.pose_pizza = []
        self.pose_pizzaC = []
        self.pizza_count = 0
        self.pizza_check = 0
        self.set_pizza = 20
        self.kp = 1
        self.kp_a = 5
        self.c = 0
        self.save_count = 0
        self.prev_i = False
        self.prev_i2 = False
        self.flag_clear = 0
        self.control_robot = np.array([0.0]*12)
        self.create_timer(0.02, self.timer_callback)
    def shut_down(self,msg):
        if msg.data == True :
            self.shut = True
            self.get_logger().info(f"shutdown Controller: {msg.data}")
            self.destroy_node()
            rclpy.shutdown()
    def set_pizza_callback(self,request:SetMaxPizza.Request ,response:SetMaxPizza.Response):
        if request.max_piza.data >= self.set_pizza :
            self.set_pizza = request.max_piza.data
            response.log.data = 'pizza max :' + str(self.set_pizza)
        else:
            response.log.data = 'Cant call Set Pizza !!!!!:' + str(self.set_pizza)
        return response
    def pizza(self,msg):
        self.pizza_count = msg.data
        # print(self.pizza_count)
    def key_cb(self, msg: Keyboard):
        kb = list(msg.keyboard)
        if len(kb) < 9:
            kb += [False]*(9 - len(kb))
        self.keybool.keyboard = kb[:9]
        # debug:
        # self.get_logger().info(f"keys: {self.keybool.keyboard}")
    def start(self):
        self.state = Bool()
        self.state.data = True
        self.status_start_u2.publish(self.state)
    def pose_cb(self, msg: Pose):
        self.pose[:] = [msg.x, msg.y, msg.theta]

    def spawn_pizza(self):
        if self.set_pizza > self.pizza_count :
            req = GivePosition.Request()
            req.x, req.y = float(self.pose[0]), float(self.pose[1])
            self.spawn_cli.call_async(req)
            self.pose_pizza.append((float(self.pose[0] ),float(self.pose[1])))
            self.pose_pizzaC.append((float(self.pose[0] ),float(self.pose[1])))
            self.pizza_count +=1
            print(f'{self.set_pizza,self.pizza_count}')
            self.get_logger().info(f"spawn at ({self.pose[0]:.2f}, {self.pose[1]:.2f} :: Pizza {self.pizza_count}/{self.set_pizza})")
        else:
            self.get_logger().info(f"The pizza is done! :: Pizza {self.pizza_count}/{self.set_pizza})")


    def save_path(self):
        if self.num_path <=4:
            print('save')
            data_to_save = {
            "pizza_path": [list(p) for p in self.pose_pizza]
            }
            with open(f'path{self.num_path}.yaml', "w") as f:
                yaml.dump(data_to_save, f)
                self.pose_pizza=[]
            self.get_logger().info(f"Path saved to path{self.num_path}")
            self.num_path += 1
    def eat_pizza(self):
         eat_request = Empty.Request()
         self.eat_pizza_client.call_async(eat_request)
    def controller(self):
        kb = self.keybool.keyboard 
        # print(kb)
        v = 0.0
        w = 0.0

        # map ปุ่ม
        if kb[0]: v = 2.0      # w
        if kb[1]: v = -2.0     # s
        if kb[2]: w = 2.0      # a
        if kb[3]: w = -2.0     # d
        if kb[4]: v, w = 0.0, 0.0   # space
        if kb[5] and not self.prev_i and self.num_path <= 4:
            self.spawn_pizza()  
        if kb[7] and not self.prev_i2:
            self.save_path()
        if kb[8] and self.num_path <= 4:
            if self.pizza_count > 0:
                self.flag_clear = 1
                self.num_path = 1
                self.pose_pizza = []
                self.get_logger().info(f"clear Pizza")
        self.prev_i2 = kb[7]
        self.prev_i = kb[5] # i
        if kb[6]:                   # q
            rclpy.shutdown()
            return

        twist = Twist()
        twist.linear.x  = v
        twist.angular.z = w
        self.cmd_pub.publish(twist)
    def cmdvel(self, v, w):
        msg = Twist()
        msg.linear.x = v
        msg.angular.z = w
        self.cmd_vel_pub.publish(msg)
    def clear_pizz(self):
        self.control_robot[0] = self.pose_pizzaC[self.c][0] - self.pose[0]  # delta_x
        self.control_robot[1] = self.pose_pizzaC[self.c][1] - self.pose[1]  # delta_y
        self.control_robot[2] = math.atan2(self.control_robot[1], self.control_robot[0])  # theta
        self.control_robot[3] = math.sqrt((self.control_robot[0]**2) + (self.control_robot[1]**2)) # d
        t = self.control_robot[2] - self.pose[2]  # etheta
        self.control_robot[7] = math.atan2(math.sin(t), math.cos(t))  # etheta (wrap)
        self.control_robot[5] = (self.kp)   * (self.control_robot[3])
        self.control_robot[6] = (self.kp_a) * (self.control_robot[7])
        self.cmdvel(self.control_robot[5], self.control_robot[6])
        if self.control_robot[3] <= 0.1:
                if len(self.pose_pizzaC)==self.c:
                    self.pose_pizzaC = []
                self.eat_pizza()
                self.pizza_count -=1
                self.c += 1
    def timer_callback(self):
        if self.num_path == 5:
            self.start()
        if self.flag_clear == 1:
            self.clear_pizz()
            if self.pizza_count <= 0:
                self.flag_clear = 0 
        if self.flag_clear == 0:
            self.controller()

def main(args=None):
    rclpy.init(args=args)
    node = Control()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

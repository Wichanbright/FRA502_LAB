#!/usr/bin/python3

import rclpy
import numpy as np
import math
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from std_srvs.srv import Empty
from std_msgs.msg import Bool
from std_msgs.msg import Int64
from turtlesim.srv import Kill
from controller_interfaces.srv import SetParam
from turtlesim.srv import Spawn
import time as t
class DummyNode(Node):
    def __init__(self):
        super().__init__('killer')
        self.namer = self.get_namespace()
        self.declare_parameter('rate', 10.0)
        self.rate = self.get_parameter('rate').get_parameter_value().double_value
        self.declare_parameter('namet', 'turtle1')
        self.name_kill = self.get_parameter('namet').get_parameter_value().string_value
        self.name_kill='/'+self.name_kill
        self.eater = self.create_publisher(Bool,'/state_eat',10)
        self.cmd_vel_pub = self.create_publisher(Twist,self.namer+'/cmd_vel',10)
        self.create_subscription(Bool,'/eat_status',self.state_callback,10)
        self.create_subscription(Pose,self.name_kill+'/pose',self.pose_callback1,10)
        self.create_subscription(Pose,self.namer+'/pose',self.pose_callback2,10)
        self.create_subscription(Int64,self.name_kill+'/pizza_count',self.count_callback,10)
        
        self.setpara =self.create_service(SetParam , '/set_controler_param',self.param_callback)
        self.eat_pizza_client =self.create_client(Empty,self.namer+'/eat')
        self.delturtle =self.create_client(Kill,'/remove_turtle')
        self.spawnturtle =self.create_client(Spawn,'/spawn_turtle')
        self.create_timer(1/float(self.rate),self.timer_callback)
        self.turtle1_pose = np.array([0.0 ,0.0 ,0.0])
        self.turtle2_pose = np.array([0.0 ,0.0 ,0.0])
        self.kp_v=3
        self.kp_w=8
        self.state_pizza=False
        self.state_end=False
        self.count=0
        
        t.sleep(1)
        self.t('turtle1')
        self.spawn(2.0,2.0,self.namer)
        self.spawn(0.0,0.0,self.name_kill)
        print("ok")
    def spawn(self,x,y,n):
        position= Spawn.Request()
        position.x=x
        position.y=y
        position.theta=0.0
        position.name=n
        self.spawnturtle.call_async(position)
    def param_callback(self,request:SetParam.Request, response:SetParam.Response):
        self.kp_v = request.kp_linear.data
        self.kp_w = request.kp_angular.data
        return response
    def t(self,n):
        d=Kill.Request()  
        d.name=n
        self.delturtle.call_async(d)
    def count_callback(self,msg):
        self.count=msg.data
        # print(self.count)
    def eat_turtle(self,s):
        e=Bool()
        e.data=s
        self.eater.publish(e)        
    def state_callback(self,msg):
        self.state_pizza=msg.data
        print(msg.data)
    def cmdvel(self, v, w):
        msg=Twist()
        msg.linear.x =v
        msg.angular.z=w
        self.cmd_vel_pub.publish(msg)
    def pose_callback1(self ,msg):
        self.turtle1_pose[0]=round(msg.x, 2)
        self.turtle1_pose[1]=round(msg.y, 2)
        self.turtle1_pose[2]=round(msg.theta, 2)
        # print(self.turtle1_pose)
    def pose_callback2(self ,msg):
        self.turtle2_pose[0]=round(msg.x, 2)
        self.turtle2_pose[1]=round(msg.y, 2)
        self.turtle2_pose[2]=round(msg.theta, 2)
        # print(self.turtle2_pose)
    def angle(self,x,y):
        Dx=x-self.turtle2_pose[0]
        Dy=y-self.turtle2_pose[1]
        e=math.atan2(Dy,Dx)
        degree=e-self.turtle2_pose[2]
        if e>=(math.pi*0.5) and (e<=math.pi) and self.turtle2_pose[2]<=-(math.pi*0.5) and (self.turtle2_pose[2]>=-math.pi)  :
            degree=-(math.pi*2)-(self.turtle2_pose[2]-e)
        elif self.turtle2_pose[2]>=(math.pi*0.5) and (self.turtle2_pose[2]<=math.pi) and e<=-(math.pi*0.5) and (e>=-math.pi) :
            degree=(math.pi*2)-(self.turtle2_pose[2]-e)  
        return degree
    def Distant(self,x,y):
        Dx=x-self.turtle2_pose[0]
        Dy=y-self.turtle2_pose[1]
        return ((Dx**2)+(Dy**2))**(1/2)
    def eat(self):
        eater=Empty.Request()  
        self.eat_pizza_client.call_async(eater)  
    def timer_callback(self):
        # print(self.state_end)
        if self.state_pizza==True and self.state_end==False:
            if self.Distant(self.turtle1_pose [0],self.turtle1_pose [1])<0.5 and self.angle(self.turtle1_pose [0],self.turtle1_pose [1])<0.1:
                self.t(self.name_kill)
                self.state_end=True
                self.cmdvel(0.0,0.0)
            else:
                self.eat_turtle(False)
            w=self.angle(self.turtle1_pose [0],self.turtle1_pose [1])*4
            V=self.Distant(self.turtle1_pose[0],self.turtle1_pose[1])*1
            self.cmdvel(V,w)
        else:
            self.cmdvel(0.0,0.0)
        
def main(args=None):
    rclpy.init(args=args)
    node = DummyNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()

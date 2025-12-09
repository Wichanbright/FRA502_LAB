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
class DummyNode(Node):
    def __init__(self):
        super().__init__('killer')
        self.eater = self.create_publisher(Bool,'/state_eat',10)
        self.cmd_vel_pub = self.create_publisher(Twist,'/turtle2/cmd_vel',10)
        self.create_subscription(Bool,'/state',self.state_callback,10)
        self.create_subscription(Pose,'/turtle1/pose',self.pose_callback1,10)
        self.create_subscription(Pose,'/turtle2/pose',self.pose_callback2,10)
        self.create_subscription(Int64,'/turtle1/pizza_count',self.count_callback,10)
        self.eat_pizza_client =self.create_client(Empty,'/turtle2/eat')
        self.delturtle =self.create_client(Kill,'/remove_turtle')
        self.create_timer(0.01,self.timer_callback)
        self.turtle1_pose = np.array([0.0 ,0.0 ,0.0])
        self.turtle2_pose = np.array([0.0 ,0.0 ,0.0])
        self.state_pizza=False
        self.state_end=False
        self.count=0
    def t(self):
        d=Kill.Request()  
        d.name='turtle1'
        self.delturtle.call_async(d)
    def count_callback(self,msg):
        self.count=msg.data
        print(self.count)
    def eat_turtle(self,s):
        e=Bool()
        e.data=s
        self.eater.publish(e)        
    def state_callback(self,msg):
        self.state_pizza=msg.data
        # print(msg.data)
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
        print(self.state_end)
        if self.count >4  and self.state_end==False:
            print("kill")
            if self.Distant(self.turtle1_pose [0],self.turtle1_pose [1])<0.5 and self.angle(self.turtle1_pose [0],self.turtle1_pose [1])<0.1:
                
                self.t()
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

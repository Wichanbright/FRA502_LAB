#!/usr/bin/python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Point
from turtlesim.msg import Pose
from turtlesim_plus_interfaces.srv import GivePosition
from std_srvs.srv import Empty
from std_msgs.msg import Bool
from std_msgs.msg import Int64
from geometry_msgs.msg import PoseStamped
import math
import numpy as np
class eater(Node):
    def __init__(self):
        super().__init__('eater')
        self.state_turtle2 = self.create_publisher(Bool,"state",10)
        self.cmd_vel_pub = self.create_publisher(Twist,'/turtle1/cmd_vel',10)
        self.create_subscription(PoseStamped,'/goal_pose',self.pose_go,10)
        self.create_subscription(Bool,'/state_eat',self.eat_callback,10)
        self.create_subscription(Pose,'/turtle1/pose',self.pose_callback,10)
        self.create_subscription(Point,'/mouse_position',self.mouse_callback,10)
        self.spawn_pizza_client =self.create_client(GivePosition,'spawn_pizza')
        self.create_subscription(Int64,'/turtle1/pizza_count',self.count_callback,10)
        self.eat_pizza_client =self.create_client(Empty,'/turtle1/eat')
        self.taget_x=[0,0,0,0,0]
        self.taget_y=[0,0,0,0,0]
        self.pieces=0
        self.round=0
        self.state=0
        self.last=0
        self.count=0
        self.create_timer(0.01,self.timer_callback)
        self.robot_pose = np.array([0.0 ,0.0 ,0.0])
        self.mouse = np.array([0.0 ,0.0 ])
        self.go = np.array([0.0 ,0.0 ])
        self.state_turtle(False)
        self.state_eat=False
    def count_callback(self,msg):
        self.count=msg.data
       
    def eat_callback(self,msg):
        self.state_eat=msg.data
    def state_turtle(self,s):
        sta=Bool()
        sta.data=s
        self.state_turtle2.publish(sta)

    def sqawn_pizza(self,x,y):
        position= GivePosition.Request()
        position.x=x
        position.y=y
        self.spawn_pizza_client.call_async(position)
    def eat(self):
        eater=Empty.Request()  
        self.eat_pizza_client.call_async(eater)  
    def pose_callback(self ,msg):
        self.robot_pose[0]=round(msg.x, 2)
        self.robot_pose[1]=round(msg.y, 2)
        self.robot_pose[2]=round(msg.theta, 2)
        # print(self.robot_pose)
    def pose_go(self,msg):
        
        self.go[0]=msg.pose.position.x+5.440000057220459
        self.go[1]=msg.pose.position.y+5.440000057220459
        print(f'{self.go[0]}  {self.go[1]}')
        if self.go[0]>0 and self.go[1]>0 and self.go[0]<=10.88 and self.go[1]<=10.88:
            self.state=1
            if self.pieces<5:
                self.taget_x[self.pieces]=round(self.go[0], 2)
                self.taget_y[self.pieces]=round(self.go[1], 2)
                self.sqawn_pizza(self.go[0],self.go[1])
                self.pieces+=1
            else :
                self.point_x=round(self.go[0], 2)
                self.point_y=round(self.go[1], 2)
    def mouse_callback(self ,msg):
        self.state=1
        self.mouse[0]=msg.x
        self.mouse[1]=msg.y
        if self.pieces<5:
            self.taget_x[self.pieces]=round(msg.x, 2)
            self.taget_y[self.pieces]=round(msg.y, 2)
            self.sqawn_pizza(msg.x,msg.y)
            self.pieces+=1
        else :
            self.point_x=round(msg.x, 2)
            self.point_y=round(msg.y, 2)
        # print(self.taget_x)
        # print(self.taget_y)
    def angle(self,x,y):
        Dx=x-self.robot_pose[0]
        Dy=y-self.robot_pose[1]
        e=math.atan2(Dy,Dx)
        degree=e-self.robot_pose[2]
        if e>=(math.pi*0.5) and (e<=math.pi) and self.robot_pose[2]<=-(math.pi*0.5) and (self.robot_pose[2]>=-math.pi)  :
            degree=-(math.pi*2)-(self.robot_pose[2]-e)
        elif self.robot_pose[2]>=(math.pi*0.5) and (self.robot_pose[2]<=math.pi) and e<=-(math.pi*0.5) and (e>=-math.pi) :
            degree=(math.pi*2)-(self.robot_pose[2]-e)  
        return degree
    def Distant(self,x,y):
        Dx=x-self.robot_pose[0]
        Dy=y-self.robot_pose[1]
        return ((Dx**2)+(Dy**2))**(1/2)
    def cmdvel(self, v, w):
        msg=Twist()
        msg.linear.x =v
        msg.angular.z=w
        self.cmd_vel_pub.publish(msg)
    def go_eat(self):
        w=self.angle(self.taget_x[self.round],self.taget_y[self.round])*8
        V=self.Distant(self.taget_x[self.round],self.taget_y[self.round])*3
        self.cmdvel(V,w)
        if self.Distant( self.taget_x[self.round],self.taget_y[self.round]) < 1 and self.angle(self.taget_x[self.round],self.taget_y[self.round]) <0.01:
            self.state=0 
            self.eat()
            print("eat!!!")
            self.round+=1
    def runrun(self):
        w=self.angle(self.mouse[0],self.mouse[1])*8
        V=self.Distant(self.mouse[0],self.mouse[1])*3
        self.cmdvel(V,w)
        if self.Distant(self.mouse[0],self.mouse[1]) < 1 and self.angle(self.mouse[0],self.mouse[1]) <0.01:
            self.state=0 
            print("RUN!!!")
    def timer_callback(self):
        if self.state ==1 :
            if self.round<5:
                self.go_eat()
                if self.pieces!=self.round:self.state=1
                self.state_turtle(False)
            else:
                self.state_turtle(True)
                self.runrun()
        else :
            self.cmdvel(0.0,0.0)
        
        
            
def main(args=None):
    rclpy.init(args=args)
    node = eater()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()

#!/usr/bin/python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from std_srvs.srv import Empty
from turtlesim.srv import Spawn
from turtlesim.srv import Kill
from controller_interfaces.srv import SetParam
from std_msgs.msg import Bool
import time
import math
import yaml

import sys

class kill(Node):
    def __init__(self):
        super().__init__('kill_node')
        #variables
        self.name_space=self.get_namespace()
        self.rate = 1000
        self.state=1
        self.read=0
        self.posezeno=[0,0,0]
        self.posefoxy=[0,0,0]
        self.kpzeno=[1.0,5.0]
        self.round=[0]
        self.flag_shut = False
        #subscriber
        self.create_subscription(Bool,'/status_kill',self.status,10)
        self.create_subscription(Pose,self.name_space+'/Foxy/pose',self.pose_foxy,10)
        self.create_subscription(Pose,self.name_space+'/zeno/pose',self.pose_zeno,10)
        self.state=1
        #publisher
        self.shut_pub = self.create_publisher(Bool,'/shutdown',10)
        self.cmd_vel_zeno = self.create_publisher(Twist,self.name_space+'/zeno/cmd_vel',10)
        #service
        self.gainfoxy =self.create_service(SetParam,self.name_space+'/set_gainzeno',self.gain_zeno)
        
        #client
        self.eat_pizza_client =self.create_client(Empty,self.name_space+'/zeno/eat')
        self.spawnturtle =self.create_client(Spawn,self.name_space+'/spawn_turtle')
        self.delturtle =self.create_client(Kill,self.name_space+'/remove_turtle')
        #timer
        
        self.create_timer(0.1/self.rate,self.timer_callback)
    #functions subscriber
    def pose_zeno(self,msg):
        self.posezeno[0]=msg.x
        self.posezeno[1]=msg.y
        self.posezeno[2]=msg.theta
    def pose_foxy(self,msg):
        self.posefoxy[0]=msg.x
        self.posefoxy[1]=msg.y
        self.posefoxy[2]=msg.theta
       
    def status(self,msg):
        self.status_kill=msg.data
        if self.status_kill==True:
            self.read=1
        
        
    #functions publisher
    def foxy_vel(self,vel,omega) :
        msg = Twist()
        msg.linear.x = vel
        msg.angular.z = omega
        self.cmd_vel_zeno.publish(msg)
    def shut_down(self):
        msg = Bool()
        msg.data = True
        self.flag_shut = True
        self.shut_pub.publish(msg)
    #functions service
    def gain_zeno(self,request:SetParam.Request, response:SetParam.Response):
        self.kpzeno[0] = request.kp_linear.data
        self.kpzeno[1] = request.kp_angular.data
        return response
    #functions client
    def kill_turtle(self,n):
        self.state = 5
        d=Kill.Request()  
        d.name=n
        self.delturtle.call_async(d)
    def spawn(self,x,y,n):
        position= Spawn.Request()
        position.x=float(x)
        position.y=float(y)
        position.theta=0.0
        position.name=n
        self.spawnturtle.call_async(position)
    def eat(self):
        eater=Empty.Request()  
        self.eat_pizza_client.call_async(eater) 
    #functions main
    def angle(self,x,y,xr,yr,wr):
        Dx=x-xr
        Dy=y-yr
        e=math.atan2(Dy,Dx)
        degree=e-wr
        if e>=(math.pi*0.5) and (e<=math.pi) and wr<=-(math.pi*0.5) and (wr>=-math.pi)  :
            degree=-(math.pi*2)-(wr-e)
        elif wr>=(math.pi*0.5) and (wr<=math.pi) and e<=-(math.pi*0.5) and (e>=-math.pi) :
            degree=(math.pi*2)-(wr-e)  
        distant=((Dx**2)+(Dy**2))**(1/2)
        return degree ,distant
    def zenogo(self,x,y,T):
        A1,D1=self.angle(x,y,self.posezeno[0],self.posezeno[1],self.posezeno[2])
        if D1>T or abs(A1)>0.01 :
           if D1< T: D1=0
           self.foxy_vel(D1*self.kpzeno[0],A1*self.kpzeno[1])
           status = False
        else: 
           self.foxy_vel(0.0,0.0)
           status = True
        return status
    def load_path(self, path_index: int):
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
    def state1(self):
        print("state1")
        if self.read==1:
            self.path=self.load_path(1)+self.load_path(2)+self.load_path(3)+self.load_path(4) 
            self.state=2
    def state2(self):
        self.spawn(self.posefoxy[0],self.posefoxy[1],'zeno')
        print("state2")
        self.kill_turtle('Foxy')
        self.kill_turtle('Noetic')
        self.kill_turtle('Humble')
        self.kill_turtle('Iron')
        self.state=3
    def state3(self):
        tark=0
        if len(self.path)>self.round[0]:
            if self.zenogo(self.path[self.round[0]][0],self.path[self.round[0]][1] ,0.1)==True :
                self.get_logger().info(f"numear_pazza : {self.round[0]+1}")
                self.foxy_vel(0.0,0.0)
                self.eat()
                self.round[0]+=1
            tark+=1
        if tark ==0 :
            print("next")
            self.state=4
            
        
    def state4(self):
        if not hasattr(self, 'start_time'):   # เก็บเวลาเริ่มครั้งแรก
            self.start_time = time.monotonic()

        # ถ้าเวลาผ่านไปเกิน 1 วินาที
        if time.monotonic() - self.start_time >= 1.0:
            self.kill_turtle('zeno')
            # rclpy.shutdown()
            del self.start_time 
    #function timer
    def timer_callback(self):
        match self.state:
            case 1 :
                self.state1()
            case 2 :
                self.state2()
            case 3 :
                self.state3()
            case 4 :
                self.state4()
            case 5 :
                self.shut_down()
                self.get_logger().info(f"shutdown Kill_Copy: {self.flag_shut}")
        if self.flag_shut :
            self.destroy_node()
            rclpy.shutdown()
       
        
       
        

def main(args=None):
    rclpy.init(args=args)
    node = kill()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()

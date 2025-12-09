#!/usr/bin/python3


import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from std_srvs.srv import Empty
from geometry_msgs.msg import Point
from controller_interfaces.srv import SetParam
from turtlesim_plus_interfaces.srv import GivePosition
from std_msgs.msg import Bool
import math
import yaml
import time as t
class turtle_copy(Node):
    def __init__(self):
        super().__init__('turtle_copy')
        #variable
        self.name_space=self.get_namespace()
    

        self.rate=1000
        self.state=0
        self.read=False
        self.make=False
        self.status_spawn=0
        self.mp=[0.0,0.0]
        self.round=[0,0,0,0]
        self.posefoxy=[0,0,0]
        self.posenoetic=[0,0,0]
        self.posehumber=[0,0,0]
        self.poseiron=[0,0,0]
        self.kpfoxy=[5,10]
        self.kpnoetic=[5,10]
        self.kphumber=[5,10]
        self.kpiron=[5,10]
        self.path1=[[1.0,2.0],[5.0,2.5]]
        self.path2=[[5.0,2.0,10.0],[5.0,9.0,7.0]]
        self.path3=[[8.0,8.0],[5.0,2.5]]
        self.path4=[[3.0,2.0],[5.0,8.0]]
        self.shut = False
        #publisher
        self.dejavu = self.create_publisher(Pose,'/Dejavu/pose',10)
        self.cmd_vel_foxy = self.create_publisher(Twist,self.name_space+'/Foxy/cmd_vel',10)
        self.cmd_vel_noetic = self.create_publisher(Twist,self.name_space+'/Noetic/cmd_vel',10)
        self.cmd_vel_humber = self.create_publisher(Twist,self.name_space+'/Humble/cmd_vel',10)
        self.cmd_vel_iron = self.create_publisher(Twist,self.name_space+'/Iron/cmd_vel',10)
        self.status_make = self.create_publisher(Bool,'/status_makeup',10)
        #subscriber
        self.create_subscription(Bool,'/status_spawn',self.status_callback,10)
        self.create_subscription(Point,self.name_space+'/mouse_position',self.mouse_point,10)
        self.create_subscription(Pose,self.name_space+'/Foxy/pose',self.pose_foxy,10)
        self.create_subscription(Pose,self.name_space+'/Noetic/pose',self.pose_noetic,10)
        self.create_subscription(Pose,self.name_space+'/Humble/pose',self.pose_humber,10)
        self.create_subscription(Pose,self.name_space+'/Iron/pose',self.pose_iron,10)
        self.create_subscription(Bool,'/shutdown',self.shut_down,10)
        #service
        self.gainfoxy =self.create_service(SetParam,self.name_space+'/set_gainfoxy',self.gain_foxy)
        self.gainnoetic =self.create_service(SetParam,self.name_space+'/set_gainnoetic',self.gain_noetic)
        self.gainhumber =self.create_service(SetParam,self.name_space+'/set_gainhumber',self.gain_humber)
        self.gainiron =self.create_service(SetParam,self.name_space+'/set_gainiron',self.gain_iron)
        #client
        self.spawn_pizza_client =self.create_client(GivePosition,self.name_space+'/spawn_pizza')
        self.eat_pizza_client =self.create_client(Empty,self.name_space+'/eat')
        #timer
        self.create_timer(0.1/self.rate,self.timer_callback)
    #function publisher
    def status_makeup(self,status):
        msg=Bool()
        msg.data=status
        self.status_make.publish(msg)
    def foxy_vel(self,vel,omega) :
        msg = Twist()
        msg.linear.x = vel
        msg.angular.z = omega
        self.cmd_vel_foxy.publish(msg)
    def noetic_vel(self,vel,omega) :
        msg = Twist()
        msg.linear.x = vel
        msg.angular.z = omega
        self.cmd_vel_noetic.publish(msg)
    def humber_vel(self,vel,omega) :
        msg = Twist()
        msg.linear.x = vel
        msg.angular.z = omega
        self.cmd_vel_humber.publish(msg)
    def iron_vel(self,vel,omega) :
        msg = Twist()
        msg.linear.x = vel
        msg.angular.z = omega
        self.cmd_vel_iron.publish(msg)

    #function subscriber
    def shut_down(self,msg):
        if msg.data == True :
            self.shut = True
            self.get_logger().info(f"shutdown Copy: {msg.data}")
            self.destroy_node()
            rclpy.shutdown()
    def status_callback(self,msg):
        if msg.data==True:
            self.status_spawn=1
    def mouse_point(self,msg):
        if self.read==True:
            self.mp[0]=msg.x
            self.mp[1]=msg.y
            self.read=False
    def pose_foxy(self,msg):
        self.posefoxy[0]=msg.x
        self.posefoxy[1]=msg.y
        self.posefoxy[2]=msg.theta
        msg = Pose()
        msg.x = self.posefoxy[0]
        msg.y = self.posefoxy[1]
        msg.theta = self.posefoxy[2]
        self.dejavu.publish(msg)
    def pose_noetic(self,msg):
        self.posenoetic[0]=msg.x
        self.posenoetic[1]=msg.y
        self.posenoetic[2]=msg.theta
    def pose_humber(self,msg):
        self.posehumber[0]=msg.x
        self.posehumber[1]=msg.y
        self.posehumber[2]=msg.theta
    def pose_iron(self,msg):
        self.poseiron[0]=msg.x
        self.poseiron[1]=msg.y
        self.poseiron[2]=msg.theta
    #function service
    def gain_foxy(self,request:SetParam.Request, response:SetParam.Response):
        self.kpfoxy[0] = request.kp_linear.data
        self.kpfoxy[1] = request.kp_angular.data
        return response
    def gain_noetic(self,request:SetParam.Request, response:SetParam.Response):
        self.kpnoetic[0] = request.kp_linear.data
        self.kpnoetic[1] = request.kp_angular.data
        return response
    def gain_humber(self,request:SetParam.Request, response:SetParam.Response):
        self.kphumber[0] = request.kp_linear.data
        self.kphumber[1] = request.kp_angular.data
        return response
    def gain_iron(self,request:SetParam.Request, response:SetParam.Response):
        self.kpiron[0] = request.kp_linear.data
        self.kpiron[1] = request.kp_angular.data
        return response
    #function client
    def eat(self):
        eater=Empty.Request()  
        self.eat_pizza_client.call_async(eater)  
    def sqawn_pizza(self,x,y):
        position= GivePosition.Request()
        position.x=x
        position.y=y
        self.spawn_pizza_client.call_async(position)
    #function main
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
    def foxygo(self,x,y,T):
        A1,D1=self.angle(x,y,self.posefoxy[0],self.posefoxy[1],self.posefoxy[2])
        if D1>T:
           self.foxy_vel(D1*self.kpfoxy[0],A1*self.kpfoxy[1])
           status = False
        else: 
           self.foxy_vel(0.0,0.0)
           status = True
        return status
    def noeticgo(self,x,y,T):
        A2,D2=self.angle(x,y,self.posenoetic[0],self.posenoetic[1],self.posenoetic[2])
        if D2>T:
           self.noetic_vel(D2*self.kpnoetic[0],A2*self.kpnoetic[1])
           status = False
        else: 
           self.noetic_vel(0.0,0.0)
           status = True
        return status
    def humbergo(self,x,y,T):           
        A3,D3=self.angle(x,y,self.posehumber[0],self.posehumber[1],self.posehumber[2])
        if D3>T:
           self.humber_vel(D3*self.kphumber[0],A3*self.kphumber[1])
           status = False
        else: 
           self.humber_vel(0.0,0.0)
           status = True
        return status   
    def irongo(self,x,y,T):
        A4,D4=self.angle(x,y,self.poseiron[0],self.poseiron[1],self.poseiron[2])
        if D4>T:
           self.iron_vel(D4*self.kpiron[0],A4*self.kpiron[1])
           status = False
        else: 
           self.iron_vel(0.0,0.0)
           status = True
        return status
    def state0(self):
        if  self.status_spawn== 1: 
            self.path1=self.load_path(1)
            self.path2=self.load_path(2)
            self.path3=self.load_path(3)
            self.path4=self.load_path(4)
            self.state=1
            
    def state1(self):
        tark=0
        if len(self.path1)>self.round[0]:
            if self.foxygo(self.path1[self.round[0]][0],self.path1[self.round[0]][1] ,0.5)==True :
                print("ok foxy")
                self.sqawn_pizza(self.path1[self.round[0]][0],self.path1[self.round[0]][1])
                self.round[0]+=1
            tark+=1
        if len(self.path2)>self.round[1]:
            if self.noeticgo(self.path2[self.round[1]][0],self.path2[self.round[1]][1] ,0.5)==True :
                print("ok noetic")
                self.sqawn_pizza(self.path2[self.round[1]][0],self.path2[self.round[1]][1])
                self.round[1]+=1
            tark+=1
        if len(self.path3)>self.round[2]:
            if self.humbergo(self.path3[self.round[2]][0],self.path3[self.round[2]][1] ,0.5)==True :
                print("ok humber")
                self.sqawn_pizza(self.path3[self.round[2]][0],self.path3[self.round[2]][1])
                self.round[2]+=1
            tark+=1
        if len(self.path4)>self.round[3]:       
            if self.irongo(self.path4[self.round[3]][0],self.path4[self.round[3]][1] ,0.5)==True :
                print("ok iron")
                self.sqawn_pizza(self.path4[self.round[3]][0],self.path4[self.round[3]][1])
                self.round[3]+=1
            tark+=1         
        if tark ==0 :
            print("next state")
            self.state=2
            self.read=True
    def state2(self):
        if self.read==False:
            t1= self.foxygo(self.mp[0],self.mp[1] ,0.1) 
            t2= self.noeticgo(self.mp[0],self.mp[1] ,0.1)
            t3= self.humbergo(self.mp[0],self.mp[1] ,0.1)
            t4= self.irongo(self.mp[0],self.mp[1] ,0.1)
            self.make= t1 and t2 and t3 and t4
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
        
    #function timer
    def timer_callback(self):
        if self.shut == False:
            match self.state :
                case 0 :
                    self.state0()
                case 1 :
                    self.state1()
                case 2 :
                    self.state2()
            self.status_makeup(self.make)
        

def main(args=None):
    rclpy.init(args=args)
    node = turtle_copy()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()

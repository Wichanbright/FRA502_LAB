#!/usr/bin/python3

from lab2.dummy_module import dummy_function, dummy_var
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist,Point,TransformStamped
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster
from turtlesim.msg import Pose
import numpy as np
from tf_transformations import quaternion_from_euler

class DummyNode(Node):
    def __init__(self):
        super().__init__('turtlesim_pose')
        self.create_subscription(Pose,'/turtle1/pose',self.pose1_callback,10)
        self.create_subscription(Pose,'/turtle2/pose',self.pose2_callback,10)
        self.odom1_publisher=self.create_publisher(Odometry,'/odom1',10)
        self.odom2_publisher=self.create_publisher(Odometry,'/odom2',10)
        self.tf_broadcaster = TransformBroadcaster(self)
        # var
        self.turtle1_pose = np.array([0.0 ,0.0 ,0.0])
        self.turtle2_pose = np.array([0.0 ,0.0 ,0.0])
    def pose1_callback(self ,msg):
        self.turtle1_pose[0]=round(msg.x, 2)
        self.turtle1_pose[1]=round(msg.y, 2)
        self.turtle1_pose[2]=round(msg.theta, 2)
        odom_msg =Odometry()
        odom_msg.header.stamp = self.get_clock().now().to_msg()
        odom_msg.header.frame_id="odom"
        odom_msg.child_frame_id="robot"
        odom_msg.pose.pose.position.x = self.turtle1_pose[0]-5.440000057220459
        odom_msg.pose.pose.position.y = self.turtle1_pose[1]-5.440000057220459
        q=quaternion_from_euler(0,0,self.turtle1_pose[2])
        odom_msg.pose.pose.orientation.x=q[0]
        odom_msg.pose.pose.orientation.y=q[1]
        odom_msg.pose.pose.orientation.z=q[2]
        odom_msg.pose.pose.orientation.w=q[3]
        self.odom1_publisher.publish(odom_msg)

        t= TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id="odom1"
        t.child_frame_id="turtle1"
        t.transform.translation.x=self.turtle1_pose[0]-5.440000057220459
        t.transform.translation.y=self.turtle1_pose[1]-5.440000057220459

        t.transform.rotation.x =q[0]
        t.transform.rotation.y =q[1]
        t.transform.rotation.z =q[2]
        t.transform.rotation.w =q[3]
        self.tf_broadcaster.sendTransform(t)
    def pose2_callback(self ,msg):
        self.turtle2_pose[0]=round(msg.x, 2)
        self.turtle2_pose[1]=round(msg.y, 2)
        self.turtle2_pose[2]=round(msg.theta, 2)
        odom_msg =Odometry()
        odom_msg.header.stamp = self.get_clock().now().to_msg()
        odom_msg.header.frame_id="odom"
        odom_msg.child_frame_id="robot"
        odom_msg.pose.pose.position.x = self.turtle2_pose[0]-5.440000057220459
        odom_msg.pose.pose.position.y = self.turtle2_pose[1]-5.440000057220459
        q=quaternion_from_euler(0,0,self.turtle2_pose[2])
        odom_msg.pose.pose.orientation.x=q[0]
        odom_msg.pose.pose.orientation.y=q[1]
        odom_msg.pose.pose.orientation.z=q[2]
        odom_msg.pose.pose.orientation.w=q[3]
        self.odom2_publisher.publish(odom_msg)

        t= TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id="odom2"
        t.child_frame_id="turtle2"
        t.transform.translation.x=self.turtle2_pose[0]-5.440000057220459
        t.transform.translation.y=self.turtle2_pose[1]-5.440000057220459

        t.transform.rotation.x =q[0]
        t.transform.rotation.y =q[1]
        t.transform.rotation.z =q[2]
        t.transform.rotation.w =q[3]
        self.tf_broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = DummyNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()

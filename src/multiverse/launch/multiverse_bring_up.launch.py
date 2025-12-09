from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
import numpy as np
angle=np.pi/4
name_universe=['xxx1','xxx2']
turtle_universe1=['teleop']
turtle_universe2=['Foxy','Noetic','Humble','Iron']
def generate_launch_description():
    launch = LaunchDescription()
    for name in name_universe:
        node1=Node(
            package='turtlesim_plus',
            namespace=name,
            executable='turtlesim_plus_node.py'
        )
        launch.add_action(node1)
    for name in  name_universe :
        turtle_del = ExecuteProcess(
            cmd=['ros2', 'service', 'call',
                '/'+name+'/remove_turtle', 'turtlesim/srv/Kill',
                "{name: 'turtle1'}"],
            output='screen'
        )
        launch.add_action(turtle_del)
    for name in turtle_universe1 :
        turtle1 = ExecuteProcess(
            cmd=['ros2', 'service', 'call',
                '/'+name_universe[0]+'/spawn_turtle', 'turtlesim/srv/Spawn',
                f"{{x: -5.0, y: -5.0, theta: 0.78, name: '{name}'}}"],
            output='screen'
        )
        launch.add_action(turtle1)
    for name in turtle_universe2 :
        turtle2 = ExecuteProcess(
            cmd=['ros2', 'service', 'call',
                '/'+name_universe[1]+'/spawn_turtle', 'turtlesim/srv/Spawn',
                f"{{x: -5.0, y: -5.0, theta: 0.78, name: '{name}'}}"],
            output='screen'
        )
        launch.add_action(turtle2)
    node2=Node(
            package='universe_1',
            namespace=name_universe[0],
            executable='controller_node.py',
            name='controller_node'

        )
    launch.add_action(node2)
    node3=Node(
            package='universe_2',
            namespace=name_universe[1],
            executable='turtle_copy_node.py',

        )
    launch.add_action(node3)
    node4=Node(
            package='universe_1',
            namespace=name_universe[0],
            executable='eraser_node.py',

        )
    launch.add_action(node4)
    node5=Node(
            package='universe_2',
            namespace=name_universe[1],
            executable='kill_copy_node.py',

        )
    launch.add_action(node5)
    return launch
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node


def generate_launch_description():
    package_share = get_package_share_directory('cell_bringup')
    world_path = os.path.join(package_share, 'worlds', 'factory_world.sdf')

    return LaunchDescription([
        ExecuteProcess(
            cmd=['gz', 'sim', '-r', world_path],
            output='screen'
        ),

        Node(
            package='cell_bringup',
            executable='cell_state_simulator',
            name='cell_state_simulator',
            output='screen'
        ),

        Node(
            package='cell_bringup',
            executable='delay_detector',
            name='delay_detector',
            output='screen'
        ),

        Node(
            package='cell_bringup',
            executable='adaptive_reallocator',
            name='adaptive_reallocator',
            output='screen'
        ),

        Node(
            package='cell_bringup',
            executable='resilience_score',
            name='resilience_score',
            output='screen'
        ),

        Node(
            package='cell_bringup',
            executable='experiment_logger',
            name='experiment_logger',
            output='screen'
        ),

        Node(
            package='cell_bringup',
            executable='continuous_workpiece_animator',
            name='continuous_workpiece_animator',
            output='screen'
        ),
    ])

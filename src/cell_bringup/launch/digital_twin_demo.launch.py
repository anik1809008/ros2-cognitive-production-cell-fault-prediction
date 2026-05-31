from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
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
    ])

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
            executable='rl_reallocator',
            name='rl_reallocator',
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
        Node(
             package='cell_bringup',
             executable='fault_predictor',
             name='fault_predictor',
             output='screen'
        ),


    ])

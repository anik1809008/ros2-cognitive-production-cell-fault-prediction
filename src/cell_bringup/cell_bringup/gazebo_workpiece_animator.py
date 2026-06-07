import json
import subprocess
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class GazeboWorkpieceAnimator(Node):
    def __init__(self):
        super().__init__('gazebo_workpiece_animator')

        self.world_name = 'resilience_aware_digital_twin_world'
        self.last_state = None

        self.subscription = self.create_subscription(
            String,
            'reallocation_decision',
            self.animate_from_decision,
            10
        )

        self.get_logger().info('Gazebo Workpiece Animator started')
        self.get_logger().info('Listening to /reallocation_decision')

    def set_pose(self, model_name, x, y, z):
        service_name = f'/world/{self.world_name}/set_pose'

        request = (
            f'name: "{model_name}", '
            f'position: {{x: {x}, y: {y}, z: {z}}}, '
            f'orientation: {{x: 0, y: 0, z: 0, w: 1}}'
        )

        cmd = [
            'gz', 'service',
            '-s', service_name,
            '--reqtype', 'gz.msgs.Pose',
            '--reptype', 'gz.msgs.Boolean',
            '--timeout', '1000',
            '--req', request
        ]

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def move_workpiece_path(self, path):
        for x, y, z in path:
            self.set_pose('adaptive_workpiece', x, y, z)
            time.sleep(0.3)

    def hide_markers(self):
        self.set_pose('delay_marker_red', 0, 0, -5)
        self.set_pose('helper_marker_yellow', 0, 0, -5)

    def animate_from_decision(self, msg):
        try:
            data = json.loads(msg.data)

            delayed_cell = data.get('delayed_cell')
            target_cell = data.get('target_cell')
            reallocation_required = data.get('reallocation_required')

            current_state = f'{delayed_cell}_{target_cell}_{reallocation_required}'

            if current_state == self.last_state:
                return

            self.last_state = current_state

            if not reallocation_required:
                self.get_logger().info('Normal operation: hiding delay/helper markers')
                self.hide_markers()
                self.set_pose('adaptive_workpiece', -8, 0, 1.0)
                return

            if delayed_cell == 'cell_1' and target_cell == 'cell_2':
                self.get_logger().warn('Animating recovery: Cell 1 delayed, Cell 2 assisting')

                # Red marker above Cell 1, yellow marker above Cell 2
                self.set_pose('delay_marker_red', -2, 2.5, 2.0)
                self.set_pose('helper_marker_yellow', -2, -2.5, 2.0)

                path = [
                    (-2, 2.5, 1.4),
                    (-2, 1.5, 1.4),
                    (-2, 0.5, 1.4),
                    (-2, -0.5, 1.4),
                    (-2, -1.5, 1.4),
                    (-2, -2.5, 1.4),
                    (2, 0, 1.2),
                    (7, 0, 1.2),
                ]
                self.move_workpiece_path(path)

            elif delayed_cell == 'cell_2' and target_cell == 'cell_1':
                self.get_logger().warn('Animating recovery: Cell 2 delayed, Cell 1 assisting')

                # Red marker above Cell 2, yellow marker above Cell 1
                self.set_pose('delay_marker_red', -2, -2.5, 2.0)
                self.set_pose('helper_marker_yellow', -2, 2.5, 2.0)

                path = [
                    (-2, -2.5, 1.4),
                    (-2, -1.5, 1.4),
                    (-2, -0.5, 1.4),
                    (-2, 0.5, 1.4),
                    (-2, 1.5, 1.4),
                    (-2, 2.5, 1.4),
                    (2, 0, 1.2),
                    (7, 0, 1.2),
                ]
                self.move_workpiece_path(path)

        except Exception as e:
            self.get_logger().error(f'Animation error: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = GazeboWorkpieceAnimator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

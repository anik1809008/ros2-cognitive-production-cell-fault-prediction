import json
import subprocess

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ContinuousWorkpieceAnimator(Node):
    def __init__(self):
        super().__init__('continuous_workpiece_animator')

        self.world_name = 'resilience_aware_digital_twin_world'
        self.mode = 'normal'
        self.step = 0

        self.boxes = [
            'flow_box_1',
            'flow_box_2',
            'flow_box_3',
            'flow_box_4'
        ]

        self.cell1_route = self.make_path([
            (-8, 0, 1.2),
            (-5, 0, 1.2),
            (-2, 2.5, 1.4),
            (2, 0, 1.2),
            (7, 0, 1.2),
        ])

        self.cell2_route = self.make_path([
            (-8, 0, 1.2),
            (-5, 0, 1.2),
            (-2, -2.5, 1.4),
            (2, 0, 1.2),
            (7, 0, 1.2),
        ])

        self.subscription = self.create_subscription(
            String,
            'reallocation_decision',
            self.update_mode,
            10
        )

        self.timer = self.create_timer(0.35, self.animate_boxes)

        self.get_logger().info('Continuous Workpiece Animator started')
        self.get_logger().info('Normal mode: boxes go equally to Cell 1 and Cell 2')
        self.get_logger().info('Delay mode: extra boxes shift to the healthy cell')

    def make_path(self, points, parts=6):
        path = []

        for i in range(len(points) - 1):
            x1, y1, z1 = points[i]
            x2, y2, z2 = points[i + 1]

            for j in range(parts):
                t = j / parts
                x = x1 + (x2 - x1) * t
                y = y1 + (y2 - y1) * t
                z = z1 + (z2 - z1) * t
                path.append((round(x, 2), round(y, 2), round(z, 2)))

        return path

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
            '--timeout', '500',
            '--req', request
        ]

        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def update_mode(self, msg):
        try:
            data = json.loads(msg.data)

            if not data.get('reallocation_required'):
                self.mode = 'normal'
                self.hide_markers()
                return

            delayed_cell = data.get('delayed_cell')

            if delayed_cell == 'cell_1':
                self.mode = 'cell_1_delayed'
                self.get_logger().warn(
                    'Cell 1 delayed: extra boxes shifting to Cell 2'
                )

                self.set_pose('delay_marker_red', -2, 2.5, 2.0)
                self.set_pose('helper_marker_yellow', -2, -2.5, 2.0)

            elif delayed_cell == 'cell_2':
                self.mode = 'cell_2_delayed'
                self.get_logger().warn(
                    'Cell 2 delayed: extra boxes shifting to Cell 1'
                )

                self.set_pose('delay_marker_red', -2, -2.5, 2.0)
                self.set_pose('helper_marker_yellow', -2, 2.5, 2.0)

        except Exception as e:
            self.get_logger().error(f'Mode update error: {e}')

    def hide_markers(self):
        self.set_pose('delay_marker_red', 0, 0, -5)
        self.set_pose('helper_marker_yellow', 0, 0, -5)

    def choose_route(self, box_index):
        if self.mode == 'normal':
            # Normal: 2 boxes go to Cell 1, 2 boxes go to Cell 2
            if box_index in [0, 2]:
                return self.cell1_route
            return self.cell2_route

        if self.mode == 'cell_1_delayed':
            # Cell 1 delayed: only 1 box to Cell 1, 3 boxes to Cell 2
            if box_index == 0:
                return self.cell1_route
            return self.cell2_route

        if self.mode == 'cell_2_delayed':
            # Cell 2 delayed: only 1 box to Cell 2, 3 boxes to Cell 1
            if box_index == 0:
                return self.cell2_route
            return self.cell1_route

        return self.cell1_route

    def animate_boxes(self):
        self.step += 1

        for i, box in enumerate(self.boxes):
            route = self.choose_route(i)
            index = (self.step + i * 6) % len(route)

            x, y, z = route[index]
            self.set_pose(box, x, y, z)


def main(args=None):
    rclpy.init(args=args)
    node = ContinuousWorkpieceAnimator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

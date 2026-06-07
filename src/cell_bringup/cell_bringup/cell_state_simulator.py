import json
import random
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class CellStateSimulator(Node):
    def __init__(self):
        super().__init__('cell_state_simulator')

        self.publisher_ = self.create_publisher(String, 'cell_state', 10)
        self.timer = self.create_timer(1.0, self.publish_cell_state)

        self.start_time = time.time()

        self.get_logger().info('Cell State Simulator started')
        self.get_logger().info('Publishing Cell 1 and Cell 2 status on /cell_state')

    def publish_cell_state(self):
        elapsed = int(time.time() - self.start_time)
        phase = elapsed % 40
        # Normal condition
        cell_1_task_time = round(random.uniform(3.0, 4.5), 2)
        cell_2_task_time = round(random.uniform(3.0, 4.5), 2)

        cell_1_workload = random.randint(45, 60)
        cell_2_workload = random.randint(45, 60)

        # Simulated delay scenario for Cell 1
        if 8 <= phase <= 16:
            cell_1_task_time = round(random.uniform(6.0, 8.5), 2)
            cell_1_workload = random.randint(75, 90)

        # Simulated delay scenario for Cell 2
        if 22 <= phase <= 30:
            cell_2_task_time = round(random.uniform(6.0, 8.5), 2)
            cell_2_workload = random.randint(75, 90)

        data = {
            "timestamp": elapsed,
            "cell_1": {
                "status": "working",
                "task_time": cell_1_task_time,
                "workload": cell_1_workload
            },
            "cell_2": {
                "status": "working",
                "task_time": cell_2_task_time,
                "workload": cell_2_workload
            }
        }

        msg = String()
        msg.data = json.dumps(data)
        self.publisher_.publish(msg)

        self.get_logger().info(f'Published cell state: {msg.data}')


def main(args=None):
    rclpy.init(args=args)
    node = CellStateSimulator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

import csv
import json
import os

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ExperimentLogger(Node):
    def __init__(self):
        super().__init__('experiment_logger')

        self.results_dir = os.path.expanduser(
            '~/ros2-cognitive-production-cell-fault-prediction/results'
        )
        os.makedirs(self.results_dir, exist_ok=True)

        self.csv_path = os.path.join(self.results_dir, 'resilience_results.csv')

        self.subscription = self.create_subscription(
            String,
            'resilience_score',
            self.log_result,
            10
        )

        self.create_csv_if_needed()

        self.get_logger().info('Experiment Logger started')
        self.get_logger().info(f'Logging results to {self.csv_path}')

    def create_csv_if_needed(self):
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'timestamp',
                    'event',
                    'delayed_cell',
                    'target_cell',
                    'workload_shift_percent',
                    'recovery_time',
                    'resilience_score',
                    'system_status'
                ])

    def log_result(self, msg):
        try:
            data = json.loads(msg.data)

            with open(self.csv_path, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    data.get('timestamp'),
                    data.get('event'),
                    data.get('delayed_cell', 'none'),
                    data.get('target_cell', 'none'),
                    data.get('workload_shift_percent', 0),
                    data.get('recovery_time'),
                    data.get('digital_twin_resilience_score'),
                    data.get('system_status')
                ])

            self.get_logger().info('Result logged successfully')

        except Exception as e:
            self.get_logger().error(f'Failed to log result: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = ExperimentLogger()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

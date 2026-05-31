import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class DelayDetector(Node):
    def __init__(self):
        super().__init__('delay_detector')

        self.delay_threshold = 5.0

        self.subscription = self.create_subscription(
            String,
            'cell_state',
            self.detect_delay,
            10
        )

        self.publisher_ = self.create_publisher(String, 'delay_status', 10)

        self.get_logger().info('Delay Detector started')
        self.get_logger().info('Listening to /cell_state and publishing delay info on /delay_status')

    def detect_delay(self, msg):
        try:
            data = json.loads(msg.data)

            cell_1_time = data["cell_1"]["task_time"]
            cell_2_time = data["cell_2"]["task_time"]

            cell_1_workload = data["cell_1"]["workload"]
            cell_2_workload = data["cell_2"]["workload"]

            delay_report = {
                "timestamp": data["timestamp"],
                "delay_detected": False,
                "delayed_cell": None,
                "message": "Both cells are working normally",
                "cell_1_task_time": cell_1_time,
                "cell_2_task_time": cell_2_time,
                "cell_1_workload": cell_1_workload,
                "cell_2_workload": cell_2_workload
            }

            if cell_1_time > self.delay_threshold:
                delay_report["delay_detected"] = True
                delay_report["delayed_cell"] = "cell_1"
                delay_report["message"] = "Delay detected in Cell 1. Cell 2 should prepare to share workload."

            elif cell_2_time > self.delay_threshold:
                delay_report["delay_detected"] = True
                delay_report["delayed_cell"] = "cell_2"
                delay_report["message"] = "Delay detected in Cell 2. Cell 1 should prepare to share workload."

            output_msg = String()
            output_msg.data = json.dumps(delay_report)

            self.publisher_.publish(output_msg)

            if delay_report["delay_detected"]:
                self.get_logger().warn(output_msg.data)
            else:
                self.get_logger().info(output_msg.data)

        except Exception as e:
            self.get_logger().error(f'Failed to process cell state: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = DelayDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

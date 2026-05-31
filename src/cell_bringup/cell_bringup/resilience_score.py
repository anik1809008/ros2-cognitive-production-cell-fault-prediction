import json
import random

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ResilienceScore(Node):
    def __init__(self):
        super().__init__('resilience_score')

        self.max_allowed_delay = 10.0

        self.subscription = self.create_subscription(
            String,
            'reallocation_decision',
            self.calculate_score,
            10
        )

        self.publisher_ = self.create_publisher(String, 'resilience_score', 10)

        self.get_logger().info('Resilience Score node started')
        self.get_logger().info('Listening to /reallocation_decision and publishing /resilience_score')

    def calculate_score(self, msg):
        try:
            data = json.loads(msg.data)

            if data["reallocation_required"]:
                recovery_time = round(random.uniform(2.0, 5.0), 2)
                score = round(1 - (recovery_time / self.max_allowed_delay), 2)

                result = {
                    "timestamp": data["timestamp"],
                    "event": "adaptive_recovery",
                    "delayed_cell": data["delayed_cell"],
                    "target_cell": data["target_cell"],
                    "workload_shift_percent": data["workload_shift_percent"],
                    "recovery_time": recovery_time,
                    "max_allowed_delay": self.max_allowed_delay,
                    "digital_twin_resilience_score": score,
                    "system_status": "Production continued through adaptive workload sharing"
                }

                self.get_logger().warn(json.dumps(result))

            else:
                result = {
                    "timestamp": data["timestamp"],
                    "event": "normal_operation",
                    "recovery_time": 0.0,
                    "max_allowed_delay": self.max_allowed_delay,
                    "digital_twin_resilience_score": 1.0,
                    "system_status": "Both cells operating normally"
                }

                self.get_logger().info(json.dumps(result))

            output_msg = String()
            output_msg.data = json.dumps(result)
            self.publisher_.publish(output_msg)

        except Exception as e:
            self.get_logger().error(f'Failed to calculate resilience score: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = ResilienceScore()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

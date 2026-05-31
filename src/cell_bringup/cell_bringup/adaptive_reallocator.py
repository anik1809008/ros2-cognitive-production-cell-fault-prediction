import json
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class AdaptiveReallocator(Node):
    def __init__(self):
        super().__init__('adaptive_reallocator')

        self.subscription = self.create_subscription(
            String,
            'delay_status',
            self.reallocate_workload,
            10
        )

        self.publisher_ = self.create_publisher(String, 'reallocation_decision', 10)

        self.get_logger().info('Adaptive Reallocator started')
        self.get_logger().info('Listening to /delay_status and publishing /reallocation_decision')

    def reallocate_workload(self, msg):
        try:
            data = json.loads(msg.data)

            decision = {
                "timestamp": data["timestamp"],
                "delay_detected": data["delay_detected"],
                "delayed_cell": data["delayed_cell"],
                "reallocation_required": False,
                "source_cell": None,
                "target_cell": None,
                "workload_shift_percent": 0,
                "recovery_action": "No recovery needed. Both cells continue normal operation.",
                "decision_time": time.time()
            }

            if data["delay_detected"]:
                decision["reallocation_required"] = True

                if data["delayed_cell"] == "cell_1":
                    decision["source_cell"] = "cell_1"
                    decision["target_cell"] = "cell_2"
                    decision["workload_shift_percent"] = 40
                    decision["recovery_action"] = "Cell 1 delayed. Shift 40% workload to Cell 2."

                elif data["delayed_cell"] == "cell_2":
                    decision["source_cell"] = "cell_2"
                    decision["target_cell"] = "cell_1"
                    decision["workload_shift_percent"] = 40
                    decision["recovery_action"] = "Cell 2 delayed. Shift 40% workload to Cell 1."

            output_msg = String()
            output_msg.data = json.dumps(decision)
            self.publisher_.publish(output_msg)

            if decision["reallocation_required"]:
                self.get_logger().warn(output_msg.data)
            else:
                self.get_logger().info(output_msg.data)

        except Exception as e:
            self.get_logger().error(f'Failed to process delay status: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = AdaptiveReallocator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

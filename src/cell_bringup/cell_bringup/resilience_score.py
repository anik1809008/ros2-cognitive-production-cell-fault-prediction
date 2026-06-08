import json
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


class ResilienceScore(Node):
    def __init__(self):
        super().__init__('resilience_score')

        self.delay_threshold = 5.0
        self.max_task_time = 9.0
        self.last_delay_status = {}

        self.delay_subscription = self.create_subscription(
            String,
            'delay_status',
            self.update_delay_status,
            10
        )

        self.decision_subscription = self.create_subscription(
            String,
            'reallocation_decision',
            self.calculate_score,
            10
        )

        self.publisher_ = self.create_publisher(String, 'resilience_score', 10)

        self.get_logger().info('Multi-Objective Resilience Score node started')
        self.get_logger().info('Listening to /delay_status and /reallocation_decision')

    def update_delay_status(self, msg):
        try:
            self.last_delay_status = json.loads(msg.data)
        except Exception as e:
            self.get_logger().error(f'Failed to update delay status: {e}')

    def calculate_score(self, msg):
        try:
            decision = json.loads(msg.data)
            delay = self.last_delay_status

            cell_1_time = float(delay.get('cell_1_task_time', 4.0))
            cell_2_time = float(delay.get('cell_2_task_time', 4.0))
            cell_1_workload = float(delay.get('cell_1_workload', 50))
            cell_2_workload = float(delay.get('cell_2_workload', 50))

            max_time = max(cell_1_time, cell_2_time)

            # 1. Throughput score: lower task time means better throughput
            throughput_score = clamp(1.0 - ((max_time - 3.0) / (self.max_task_time - 3.0)))

            # 2. Delay score: penalize time above threshold
            if max_time <= self.delay_threshold:
                delay_score = 1.0
            else:
                delay_score = clamp(1.0 - ((max_time - self.delay_threshold) / (self.max_task_time - self.delay_threshold)))

            # 3. Workload balance score: closer workload balance is better
            workload_gap = abs(cell_1_workload - cell_2_workload)
            workload_balance_score = clamp(1.0 - (workload_gap / 100.0))

            # 4. Recovery action score: reward reallocation during delay
            delay_detected = bool(decision.get('delay_detected', False))
            reallocation_required = bool(decision.get('reallocation_required', False))

            if delay_detected and reallocation_required:
                recovery_action_score = 1.0
                event = 'adaptive_recovery'
                system_status = 'Adaptive workload reallocation active'
            elif delay_detected and not reallocation_required:
                recovery_action_score = 0.3
                event = 'unhandled_delay'
                system_status = 'Delay detected but no recovery action selected'
            else:
                recovery_action_score = 1.0
                event = 'normal_operation'
                system_status = 'Both cells operating normally'

            # 5. Stability score: penalize severe imbalance and high processing time
            stability_score = clamp((workload_balance_score + delay_score) / 2.0)

            final_score = round(
                (0.30 * throughput_score) +
                (0.25 * delay_score) +
                (0.20 * workload_balance_score) +
                (0.15 * recovery_action_score) +
                (0.10 * stability_score),
                2
            )

            result = {
                'timestamp': decision.get('timestamp'),
                'event': event,
                'delayed_cell': decision.get('delayed_cell'),
                'target_cell': decision.get('target_cell'),
                'workload_shift_percent': decision.get('workload_shift_percent', 0),

                'cell_1_task_time': cell_1_time,
                'cell_2_task_time': cell_2_time,
                'cell_1_workload': cell_1_workload,
                'cell_2_workload': cell_2_workload,

                'throughput_score': round(throughput_score, 2),
                'delay_score': round(delay_score, 2),
                'workload_balance_score': round(workload_balance_score, 2),
                'recovery_action_score': round(recovery_action_score, 2),
                'stability_score': round(stability_score, 2),

                'digital_twin_resilience_score': final_score,
                'recovery_time': 0.0,
                'scoring_method': 'multi_objective_weighted_score',
                'system_status': system_status,
                'calculation_time': time.time()
            }

            output_msg = String()
            output_msg.data = json.dumps(result)
            self.publisher_.publish(output_msg)

            if event == 'adaptive_recovery':
                self.get_logger().warn(json.dumps(result))
            else:
                self.get_logger().info(json.dumps(result))

        except Exception as e:
            self.get_logger().error(f'Failed to calculate multi-objective score: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = ResilienceScore()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

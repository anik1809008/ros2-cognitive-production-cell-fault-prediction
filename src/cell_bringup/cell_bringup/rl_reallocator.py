import json
import random
import time
from collections import defaultdict

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class RLReallocator(Node):
    def __init__(self):
        super().__init__('rl_reallocator')

        self.latest_prediction = {}

        self.actions = [0, 20, 40, 60, 80]
        self.q_table = defaultdict(lambda: {a: 0.0 for a in self.actions})

        self.epsilon = 0.15
        self.learning_rate = 0.2
        self.discount_factor = 0.9

        self.prediction_sub = self.create_subscription(
            String,
            'fault_prediction',
            self.update_prediction,
            10
        )

        self.delay_sub = self.create_subscription(
            String,
            'delay_status',
            self.select_reallocation_action,
            10
        )

        self.publisher_ = self.create_publisher(
            String,
            'reallocation_decision',
            10
        )

        self.get_logger().info('RL Reallocator started')
        self.get_logger().info('Listening to /delay_status and /fault_prediction')
        self.get_logger().info('Publishing RL decisions on /reallocation_decision')

    def update_prediction(self, msg):
        try:
            self.latest_prediction = json.loads(msg.data)
        except Exception as e:
            self.get_logger().error(f'Failed to read fault prediction: {e}')

    def discretize_state(self, delayed_cell, risk_level, c1_workload, c2_workload):
        workload_gap = abs(c1_workload - c2_workload)

        if workload_gap < 15:
            balance_state = 'balanced'
        elif workload_gap < 30:
            balance_state = 'moderate_imbalance'
        else:
            balance_state = 'high_imbalance'

        return f'{delayed_cell}_{risk_level}_{balance_state}'

    def calculate_reward(self, action, delay_detected, risk_level, c1_workload, c2_workload):
        if not delay_detected:
            if action == 0:
                return 1.0
            return -0.3

        workload_gap = abs(c1_workload - c2_workload)

        reward = 0.0

        if risk_level == 'HIGH':
            if action in [60, 80]:
                reward += 1.0
            elif action == 40:
                reward += 0.6
            else:
                reward -= 0.4

        elif risk_level == 'MEDIUM':
            if action in [40, 60]:
                reward += 0.8
            elif action == 20:
                reward += 0.4
            else:
                reward -= 0.2

        else:
            if action in [20, 40]:
                reward += 0.5
            elif action == 0:
                reward += 0.2
            else:
                reward -= 0.3

        if workload_gap > 30 and action >= 60:
            reward -= 0.2

        if action == 80:
            reward -= 0.1

        return round(reward, 2)

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.choice(self.actions), 'exploration'

        q_values = self.q_table[state]
        best_action = max(q_values, key=q_values.get)
        return best_action, 'exploitation'

    def update_q_value(self, state, action, reward):
        old_q = self.q_table[state][action]
        max_future_q = max(self.q_table[state].values())

        new_q = old_q + self.learning_rate * (
            reward + self.discount_factor * max_future_q - old_q
        )

        self.q_table[state][action] = round(new_q, 3)

    def select_reallocation_action(self, msg):
        try:
            delay_data = json.loads(msg.data)

            delay_detected = bool(delay_data.get('delay_detected', False))
            delayed_cell = delay_data.get('delayed_cell')

            c1_workload = float(delay_data.get('cell_1_workload', 50))
            c2_workload = float(delay_data.get('cell_2_workload', 50))

            risk_level = self.latest_prediction.get('risk_level', 'LOW')
            predicted_cell = self.latest_prediction.get('predicted_fault_cell')
            c1_probability = self.latest_prediction.get('cell_1_fault_probability', 0.0)
            c2_probability = self.latest_prediction.get('cell_2_fault_probability', 0.0)

            if not delay_detected:
                action = 0
                policy_mode = 'normal_no_reallocation'
                source_cell = None
                target_cell = None
                reallocation_required = False
                recovery_action = 'No delay detected. RL agent keeps normal operation.'
                state = 'normal'
                reward = 1.0

            else:
                state = self.discretize_state(
                    delayed_cell,
                    risk_level,
                    c1_workload,
                    c2_workload
                )

                action, policy_mode = self.choose_action(state)
                reward = self.calculate_reward(
                    action,
                    delay_detected,
                    risk_level,
                    c1_workload,
                    c2_workload
                )

                self.update_q_value(state, action, reward)

                reallocation_required = action > 0
                source_cell = delayed_cell

                if delayed_cell == 'cell_1':
                    target_cell = 'cell_2'
                elif delayed_cell == 'cell_2':
                    target_cell = 'cell_1'
                else:
                    target_cell = None

                if reallocation_required:
                    recovery_action = (
                        f'RL selected {action}% workload shift from '
                        f'{source_cell} to {target_cell}.'
                    )
                else:
                    recovery_action = 'RL selected no workload shift.'

            decision = {
                'timestamp': delay_data.get('timestamp'),
                'delay_detected': delay_detected,
                'delayed_cell': delayed_cell,
                'reallocation_required': reallocation_required,
                'source_cell': source_cell,
                'target_cell': target_cell,
                'workload_shift_percent': action,
                'recovery_action': recovery_action,

                'rl_state': state,
                'rl_policy_mode': policy_mode,
                'rl_reward': reward,
                'rl_epsilon': self.epsilon,
                'risk_level': risk_level,
                'predicted_fault_cell': predicted_cell,
                'cell_1_fault_probability': c1_probability,
                'cell_2_fault_probability': c2_probability,
                'decision_time': time.time(),
                'method': 'online_q_learning_reallocator'
            }

            output_msg = String()
            output_msg.data = json.dumps(decision)
            self.publisher_.publish(output_msg)

            if reallocation_required:
                self.get_logger().warn(json.dumps(decision))
            else:
                self.get_logger().info(json.dumps(decision))

        except Exception as e:
            self.get_logger().error(f'RL reallocation failed: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = RLReallocator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

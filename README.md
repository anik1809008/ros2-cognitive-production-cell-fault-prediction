# ros2-cognitive-production-cell-fault-prediction
# ROS 2 Cognitive Production Cell: Resilience-Aware Digital Twin

A ROS 2 Jazzy and Gazebo Harmonic based digital-twin prototype for a two-cell production system. The project simulates production-cell delay, detects delay conditions, performs rule-based adaptive workload reallocation, visualizes workpiece routing changes in Gazebo, calculates a digital-twin resilience score, and logs experiment results to CSV.

> Current implementation status: this project implements rule-based delay detection and adaptive recovery visualization. It does not yet implement machine-learning-based future fault prediction.

---

## Project Overview

The system represents a simplified production cell with:

* Loading station
* Production Cell 1
* Production Cell 2
* Shared buffer
* Output station
* Delay-monitoring zone
* Animated workpieces
* Delay and helper markers

The ROS 2 nodes exchange JSON-formatted messages using `std_msgs/msg/String`. The Gazebo world visualizes the production layout and the adaptive rerouting of workpieces.

---

## Main Features

* Two-cell production state simulation
* Periodic delay scenario generation
* Threshold-based delay detection
* Adaptive workload reallocation decision
* Continuous workpiece flow animation in Gazebo
* Red marker for delayed cell
* Yellow marker for assisting cell
* Resilience score calculation
* CSV-based experiment logging
* ROS 2 launch file for the monitoring and recovery pipeline

---

## System Architecture

```text
/cell_state_simulator
        publishes → /cell_state
              ↓
/delay_detector
        publishes → /delay_status
              ↓
/adaptive_reallocator
        publishes → /reallocation_decision
              ↓
/resilience_score
        publishes → /resilience_score
              ↓
/experiment_logger
        writes → results/resilience_results.csv


/continuous_workpiece_animator
        subscribes → /reallocation_decision
        controls Gazebo workpiece animation through gz service
```

---

## ROS 2 Nodes

| Node                            | Purpose                                                          |
| ------------------------------- | ---------------------------------------------------------------- |
| `cell_state_simulator`          | Publishes simulated task time and workload for Cell 1 and Cell 2 |
| `delay_detector`                | Detects delay when task time exceeds the threshold               |
| `adaptive_reallocator`          | Decides workload shift from delayed cell to healthy cell         |
| `resilience_score`              | Calculates resilience score based on recovery event              |
| `experiment_logger`             | Logs experiment results into CSV                                 |
| `continuous_workpiece_animator` | Animates continuous workpiece flow in Gazebo                     |
| `gazebo_workpiece_animator`     | Older/event-based animation node                                 |
| `simple_publisher`              | Basic ROS 2 test publisher                                       |
| `simple_subscriber`             | Basic ROS 2 test subscriber                                      |

---

## ROS Topics

| Topic                    | Message Type          | Description                          |
| ------------------------ | --------------------- | ------------------------------------ |
| `/cell_state`            | `std_msgs/msg/String` | Cell task time and workload          |
| `/delay_status`          | `std_msgs/msg/String` | Delay detection result               |
| `/reallocation_decision` | `std_msgs/msg/String` | Adaptive workload-sharing decision   |
| `/resilience_score`      | `std_msgs/msg/String` | Resilience score and recovery status |

---

## Delay Scenario Logic

The cell-state simulator follows a 40-second repeating cycle:

| Time Phase | Behavior         |
| ---------- | ---------------- |
| 0–7 sec    | Normal operation |
| 8–16 sec   | Cell 1 delay     |
| 17–21 sec  | Normal operation |
| 22–30 sec  | Cell 2 delay     |
| 31–39 sec  | Normal operation |

During delay, the affected cell receives increased task time and workload.

---

## Adaptive Reallocation Logic

| Condition      | Recovery Decision            |
| -------------- | ---------------------------- |
| Cell 1 delayed | Shift 40% workload to Cell 2 |
| Cell 2 delayed | Shift 40% workload to Cell 1 |
| No delay       | Continue normal operation    |

In Gazebo, this is visualized by changing workpiece routing:

| Mode           | Workpiece Distribution               |
| -------------- | ------------------------------------ |
| Normal         | 2 boxes to Cell 1, 2 boxes to Cell 2 |
| Cell 1 delayed | 1 box to Cell 1, 3 boxes to Cell 2   |
| Cell 2 delayed | 1 box to Cell 2, 3 boxes to Cell 1   |

---

## Requirements

* Ubuntu 24.04
* ROS 2 Jazzy
* Gazebo Harmonic
* Python 3.12
* `colcon`

---

## Build Instructions

```bash
cd ~/ros2-cognitive-production-cell-fault-prediction
source /opt/ros/jazzy/setup.bash

rm -rf build install log
colcon build --symlink-install --packages-select cell_bringup

source install/setup.bash
```

---

## Run ROS Logic Pipeline

```bash
cd ~/ros2-cognitive-production-cell-fault-prediction
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch cell_bringup digital_twin_demo.launch.py
```

---

## Run Gazebo World Separately

Open a new terminal:

```bash
cd ~/ros2-cognitive-production-cell-fault-prediction
gz sim worlds/factory_world.sdf
```

Then run the ROS launch file in another terminal.

---

## Run Full Digital Twin Launch

If using the packaged world file:

```bash
cd ~/ros2-cognitive-production-cell-fault-prediction
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch cell_bringup digital_twin_full.launch.py
```

---

## Useful Debug Commands

```bash
ros2 node list
ros2 topic list -t
ros2 topic echo /cell_state --once
ros2 topic echo /delay_status --once
ros2 topic echo /reallocation_decision --once
ros2 topic echo /resilience_score --once
```

Check Gazebo services:

```bash
gz service -l | grep resilience_aware_digital_twin_world
gz service -l | grep set_pose
```

Test model control:

```bash
gz service \
-s /world/resilience_aware_digital_twin_world/set_pose \
--reqtype gz.msgs.Pose \
--reptype gz.msgs.Boolean \
--timeout 3000 \
--req 'name: "flow_box_1", position: {x: -8, y: 0, z: 1.2}, orientation: {x: 0, y: 0, z: 0, w: 1}'
```

Expected response:

```text
data: true
```

---

## Result Logging

The logger writes experiment output to:

```text
results/resilience_results.csv
```

Example event types:

* `normal_operation`
* `adaptive_recovery`

Logged fields:

* timestamp
* event
* delayed cell
* target cell
* workload shift percentage
* recovery time
* resilience score
* system status

---

## Current Limitations

* Fault handling is rule-based, not machine-learning-based.
* Delay is detected after task time exceeds a threshold; future fault prediction is not yet implemented.
* Recovery is represented through routing decisions and Gazebo animation.
* Resilience score currently uses simulated recovery time.
* Messages are JSON strings over `std_msgs/msg/String`; custom ROS messages can improve structure later.
* Gazebo is controlled through `gz service` pose updates, not through a physics-based conveyor or robot controller.

---

## Future Work

* Add `fault_predictor.py` for actual predictive fault detection.
* Add manual fault injection service such as `/inject_fault`.
* Replace JSON strings with custom ROS 2 message types.
* Improve resilience score using measured recovery duration and throughput loss.
* Add closed-loop feedback from recovery decision to cell-state simulation.
* Add plots for resilience score and recovery events.
* Add automated test scripts and demo videos.
* Add a complete architecture diagram.

---

## License

MIT License


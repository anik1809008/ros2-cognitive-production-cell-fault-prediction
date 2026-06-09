# Digital Twin for Smart Manufacturing with Reinforcement Learning Dashboard

## Project Overview
This project implements a **real-time digital twin** for smart manufacturing cells using **ROS 2** and **Gazebo**. The twin simulates a **two-cell production line**, monitors workpiece flow, predicts potential faults or delays, and dynamically reallocates workloads using a **reinforcement learning (RL) agent**.  

It bridges **simulation, intelligent decision-making, and interactive visualization**, demonstrating modern **Industry 4.0 / 5.0** manufacturing principles.  

---

## Motivation
Factories face challenges like unexpected delays, uneven workloads, and equipment faults. This digital twin:

- Predicts potential delays before they happen (e.g., detects if task completion may exceed **5 seconds** threshold per workpiece).  
- Adapts workload allocation using **RL-based strategies**.  
- Evaluates system performance via **multi-objective resilience scoring**.  
- Visualizes operations on a **live dashboard** for monitoring and research.

This makes it a **research-grade demonstration of smart manufacturing**.

---

## Key Features

### Digital Twin Simulation
- Simulates two production cells in **Gazebo**.
- Workpieces move along defined paths.
- Monitors **task completion times**, **workload**, and **delays**.

### Predictive Fault Detection
- Forecasts cell delays using historical task data.
- Classifies risk levels: **LOW, MEDIUM, HIGH**.
- Provides early warnings for preemptive recovery.

### RL-Based Adaptive Reallocation
- Dynamically adjusts workload between cells (0%, 20%, 40%, 60%, 80%).  
- Learns optimal recovery actions to minimize delays and maximize throughput.
- Considers predicted faults and workload balance.

### Multi-Objective Resilience Scoring
- Scores system performance using:
  - Throughput efficiency  
  - Delay reduction  
  - Workload balance  
  - Recovery speed  
  - Stability  
- Provides a numeric **resilience score** for each event.

### Web-Based Dashboard
- Shows live **cell state, predicted faults, RL decisions, and resilience score**.
- Updates every **~1 second** for real-time monitoring.
- Example dashboard view:  
![Dashboard Placeholder](path_to_dashboard_image.jpg)  

### Simulation Visualization
- Gazebo simulation illustrates **workpiece movement, cell delays, and recovery actions**.  
- Example simulation snapshot:  
![Simulation Placeholder](path_to_simulation_image.jpg)  

### Experiment Logging
- Logs all events, decisions, and resilience metrics.
- Enables analysis of RL performance and system effectiveness over time.

---

## Tools and Technologies
- **ROS 2 (Jazzy)** – Robotic middleware for real-time communication.
- **Gazebo** – Physics-based simulation of manufacturing cells.
- **Python (rclpy)** – ROS 2 node implementation.
- **FastAPI & WebSocket** – Web dashboard backend for live updates.
- **HTML, CSS, JavaScript** – Frontend visualization.
- **Reinforcement Learning (Q-learning)** – Adaptive workload allocation.
- **JSON** – Communication format between ROS 2 nodes and dashboard.

---

## How It Works
1. **Monitoring:** Gazebo simulates cells; ROS 2 nodes track task times, workloads, and delays.
2. **Prediction:** Fault predictor estimates potential delay/failure probabilities.
3. **Decision:** RL reallocator chooses optimal workload shifts based on prediction and cell state.
4. **Scoring:** Multi-objective resilience module calculates performance metrics.
5. **Visualization:** Web dashboard displays live state, predictions, RL actions, and resilience score.
6. **Logging:** All events and metrics are stored for analysis and research evaluation.

---

## Live Demo / Access
- Dashboard: [http://127.0.0.1:8000](http://127.0.0.1:8000)  
- The simulation can be run locally via **Gazebo + ROS 2 launch** commands.

---

## Use Cases
- Demonstrates predictive and adaptive smart manufacturing systems.
- Suitable for **research, PhD applications, and academic demonstrations**.
- Can serve as a foundation for **ML-based predictive fault models** in future phases.

---

## Contact
For inquiries or collaborations: **anik1809008@example.com**

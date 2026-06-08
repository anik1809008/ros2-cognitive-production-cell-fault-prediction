import asyncio
import json
import threading
import time
from pathlib import Path

import rclpy
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from rclpy.node import Node
from std_msgs.msg import String
import uvicorn


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

app = FastAPI(title="Digital Twin Dashboard")

latest_state = {
    "connected": False,
    "last_update": None,
    "cell_state": {},
    "delay_status": {},
    "reallocation_decision": {},
    "resilience_score": {},
}


class DashboardBridge(Node):
    def __init__(self):
        super().__init__("dashboard_bridge")

        self.create_subscription(
            String,
            "/cell_state",
            lambda msg: self.update_state("cell_state", msg),
            10,
        )

        self.create_subscription(
            String,
            "/delay_status",
            lambda msg: self.update_state("delay_status", msg),
            10,
        )

        self.create_subscription(
            String,
            "/reallocation_decision",
            lambda msg: self.update_state("reallocation_decision", msg),
            10,
        )

        self.create_subscription(
            String,
            "/resilience_score",
            lambda msg: self.update_state("resilience_score", msg),
            10,
        )

        self.get_logger().info("Dashboard bridge started")
        self.get_logger().info("Listening to ROS topics for dashboard updates")

    def update_state(self, key, msg):
        try:
            latest_state[key] = json.loads(msg.data)
        except json.JSONDecodeError:
            latest_state[key] = {"raw": msg.data}

        latest_state["connected"] = True
        latest_state["last_update"] = time.strftime("%H:%M:%S")


def ros_spin_thread():
    rclpy.init(args=None)
    node = DashboardBridge()

    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


@app.on_event("startup")
def start_ros_bridge():
    thread = threading.Thread(target=ros_spin_thread, daemon=True)
    thread.start()


@app.get("/")
def serve_dashboard():
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            await websocket.send_json(latest_state)
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        pass


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )

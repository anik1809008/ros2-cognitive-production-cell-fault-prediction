const socket = new WebSocket("ws://127.0.0.1:8000/ws");

function setText(id, value) {
    const element = document.getElementById(id);
    if (!element) return;

    if (value === undefined || value === null || value === "") {
        element.textContent = "--";
    } else {
        element.textContent = value;
    }
}

function setClassByBoolean(id, value) {
    const element = document.getElementById(id);
    if (!element) return;

    element.classList.remove("good", "bad", "warning");

    if (value === true) {
        element.classList.add("bad");
    } else if (value === false) {
        element.classList.add("good");
    }
}

socket.onopen = () => {
    setText("connection", "Connected to dashboard server");
};

socket.onclose = () => {
    setText("connection", "Disconnected");
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    const cellState = data.cell_state || {};
    const delayStatus = data.delay_status || {};
    const decision = data.reallocation_decision || {};
    const score = data.resilience_score || {};

    const cell1 = cellState.cell_1 || {};
    const cell2 = cellState.cell_2 || {};

    setText("connection", data.connected ? "Live" : "Waiting for ROS data");
    setText("lastUpdate", data.last_update);

    const mode = decision.reallocation_required ? "RECOVERY ACTIVE" : "NORMAL OPERATION";
    setText("systemMode", mode);

    setText("cell1Status", cell1.status);
    setText("cell1TaskTime", cell1.task_time);
    setText("cell1Workload", cell1.workload);

    setText("cell2Status", cell2.status);
    setText("cell2TaskTime", cell2.task_time);
    setText("cell2Workload", cell2.workload);

    setText("delayDetected", delayStatus.delay_detected);
    setText("delayedCell", delayStatus.delayed_cell || "none");
    setText("delayMessage", delayStatus.message);
    setClassByBoolean("delayDetected", delayStatus.delay_detected);

    setText("reallocationRequired", decision.reallocation_required);
    setText("sourceCell", decision.source_cell || "none");
    setText("targetCell", decision.target_cell || "none");
    setText("workloadShift", decision.workload_shift_percent);
    setText("recoveryAction", decision.recovery_action);

    setText("resilienceScore", score.digital_twin_resilience_score);
    setText("eventType", score.event);
    setText("recoveryTime", score.recovery_time);
    setText("systemStatus", score.system_status);

    setText("rawJson", JSON.stringify(data, null, 2));
};

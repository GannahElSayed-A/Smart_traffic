# 🚦 Smart Adaptive Traffic Control System (IoT & Node-RED)

An intelligent, adaptive traffic management system based on **IoT** and **Edge Computing** designed to reduce traffic congestion. It analyzes real-time vehicle density across four intersections (North, South, East, West) and dynamically controls signal timings via **Node-RED** over the **MQTT** protocol.

---

## 🏗️ System Architecture

The system consists of three core layers operating synchronously:

```text
 [ HC-SR04 Sensors / Canvas Sim ]
                 │
                 ▼  (MQTT Telemetry / Websockets)
          [ MQTT Broker ]
                 │
                 ▼
        [ Node-RED Engine ] ──► (Calculates adaptive timing / Emergency override)
                 │
                 ▼  (MQTT Commands)
  [ Traffic Light Actuators / Edge ]
```

1. **Edge & Simulation Layer:**
   * Interactive HTML5 Canvas simulating an **ESP32** microcontroller.
   * Four simulated **HC-SR04** ultrasonic sensors to measure road density.
   * Electromechanical actuators driving traffic signal lights (Red, Yellow, Green).

2. **Message Broker:**
   * **MQTT over WebSockets** for low-latency transmission of sensor telemetry and actuator commands.

3. **Logic Engine (Node-RED):**
   * Central algorithm calculating adaptive green-light durations based on traffic density.
   * Local **Fallback Mechanism** for network fault tolerance.
   * **Emergency Preemption Control** system.

---

## ✨ Key Features

* **Adaptive Traffic Control:** Dynamically calculates green light duration between a minimum ($T_{min} = 5s$) and maximum ($T_{max} = 30s$) threshold based on real-time vehicle density.
* **Automatic Fallback:** Automatically reverts to a local fixed timer (`FIXED = 12s`) if telemetry signals are interrupted for longer than 5 seconds (`TELEMETRY_TIMEOUT_MS`).
* **Emergency Vehicle Preemption:** Instantly overrides signal schedules to grant immediate green lights for active emergency vehicles.
* **Safety Transition Interval:** Enforces a mandatory 3-second yellow light phase during directional changes to ensure intersection clearance and prevent collisions.
* **Heartbeat Monitoring:** Continuously tracks operational health, uptime (`uptime_ms`), and connectivity status.

---

## 📡 MQTT Protocol & Topics

| Topic | Direction | Payload Type | Description |
| :--- | :--- | :--- | :--- |
| `smarttraffic/intersection01/telemetry` | Publisher (Edge ➔ Server) | JSON | Congestion percentages for lanes (`north`, `south`, `east`, `west`). |
| `smarttraffic/intersection01/heartbeat` | Publisher (Edge ➔ Server) | JSON | Health status check and system uptime (`uptime_ms`). |
| `smarttraffic/intersection01/command` | Subscriber (Server ➔ Edge) | JSON | Incoming phase control (`SET_PHASE`) or emergency overrides (`EMERGENCY` / `CLEAR_EMERGENCY`). |

---

## ⚙️ Configuration Parameters

| Parameter | Default Value | Description |
| :--- | :--- | :--- |
| `T_MIN` | `5s` | Minimum green light duration |
| `T_MAX` | `30s` | Maximum green light duration |
| `FIXED_DURATION` | `12s` | Fixed phase duration when running in Fallback mode |
| `TELEMETRY_TIMEOUT_MS` | `5000ms` | Timeout threshold before declaring loss of server connection |
| `YELLOW_DURATION` | `3s` | Duration of the yellow safety clearance light |

---

## 🚀 Quick Start

### 1. Node-RED Setup
1. Launch Node-RED and import the `flow.json` file.
2. Configure the MQTT Broker node to point to `broker.hivemq.com` using WebSocket port `8000` (or your custom broker setup).
3. Click **Deploy**.

### 2. Launch Simulation
1. Open `index.html` in any modern browser.
2. The simulation will automatically connect to the MQTT broker.
3. Use the **"+ Car"** button to generate traffic density or click **"🚨 Emergency"** to test priority preemption handling.

---

## 🛠️ Tech Stack

* **Front-End / Edge:** HTML5, CSS3, JavaScript (ES6+), Canvas API.
* **Communication:** MQTT over WebSockets (`mqtt.js`).
* **Backend & Logic Engine:** Node-RED (JavaScript Function Nodes & Context Storage).

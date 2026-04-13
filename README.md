# 🐾 WildAlert: Intelligent Wildlife Detection & Collision Alert System

WildAlert is an AI-powered road safety system designed to detect wildlife near roadways and prevent animal–vehicle collisions. The system uses deep learning (YOLOv8) for real-time object detection and integrates IoT (ESP8266 + MQTT) to generate instant roadside alerts.

---

## 🚀 Features

- 🔍 Real-time animal and vehicle detection using YOLOv8
- 📷 Supports live camera, image, and video inputs
- ⚠️ Collision risk analysis based on object distance
- 📡 MQTT-based communication system
- 💡 Roadside alert system (LED, buzzer, LCD display)
- 🌐 Web dashboard for monitoring detection events
- 📊 Control room interface for collision logs

---

## 🧠 Technologies Used

- Deep Learning: YOLOv8 (Ultralytics)
- Backend: Flask (Python)
- Computer Vision: OpenCV
- IoT Device: ESP8266
- Protocol: MQTT (HiveMQ broker)
- Frontend: HTML, CSS (Flask templates)

---

## ⚙️ System Architecture

1. Live camera captures frames  
2. YOLOv8 detects animals and vehicles  
3. Distance-based collision risk analysis  
4. Alert generated if risk detected  
5. MQTT sends alert to ESP8266  
6. Roadside unit activates:
   - LED (visual alert)
   - Buzzer (audio alert)
   - LCD (message display)  
7. Control room dashboard logs events  

---

## 📂 Project Structure
WildAlert/ │── app.py                 
# Main Flask application │── model/                 
# YOLO model files │── static/                
# Uploaded and result images/videos │── templates/             
# HTML pages │── esp8266/               
# IoT code for alert unit │── requirements.txt       
# Python dependencies


---

## 🔧 Installation

### 1️⃣ Clone the Repository
`bash
git clone https://github.com/your-username/WildAlert.git
cd WildAlert

pip install -r requirements.txt

python app.py

http://127.0.0.1:5000/

📡 MQTT Configuration
Broker: broker.hivemq.com
Topics:
wildalert/test → Roadside alerts
wildalert/controlroom → Collision logs
🔌 ESP8266 Setup
Connect:
LED → D5
Buzzer → D7
LCD (I2C) → SDA, SCL
Upload Arduino code to ESP8266
Ensure WiFi & MQTT connection
📊 Output
Real-time detection with bounding boxes
Collision alerts triggered instantly
LCD displays messages like:
STOP! Wildlife Crossing
Go Slow
Control room dashboard shows recent events
🎯 Applications
Highway safety systems
Forest and wildlife areas
Smart transportation systems
Accident prevention systems
🔮 Future Scope
Night vision / thermal camera integration
GPS-based alert tracking
Mobile app notifications
Edge AI deployment (low-power devices)
Advanced collision prediction using tracking
👨‍💻 Contributors
Amruth Krishnan M
📄 License
This project is for academic and research purposes.

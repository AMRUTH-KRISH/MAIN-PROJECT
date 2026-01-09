from flask import Flask, render_template, request, Response
from ultralytics import YOLO
import cv2, os, math, json
import paho.mqtt.client as mqtt
from datetime import datetime

app = Flask(__name__)

# ---------------- MQTT CONFIG ----------------
BROKER = "broker.hivemq.com"
ROAD_TOPIC = "wildalert/test"
CONTROL_TOPIC = "wildalert/controlroom"

mqtt_client = mqtt.Client()
mqtt_client.connect(BROKER, 1883, 60)

last_state = "CLEAR"

def send_alert(state):
    global last_state
    if state != last_state:
        mqtt_client.publish(ROAD_TOPIC, state)
        last_state = state

# ---------------- YOLO ----------------
model = YOLO("model/yolov8n.pt")

ANIMALS = ["cow","dog","horse","sheep","elephant","bear","zebra","giraffe"]
VEHICLES = ["car","truck","bus","motorbike"]

COLLISION_DISTANCE = 120
SAFE_DISTANCE = 180

collision_events = []
collision_active = False

def center_distance(a, b):
    ax, ay = (a[0]+a[2])//2, (a[1]+a[3])//2
    bx, by = (b[0]+b[2])//2, (b[1]+b[3])//2
    return math.sqrt((ax-bx)**2 + (ay-by)**2)

# ---------------- ROUTES ----------------

@app.route("/")
def index():
    send_alert("CLEAR")
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# ---------- IMAGE ----------
@app.route("/image", methods=["GET","POST"])
def image():
    if request.method == "POST":
        file = request.files["image"]
        path = "static/uploads/image.jpg"
        file.save(path)

        res = model(path)
        img = res[0].plot()
        cv2.imwrite("static/results/image_out.jpg", img)

        animals, vehicles = extract_boxes(res)
        send_alert("ALERT" if animals else "CLEAR")
        check_collision(animals, vehicles)

        return render_template("image.html", img="static/results/image_out.jpg")

    return render_template("image.html")

# ---------- VIDEO STREAM ----------
def gen_video(path):
    cap = cv2.VideoCapture(path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        res = model(frame)
        frame = res[0].plot()

        animals, vehicles = extract_boxes(res)
        send_alert("ALERT" if animals else "CLEAR")
        check_collision(animals, vehicles)

        _, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

    cap.release()
    send_alert("CLEAR")

@app.route("/video", methods=["GET","POST"])
def video():
    if request.method == "POST":
        file = request.files["video"]
        file.save("static/uploads/video.mp4")
        return render_template("video.html", stream=True)
    return render_template("video.html", stream=False)

@app.route("/video_feed")
def video_feed():
    return Response(gen_video("static/uploads/video.mp4"),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# ---------- LIVE CAMERA ----------
def gen_live():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        res = model(frame)
        frame = res[0].plot()

        animals, vehicles = extract_boxes(res)
        send_alert("ALERT" if animals else "CLEAR")
        check_collision(animals, vehicles)

        _, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

    cap.release()
    send_alert("CLEAR")

@app.route("/live")
def live():
    return Response(gen_live(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# ---------- COLLISION ----------
@app.route("/collision")
def collision():
    return render_template("collision.html", events=collision_events[-10:])

# ---------- HELPERS ----------
def extract_boxes(res):
    animals = []    # (box, animal_label)
    vehicles = []   # (box, vehicle_label)

    for b in res[0].boxes:
        label = model.names[int(b.cls[0])]
        box = b.xyxy[0]

        if label in ANIMALS:
            animals.append((box, label))

        if label in VEHICLES:
            vehicles.append((box, label))

    return animals, vehicles

def check_collision(animals, vehicles):
    global collision_active

    for (a_box, a_label) in animals:
        for (v_box, v_label) in vehicles:
            dist = center_distance(a_box, v_box)

            if dist < COLLISION_DISTANCE and not collision_active:
                event = {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "animal": a_label.capitalize(),
                    "vehicle": v_label.capitalize(),
                    "event": "Possible Collision"
                }

                collision_events.append(event)
                mqtt_client.publish(CONTROL_TOPIC, json.dumps(event))
                collision_active = True

            if dist > SAFE_DISTANCE and collision_active:
                collision_active = False

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)

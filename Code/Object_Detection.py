import cv2
import time
import serial
from picamera2 import Picamera2

# Serial communication with Arduino
try:
    arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    time.sleep(2)
    print("Connected to Arduino.")
except Exception as e:
    print(f"Failed to connect to Arduino: {e}")
    exit()

# Load class labels MobileNet SSD was trained on
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor", "fan"]

# Load pre-trained MobileNetSSD model
net = cv2.dnn.readNetFromCaffe("deploy.prototxt", "mobilenet_iter_73000.caffemodel")

# Initialize PiCamera2
picam2 = Picamera2()
picam2.preview_configuration.main.size = (700, 500)
picam2.preview_configuration.main.format = "BGR888"
picam2.configure("preview")
picam2.start()

time.sleep(0.5)
print("Camera connected successfully.")

# Log file for detections
output_file = open("detections.txt", "w")

# Track state to avoid spamming same command
last_command = ""

def send_command(command):
    global last_command
    if command != last_command:
        try:
            arduino.write((command + '\n').encode())
            print(f"Sent to Arduino: {command}")
            last_command = command
        except Exception as e:
            print(f"Serial Error: {e}")

try:
    while True:
        start_time = time.time()

        # Capture frame
        frame = picam2.capture_array()
        (h, w) = frame.shape[:2]

        # Prepare for detection
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                     0.007843, (300, 300), 127.5)
        net.setInput(blob)
        detections = net.forward()

        object_detected = False

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:
                object_detected = True
                idx = int(detections[0, 0, i, 1])
                label = CLASSES[idx]
                box = detections[0, 0, i, 3:7] * [w, h, w, h]
                (startX, startY, endX, endY) = box.astype("int")

                # Draw bounding box and label
                cv2.rectangle(frame, (startX, startY), (endX, endY),
                              (0, 255, 0), 2)
                text = f"{label}: {confidence:.2f}"
                cv2.putText(frame, text, (startX, startY - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Log detection
                output_file.write(f"{label}: {confidence:.2f} at [{startX},{startY},{endX},{endY}]\n")

        # Control car
        if object_detected:
            send_command("STOP")
        else:
            send_command("GO")

        # Display frame
        cv2.imshow("Object Detection", frame)

        # FPS display
        end_time = time.time()
        fps = 1.0 / (end_time - start_time)
        print(f"FPS = {int(fps)}")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print("Error:", e)

finally:
    print("Shutting down...")
    output_file.close()
    picam2.stop()
    arduino.close()
    cv2.destroyAllWindows()
import cv2
import serial
import time
from picamera2 import Picamera2
import numpy as np

# Setup serial connection to Arduino
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # Wait for Arduino to reset

# Load Haar Cascade file (Make sure the XML file is in the same directory or give full path)
stop_cascade = cv2.CascadeClassifier("/home/pi/Downloads/stop_sign_classifier_2.xml")

# Initialize the Raspberry Pi camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
picam2.start()
time.sleep(1)  # Allow camera to warm up

def send_command(command):
    try:
        arduino.write((command + '\n').encode())
        print(f"Sent to Arduino: {command}")
    except Exception as e:
        print(f"Serial Error: {e}")

try:
    while True:
        frame = picam2.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        stop_signs = stop_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        if len(stop_signs) > 0:
            print("Stop Sign Detected!")
            send_command("STOP")
            for (x, y, w, h) in stop_signs:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        else:
            send_command("GO")

        cv2.imshow("Raspberry Pi Camera - Object Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Interrupted by user.")

finally:
    picam2.close()
    arduino.close()
    cv2.destroyAllWindows()
    print("Cleaned up camera and serial.")
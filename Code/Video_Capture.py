import cv2
import time
from picamera2 import Picamera2

# Initialize PiCamera2
picam2 = Picamera2()

# Configure preview
picam2.preview_configuration.main.size = (640, 480)  # You can change this to (400, 240) if needed
picam2.preview_configuration.main.format = "BGR888"
picam2.configure("preview")
picam2.start()

time.sleep(0.5)  # Allow camera to warm up

print("Camera connected successfully.")

try:
    while True:
        start_time = time.time()

        # Capture frame
        frame = picam2.capture_array()

        # Display frame
        cv2.imshow("original", frame)

        # Calculate FPS
        end_time = time.time()
        fps = 1.0 / (end_time - start_time)
        print(f"FPS = {int(fps)}")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print("Error:", e)

finally:
    cv2.destroyAllWindows()
    picam2.stop()
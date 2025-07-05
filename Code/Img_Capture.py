from picamera2 import Picamera2
import cv2
import time
import os

# Setup save directory
save_dir = "captured_images"
os.makedirs(save_dir, exist_ok=True)

# Initialize PiCamera2
picam2 = Picamera2()
picam2.preview_configuration.main.size = (400, 240)
picam2.preview_configuration.main.format = "BGR888"
picam2.configure("preview")
picam2.start()

frame_count = 0

print("Press 's' to save image, 'q' to quit.")

while True:
    start = time.time()
    frame = picam2.capture_array()
    end = time.time()
    
    fps = int(1 / (end - start)) if end != start else 0
    print("FPS =", fps)

    cv2.imshow("Original", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):
        filename = os.path.join(save_dir, f"image_{frame_count}.jpg")
        cv2.imwrite(filename, frame)
        print(f"Saved: {filename}")
        frame_count += 1
    elif key == ord('q'):
        break

cv2.destroyAllWindows()
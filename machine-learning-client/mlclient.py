import os
import time
import cv2
from classifier import classify_frame, _create_landmarker
from db import save_result  # not created yet


def main():
    interval = float(os.environ.get("INTERVAL", 2.0))
    cap = cv2.VideoCapture(0)
    landmarker = _create_landmarker()

    try:
        while True:
            ret, frame = cap.read()
            if ret:
                gesture, _ = classify_frame(frame, landmarker)

                if gesture in ("rock", "paper", "scissors"):
                    _, buffer = cv2.imencode(".jpg", frame)
                    save_result(buffer.tobytes(), gesture, time.time())

            time.sleep(interval)

    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        landmarker.close()


if __name__ == "__main__":
    main()

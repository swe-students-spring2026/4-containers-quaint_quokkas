import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np


# Source for parts of the code and inspiration: https://medium.com/@susanne.thierfelder/head-pose-estimation-with-mediapipe-and-opencv-in-javascript-c87980df3acb
def analyze_vision(video_path):
    base_options = python.BaseOptions(model_asset_path="face_landmarker.task")
    options = vision.FaceLandmarkerOptions(base_options=base_options, num_faces=1)

    with vision.FaceLandmarker.create_from_options(options) as detector:
        model_points = np.array(
            [
                (0.0, 0.0, 0.0),  # Nose tip
                (0.0, 330.0, -65.0),  # Chin
                (-225.0, -170.0, -135.0),  # Left eye corner
                (225.0, -170.0, -135.0),  # Right eye corner
                (-150.0, 150.0, -125.0),  # Left mouth corner
                (150.0, 150.0, -125.0),  # Right mouth corner
            ],
            dtype=np.float64,
        )

        cap = cv2.VideoCapture(video_path)
        total, looking = 0, 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            total += 1
            img_h, img_w, _ = frame.shape

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
            )
            results = detector.detect(mp_image)

            if results.face_landmarks:
                lm = results.face_landmarks[0]
                image_points = np.array(
                    [
                        (lm[1].x * img_w, lm[1].y * img_h),  # Nose tip
                        (lm[152].x * img_w, lm[152].y * img_h),  # Chin
                        (lm[33].x * img_w, lm[33].y * img_h),  # Left eye
                        (lm[263].x * img_w, lm[263].y * img_h),  # Right eye
                        (lm[61].x * img_w, lm[61].y * img_h),  # Left mouth
                        (lm[291].x * img_w, lm[291].y * img_h),  # Right mouth
                    ],
                    dtype=np.float64,
                )

                camera_matrix = np.array(
                    [[img_w, 0, img_w / 2], [0, img_w, img_h / 2], [0, 0, 1]],
                    dtype="double",
                )

                # Calculate head pose
                success, rvec, _ = cv2.solvePnP(
                    model_points, image_points, camera_matrix, np.zeros((4, 1))
                )

                if success:
                    rmat, _ = cv2.Rodrigues(rvec)
                    angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

                    pitch = angles[0]
                    yaw = angles[1]

                    if abs(pitch) < 15.0 and abs(yaw) < 15.0:
                        looking += 1

        cap.release()

    if total == 0:
        return {}

    pct = (looking / total) * 100

    return {
        "total_frames": total,
        "looking_frames": looking,
        "eye_contact_score": round(pct, 2),
        "feedback": "Excellent" if pct >= 85 else "Good" if pct >= 65 else "Needs work",
    }

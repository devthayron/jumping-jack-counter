import math

import cv2 as cv
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import PoseLandmarksConnections

from config import (
    ARM_CLOSED_THRESHOLD,
    ARM_OPEN_THRESHOLD,
    FOOT_CLOSED_THRESHOLD,
    FOOT_OPEN_THRESHOLD,
    MODEL_PATH,
    NUM_POSES,
)


def create_pose_landmarker():
    """Cria e configura o detector de pose do MediaPipe."""
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)

    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_poses=NUM_POSES,
    )

    return vision.PoseLandmarker.create_from_options(options)


def calculate_angle(hip, shoulder, wrist):
    """Calcula o ângulo do braço entre o quadril, ombro e punho."""
    angle = math.degrees(
        math.atan2(
            wrist.y - shoulder.y,
            wrist.x - shoulder.x,
        )
        - math.atan2(
            hip.y - shoulder.y,
            hip.x - shoulder.x,
        )
    )

    angle = abs(angle)

    if angle > 180:
        angle = 360 - angle

    return angle


def calculate_metrics(landmarks):
    """Calcula as métricas utilizadas para identificar o movimento do polichinelo."""
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]

    left_hip = landmarks[23]
    right_hip = landmarks[24]

    left_wrist = landmarks[15]
    right_wrist = landmarks[16]

    left_foot = landmarks[31]
    right_foot = landmarks[32]

    # Calcula o ângulo médio dos braços.
    left_arm_angle = calculate_angle(left_hip, left_shoulder, left_wrist)
    right_arm_angle = calculate_angle(right_hip, right_shoulder, right_wrist)

    arm_angle = (left_arm_angle + right_arm_angle) / 2

    hip_distance = math.hypot(right_hip.x - left_hip.x, right_hip.y - left_hip.y)

    foot_distance = math.hypot(right_foot.x - left_foot.x, right_foot.y - left_foot.y)

    foot_ratio = foot_distance / hip_distance if hip_distance > 0 else 0

    nose = landmarks[0]

    hands_above = left_wrist.y < nose.y and right_wrist.y < nose.y

    return arm_angle, foot_ratio, hands_above


def is_open(arm_angle, foot_ratio, hands_above):
    """
    Verifica se a pessoa está na posição `open`,
    com braços abertos e pernas afastadas.
    """
    return (
        arm_angle >= ARM_OPEN_THRESHOLD
        and foot_ratio >= FOOT_OPEN_THRESHOLD
        and hands_above
    )


def is_closed(arm_angle, foot_ratio):
    """
    Verifica se a pessoa está na posição `closed`,
    com braços fechados e pernas próximas.
    """
    return arm_angle <= ARM_CLOSED_THRESHOLD and foot_ratio <= FOOT_CLOSED_THRESHOLD


def update_counter(arm_angle, foot_ratio, hands_above, count, state):
    """Atualiza o estado e contabiliza as repetições do polichinelo."""
    if state == "closed" and is_open(arm_angle, foot_ratio, hands_above):
        state = "open"

    elif state == "open" and is_closed(arm_angle, foot_ratio):
        count += 1
        state = "closed"

    return count, state


def draw_landmarks(frame, landmarks):
    """Desenha os pontos e conexões da pose no frame."""
    height, width, _ = frame.shape

    for landmark in landmarks:
        x = int(landmark.x * width)
        y = int(landmark.y * height)

        cv.circle(frame, (x, y), 4, (0, 255, 0), -1)

    for connection in PoseLandmarksConnections.POSE_LANDMARKS:
        start = landmarks[connection.start]
        end = landmarks[connection.end]

        start_point = (int(start.x * width), int(start.y * height))
        end_point = (int(end.x * width), int(end.y * height))

        cv.line(frame, start_point, end_point, (0, 255, 0), 2)


def create_video_writer(video, output_path):
    """Cria o gravador do vídeo de saída."""
    fps = video.get(cv.CAP_PROP_FPS)

    if fps <= 0:
        fps = 30

    width = int(video.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv.VideoWriter_fourcc(*"mp4v")

    return cv.VideoWriter(output_path, fourcc, fps, (width, height))

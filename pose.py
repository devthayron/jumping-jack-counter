import math

import cv2 as cv
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from config import (
    FOOT_THRESHOLD,
    HAND_THRESHOLD,
    LEFT_FOOT_INDEX,
    LEFT_INDEX,
    LEFT_SHOULDER,
    MODEL_PATH,
    NUM_POSES,
    RIGHT_FOOT_INDEX,
    RIGHT_INDEX,
    RIGHT_SHOULDER,
)


def create_pose_landmarker():
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)

    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_poses=NUM_POSES,
    )

    return vision.PoseLandmarker.create_from_options(options)


def calculate_distances(landmarks):
    right_shoulder = landmarks[RIGHT_SHOULDER]
    left_shoulder = landmarks[LEFT_SHOULDER]

    right_hand = landmarks[RIGHT_INDEX]
    left_hand = landmarks[LEFT_INDEX]

    right_foot = landmarks[RIGHT_FOOT_INDEX]
    left_foot = landmarks[LEFT_FOOT_INDEX]

    shoulder_distance = math.hypot(
        right_shoulder.x - left_shoulder.x,
        right_shoulder.y - left_shoulder.y,
    )

    hand_distance = math.hypot(
        right_hand.x - left_hand.x,
        right_hand.y - left_hand.y,
    )

    foot_distance = math.hypot(
        right_foot.x - left_foot.x,
        right_foot.y - left_foot.y,
    )

    return shoulder_distance, hand_distance, foot_distance


def update_counter(
    hand_ratio,
    foot_ratio,
    count,
    ready_to_count,
):
    if hand_ratio <= HAND_THRESHOLD and foot_ratio >= FOOT_THRESHOLD and ready_to_count:
        ready_to_count = False

    elif (
        hand_ratio >= HAND_THRESHOLD
        and foot_ratio <= FOOT_THRESHOLD
        and not ready_to_count
    ):
        count += 1
        ready_to_count = True

    return count, ready_to_count


def draw_landmarks(frame, landmarks):
    height, width, _ = frame.shape

    for landmark in landmarks:
        x = int(landmark.x * width)
        y = int(landmark.y * height)

        cv.circle(frame, (x, y), 4, (0, 255, 0), -1)

    connections = [
        (11, 12),
        (11, 13),
        (13, 15),
        (12, 14),
        (14, 16),
        (11, 23),
        (12, 24),
        (23, 24),
        (23, 25),
        (25, 27),
        (24, 26),
        (26, 28),
        (27, 31),
        (28, 32),
    ]

    for start, end in connections:
        start_point = landmarks[start]
        end_point = landmarks[end]

        start_x = int(start_point.x * width)
        start_y = int(start_point.y * height)

        end_x = int(end_point.x * width)
        end_y = int(end_point.y * height)

        cv.line(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)


def create_video_writer(video, output_path):
    fps = video.get(cv.CAP_PROP_FPS)

    if fps <= 0:
        fps = 30

    width = int(video.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv.VideoWriter_fourcc(*"mp4v")

    return cv.VideoWriter(output_path, fourcc, fps, (width, height))

import cv2 as cv
import mediapipe as mp

from config import VIDEO_PATH_INPUT, VIDEO_PATH_OUTPUT
from pose import (
    calculate_metrics,
    create_pose_landmarker,
    create_video_writer,
    draw_landmarks,
    update_counter,
)


def open_video(video_path):
    video = cv.VideoCapture(video_path)

    if not video.isOpened():
        raise RuntimeError(f"Não foi possível abrir o vídeo: {video_path}")

    return video


def process_frame(frame, pose_landmarker, frame_index, fps, count, state):
    """
    Processa um frame, detecta a pose e atualiza a contagem.
    """
    timestamp_ms = int(frame_index * 1000 / fps)

    frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

    result = pose_landmarker.detect_for_video(mp_image, timestamp_ms)

    if not result.pose_landmarks:
        return frame, count, state

    landmarks = result.pose_landmarks[0]

    arm_angle, foot_ratio, hands_above = calculate_metrics(landmarks)

    count, state = update_counter(arm_angle, foot_ratio, hands_above, count, state)

    debug = (
        f"braço: {arm_angle:.1f} | "
        f"pernas: {foot_ratio:.2f} | "
        f"mãos acima: {hands_above} | "
        f"estado: {state}"
    )

    print(debug)

    draw_landmarks(frame, landmarks)

    return frame, count, state


def draw_counter(frame, count, state):
    """Exibe a quantidade de repetições e o estado atual no frame."""
    cv.putText(
        frame, f"QTD: {count}", (50, 100), cv.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5
    )

    cv.putText(
        frame,
        f"STATUS: {state.upper()}",
        (50, 160),
        cv.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 0, 0),
        3,
    )


def main():
    pose_landmarker = create_pose_landmarker()

    video = open_video(VIDEO_PATH_INPUT)
    output = create_video_writer(video, VIDEO_PATH_OUTPUT)

    fps = video.get(cv.CAP_PROP_FPS)

    if fps <= 0:
        fps = 30

    delay = int(1000 / fps)

    frame_index = 0
    count = 0
    state = "closed"

    while True:
        success, frame = video.read()

        if not success:
            break

        frame, count, state = process_frame(
            frame, pose_landmarker, frame_index, fps, count, state
        )

        frame_index += 1

        draw_counter(frame, count, state)

        output.write(frame)

        cv.imshow("Contador de Polichinelos", frame)

        if cv.waitKey(delay) & 0xFF == ord("q"):
            break

    video.release()
    output.release()
    pose_landmarker.close()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()

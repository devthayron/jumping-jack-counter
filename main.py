import cv2 as cv
import mediapipe as mp

from config import VIDEO_PATH_INPUT, VIDEO_PATH_OUTPUT
from pose import (
    calculate_distances,
    create_pose_landmarker,
    create_video_writer,
    draw_landmarks,
    update_counter,
)


def main():
    pose_landmarker = create_pose_landmarker()

    video = cv.VideoCapture(VIDEO_PATH_INPUT)

    if not video.isOpened():
        pose_landmarker.close()
        raise RuntimeError(f"Não foi possível abrir o vídeo: {VIDEO_PATH_INPUT}")

    output = create_video_writer(video, VIDEO_PATH_OUTPUT)

    fps = video.get(cv.CAP_PROP_FPS)

    if fps <= 0:
        fps = 30

    delay = int(1000 / fps)
    frame_index = 0
    count = 0
    ready_to_count = True

    while True:
        success, frame = video.read()

        if not success:
            break

        timestamp_ms = int(frame_index * 1000 / fps)

        frame_index += 1

        frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        result = pose_landmarker.detect_for_video(mp_image, timestamp_ms)

        if result.pose_landmarks:
            landmarks = result.pose_landmarks[0]

            (
                shoulder_distance,
                hand_distance,
                foot_distance,
            ) = calculate_distances(landmarks)

            if shoulder_distance > 0:
                hand_ratio = hand_distance / shoulder_distance

                foot_ratio = foot_distance / shoulder_distance

                count, ready_to_count = update_counter(
                    hand_ratio, foot_ratio, count, ready_to_count
                )

                # debug
                # print(f"maos: {hand_ratio:.2f} pes: {foot_ratio:.2f}")

            draw_landmarks(frame, landmarks)

        cv.putText(
            frame,
            f"QTD: {count}",
            (50, 200),
            cv.FONT_HERSHEY_SIMPLEX,
            2,
            (255, 0, 0),
            5,
        )

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

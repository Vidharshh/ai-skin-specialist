from dataclasses import dataclass
from pathlib import Path

import imageio_ffmpeg
from PIL import Image


MAX_VIDEO_DURATION_SECONDS = 60
MAX_VIDEO_FILE_BYTES = 100 * 1024 * 1024
MAX_FRAME_DIMENSION = 1024


class VideoProcessingError(ValueError):
    pass


@dataclass(frozen=True)
class VideoFrame:
    path: Path
    timestamp_seconds: float


def extract_video_frames(video_filepath, output_directory, max_frames=3):
    video_path = Path(video_filepath)
    if not video_path.is_file():
        raise VideoProcessingError("The uploaded video could not be found.")
    if video_path.stat().st_size > MAX_VIDEO_FILE_BYTES:
        raise VideoProcessingError("Please upload a video smaller than 100 MB.")
    if max_frames < 1:
        raise ValueError("max_frames must be at least 1")

    try:
        probe = imageio_ffmpeg.read_frames(str(video_path))
        try:
            metadata = next(probe)
        finally:
            probe.close()
    except Exception as error:
        raise VideoProcessingError("The uploaded video could not be read. Try an MP4, MOV, or WebM file.") from error

    duration = float(metadata.get("duration") or 0)
    if duration <= 0:
        raise VideoProcessingError("The video duration could not be determined.")
    if duration > MAX_VIDEO_DURATION_SECONDS:
        raise VideoProcessingError("Please upload a video that is 60 seconds or shorter.")

    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)
    frame_times = [duration * (index + 1) / (max_frames + 1) for index in range(max_frames)]
    extracted_frames = []

    for index, timestamp in enumerate(frame_times, start=1):
        reader = imageio_ffmpeg.read_frames(
            str(video_path),
            input_params=["-ss", f"{timestamp:.3f}"],
            output_params=[
                "-frames:v", "1",
                "-vf", f"scale={MAX_FRAME_DIMENSION}:{MAX_FRAME_DIMENSION}:force_original_aspect_ratio=decrease",
            ],
        )
        try:
            frame_metadata = next(reader)
            raw_frame = next(reader)
        except StopIteration:
            continue
        except Exception as error:
            raise VideoProcessingError("A frame could not be extracted from the uploaded video.") from error
        finally:
            reader.close()

        width, height = frame_metadata["size"]
        frame_image = Image.frombytes("RGB", (width, height), raw_frame)
        frame_path = output_path / f"video-frame-{index}.jpg"
        frame_image.save(frame_path, format="JPEG", quality=75)
        extracted_frames.append(VideoFrame(path=frame_path, timestamp_seconds=timestamp))

    if not extracted_frames:
        raise VideoProcessingError("No readable frames were found in the uploaded video.")

    return extracted_frames

from pathlib import Path
import re

from agents.vision_agent import brain_of_the_doctor
from rag.retriever import retrieve_knowledge
from services.speech_to_text import transcribe_patient_voice
from services.text_to_speech import convert_text_to_doctor_audio
from services.video_processing import extract_video_frames


def run_consultation(audio_filepath, image_filepath, video_filepath, output_audio_filepath=None):
    patient_text = transcribe_patient_voice(audio_filepath)
    references = retrieve_knowledge(patient_text, limit=3)
    visual_paths = []
    frame_timestamps = []

    if image_filepath:
        visual_paths.append(image_filepath)
        frame_timestamps.append(None)

    if video_filepath:
        available_frames = 3 - len(visual_paths)
        frames = extract_video_frames(
            video_filepath,
            Path(video_filepath).parent / "video-frames",
            max_frames=available_frames,
        )
        visual_paths.extend(str(frame.path) for frame in frames)
        frame_timestamps.extend(frame.timestamp_seconds for frame in frames)

    if not visual_paths:
        raise ValueError("Please upload a skin image or video before analysis.")

    doctor_text = brain_of_the_doctor(
        patient_text=patient_text,
        image_filepaths=visual_paths,
        frame_timestamps=frame_timestamps,
        knowledge_context=references,
    )
    speech_text = re.sub(r"\s*\[\d+\]", "", doctor_text).strip()
    if output_audio_filepath is None:
        doctor_audio = convert_text_to_doctor_audio(speech_text)
    else:
        doctor_audio = convert_text_to_doctor_audio(speech_text, output_filepath=output_audio_filepath)

    sources = [
        {"title": reference["title"], "source": reference["source"], "source_url": reference["source_url"]}
        for reference in references
    ]
    return patient_text, doctor_text, str(Path(doctor_audio)), sources

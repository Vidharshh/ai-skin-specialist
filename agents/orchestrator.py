from pathlib import Path

from agents.vision_agent import brain_of_the_doctor
from services.speech_to_text import transcribe_patient_voice
from services.text_to_speech import convert_text_to_doctor_audio


def run_consultation(audio_filepath, image_filepath, video_filepath):
    patient_text = transcribe_patient_voice(audio_filepath)
    doctor_text = brain_of_the_doctor(
        patient_text=patient_text,
        image_filepath=image_filepath,
        video_filepath=video_filepath,
    )
    doctor_audio = convert_text_to_doctor_audio(doctor_text)

    return patient_text, doctor_text, str(Path(doctor_audio))

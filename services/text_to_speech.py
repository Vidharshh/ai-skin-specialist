# Step1: Create API keys

# Step2: Create Client and send request
from deepgram import DeepgramClient
import os
from pathlib import Path
from config import settings

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DOCTOR_AUDIO = BASE_DIR / "outputs" / "doctor_response.mp3"
def convert_text_to_doctor_audio(text, output_filepath=DEFAULT_DOCTOR_AUDIO):
    deepgram_api_key = settings.deepgram_api_key
    if not deepgram_api_key:
        raise ValueError("Missing DEEPGRAM_API_KEY in .env or environment")
    deepgram = DeepgramClient(api_key=deepgram_api_key)
    audio = deepgram.speak.v1.audio.generate(
        text=text,
        model=settings.deepgram_tts_model,
        encoding="mp3",
    )

    output_filepath = Path(output_filepath)
    output_filepath.parent.mkdir(parents=True, exist_ok=True)
    with output_filepath.open("wb") as file:
        for chunk in audio:
            file.write(chunk)

    return output_filepath

import subprocess
import platform
def play_audio(audio_filepath):
    audio_filepath = str(audio_filepath)

    if platform.system() == "Darwin":
        subprocess.run(["afplay", audio_filepath], check=False)
    elif platform.system() == "Windows":
        os.startfile(audio_filepath)
    else:
        subprocess.run(["xdg-open", audio_filepath], check=False)


"""text = "Hi, my name is AI with Hassan, who are you?. I am very happy."
api_key = settings.deepgram_api_key
deepgram = DeepgramClient(api_key=api_key)
audio = deepgram.speak.v1.audio.generate(
    text=text,
    model="aura-2-thalia-en",
    encoding="mp3",
)
# Step3: Save audio
from pathlib import Path

audio_file="test-output.mp3"
audio_path = Path(__file__).with_name(audio_file)
with audio_path.open("wb") as file:
    for chunk in audio:
        file.write(chunk)

# Step4: Play audio
import platform
import subprocess


if platform.system() == "Darwin":  # macOS
    subprocess.run(["afplay", str(audio_path)])
elif platform.system() == "Windows":
    os.startfile(audio_path)
else:  # Linux
    subprocess.run(["xdg-open", str(audio_path)])"""



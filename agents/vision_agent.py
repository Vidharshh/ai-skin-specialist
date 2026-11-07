import os

from dotenv import load_dotenv
from groq import Groq

from services.image_processing import encode_image_for_groq


load_dotenv()


def brain_of_the_doctor(patient_text, image_filepaths, frame_timestamps=None):
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("Missing GROQ_API_KEY in .env or environment")
    if not image_filepaths:
        raise ValueError("Please upload a skin image or video before analysis.")
    if len(image_filepaths) > 3:
        raise ValueError(
            "The current Groq vision model accepts up to three images per request."
        )

    frame_timestamps = frame_timestamps or [None] * len(image_filepaths)
    if len(frame_timestamps) != len(image_filepaths):
        raise ValueError("Each visual input must have a matching timestamp entry.")

    visual_descriptions = []
    for index, timestamp in enumerate(frame_timestamps, start=1):
        if timestamp is None:
            visual_descriptions.append(f"Visual {index}: uploaded still image")
        else:
            visual_descriptions.append(
                f"Visual {index}: video frame at approximately {timestamp:.1f} seconds"
            )

    prompt = (
        "You are a careful skin care assistant. Give general information, not a "
        "diagnosis. Keep the response to two or three sentences. Do not claim that "
        "an image proves a diagnosis. Do not use markdown because the response will "
        "be converted to speech.\n\n"
        f"Patient description: {patient_text}\n\n"
        "Review the provided skin image or video frames. Describe visible features "
        "cautiously. These are still images, including sampled video frames; do not "
        "infer movement or events between frames.\n\n"
        + "\n".join(visual_descriptions)
    )

    image_data = [
        encode_image_for_groq(filepath) for filepath in image_filepaths
    ]

    message_content = [{"type": "text", "text": prompt}]
    message_content.extend(
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
        }
        for encoded_image in image_data
    )

    client = Groq(api_key=groq_api_key)
    response = client.chat.completions.create(
        model=os.environ.get("GROQ_MODEL", "qwen/qwen3.8-27b"),
        max_completion_tokens=1000,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful skin care assistant. Provide general "
                    "information, not a medical diagnosis."
                ),
            },
            {"role": "user", "content": message_content},
        ],
    )

    return response.choices[0].message.content
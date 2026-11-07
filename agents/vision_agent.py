from groq import Groq

from config import settings

from services.image_processing import encode_image_for_groq



def brain_of_the_doctor(
    patient_text, image_filepaths, frame_timestamps=None, knowledge_context=None
):
    groq_api_key = settings.groq_api_key
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

    reference_lines = []
    for index, reference in enumerate(knowledge_context or [], start=1):
        reference_lines.append(
            f"[{index}] {reference['title']} — {reference['source']}: "
            f"{reference['text']}"
        )
    reference_context = ""
    if reference_lines:
        reference_context = (
            "\n\nTrusted reference notes (general educational information only):\n"
            + "\n".join(reference_lines)
            + "\nUse these notes only when directly relevant. Do not treat them as a diagnosis. "
            "When a sentence relies on a note, add its bracketed source number, such as [1]."
        )

    prompt = (
        "You are a careful skin care assistant. Give general information, not a "
        "diagnosis. Keep the response to a few concise sentences. Do not claim that "
        "an image proves a diagnosis. Do not use markdown because the response will "
        "be converted to speech.\n\n"
        f"Patient description: {patient_text}\n\n"
        "Review the provided skin image or video frames. Describe visible features "
        "cautiously. These are still images, including sampled video frames; do not "
        "infer movement or events between frames.\n\n"
        + "\n".join(visual_descriptions)
        + reference_context
    )

    image_data = [encode_image_for_groq(filepath) for filepath in image_filepaths]
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
        model=settings.groq_model,
        max_completion_tokens=1000,
        messages=[
            {
                "role": "system",
                "content": (
                    "You provide general skin health information, not medical care. Do not "
                    "diagnose, rank likely conditions, or identify a condition from an image. "
                    "Describe only visible features; do not infer texture, pain, warmth, duration, "
                    "or change over time from an image. If uncertain, say so. Do not promise a "
                    "mark or scar can be removed, and do not recommend a specific procedure or "
                    "treatment based only on an image. For questions about treating or removing "
                    "a mark, recommend an in-person dermatologist or clinician assessment before "
                    "choosing treatment. If the patient reports fever or chills together with "
                    "painful, red, tender skin, recommend prompt clinical assessment. If the "
                    "patient reports trouble breathing or swelling of the face or throat, advise "
                    "calling local emergency services immediately. For severe or rapidly worsening "
                    "symptoms, advise seeking urgent local medical care. "
                    "Use retrieved reference notes only when they directly support general "
                    "information, and cite those notes by their bracketed numbers."
                ),
            },
            {"role": "user", "content": message_content},
        ],
    )

    return response.choices[0].message.content

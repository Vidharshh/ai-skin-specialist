from pydantic import BaseModel


class ConsultationResponse(BaseModel):
    transcript: str
    guidance: str
    audio_base64: str
    audio_content_type: str = "audio/mpeg"

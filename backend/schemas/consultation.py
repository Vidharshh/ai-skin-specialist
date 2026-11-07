from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    title: str
    source: str
    source_url: str


class ConsultationResponse(BaseModel):
    transcript: str
    guidance: str
    audio_base64: str
    audio_content_type: str = "audio/mpeg"
    sources: list[SourceReference] = Field(default_factory=list)

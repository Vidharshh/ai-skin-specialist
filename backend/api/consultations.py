from base64 import b64encode
import logging
from pathlib import Path
from shutil import copyfileobj
from tempfile import TemporaryDirectory

from fastapi import APIRouter, File, HTTPException, UploadFile

from agents.orchestrator import run_consultation
from backend.schemas.consultation import ConsultationResponse
from services.video_processing import VideoProcessingError


logger = logging.getLogger(__name__)
router = APIRouter(tags=["consultations"])


def _save_upload(upload: UploadFile, directory: Path, name: str) -> Path:
    suffix = Path(upload.filename or "").suffix
    destination = directory / f"{name}{suffix}"
    with destination.open("wb") as saved_file:
        copyfileobj(upload.file, saved_file)
    return destination


@router.post("/consultations", response_model=ConsultationResponse)
def create_consultation(
    audio: UploadFile = File(...),
    image: UploadFile | None = File(default=None),
    video: UploadFile | None = File(default=None),
):
    if image is None and video is None:
        raise HTTPException(status_code=400, detail="Upload a skin image or video.")

    with TemporaryDirectory(prefix="skin-consultation-") as temporary_directory:
        work_directory = Path(temporary_directory)
        audio_path = _save_upload(audio, work_directory, "patient-audio")
        image_path = _save_upload(image, work_directory, "skin-image") if image else None
        video_path = _save_upload(video, work_directory, "skin-video") if video else None
        response_audio_path = work_directory / "doctor-response.mp3"

        try:
            transcript, guidance, generated_audio_path = run_consultation(
                str(audio_path),
                str(image_path) if image_path else None,
                str(video_path) if video_path else None,
                output_audio_filepath=response_audio_path,
            )
            audio_bytes = Path(generated_audio_path).read_bytes()
        except VideoProcessingError as error:
            logger.info("Video upload rejected: %s", error)
            raise HTTPException(status_code=400, detail=str(error)) from error
        except Exception as error:
            logger.exception("Consultation processing failed")
            raise HTTPException(
                status_code=502,
                detail=f"Consultation failed ({type(error).__name__}). Check the backend terminal for details.",
            ) from error

    return ConsultationResponse(
        transcript=transcript,
        guidance=guidance,
        audio_base64=b64encode(audio_bytes).decode("ascii"),
    )

import logging
import re

import requests

from kog_ace_step import __version__
from kog_ace_step.api import ACEStepInput
from kog_ace_step.constants import MUSIC_PORT, MUSIC_URL

logger = logging.getLogger(__name__)


def generate_song(
    prompt: str,
    music_url: str = MUSIC_URL,
    music_port: str = MUSIC_PORT,
    **cfg,
):
    # Construct the full URL
    full_url = f"http://{music_url}:{music_port}/generate"
    raw_payload = {"prompt": prompt, "version": __version__, **cfg}
    gen_request_cfg = ACEStepInput(**raw_payload)
    payload = gen_request_cfg.model_dump(mode="json")

    try:
        response = requests.post(full_url, json=payload)

        if response.status_code == 200:
            audio_data = response.content
            filename = None
            content_disposition = response.headers.get("Content-Disposition")
            if content_disposition:
                # Extract filename from Content-Disposition header
                # e.g., attachment; filename="output.wav"
                filename_match = re.search(r'filename="?([^"]+)"?', content_disposition)
                if filename_match:
                    filename = filename_match.group(1)
            return {"filename": filename, "audio_data": audio_data}
    except requests.exceptions.RequestException as e:
        logger.info(f"Request to Music API failed: {e}")
        return {}

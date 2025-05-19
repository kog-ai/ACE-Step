from typing import List, Optional
from pydantic import BaseModel

from kog_ace_step import __version__

class ACEStepInput(BaseModel):
    __version__ = __version__
    
    checkpoint_path: Optional[str] = None
    bf16: bool = True
    torch_compile: bool = False
    device_id: int = 0
    output_path: Optional[str] = None
    audio_duration: float = 30
    prompt: str
    lyrics: str = "[instrumental]\n"
    infer_step: int = 60
    guidance_scale: float = 15
    scheduler_type: str = "euler"
    cfg_type: str = "apg"
    omega_scale: float = 10
    actual_seeds: Optional[List[int]] = None
    guidance_interval: float = 0.5
    guidance_interval_decay: float = 0.0
    min_guidance_scale: float = 3.0
    use_erg_tag: bool = True
    use_erg_lyric: bool = False
    use_erg_diffusion: bool = True
    oss_steps: Optional[List[int]] = None
    guidance_scale_text: float = 0.0
    guidance_scale_lyric: float = 0.0


class ACEStepOutput(BaseModel):
    status: str
    output_path: Optional[str]
    message: str

import logging
import os
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from acestep.pipeline_ace_step import ACEStepPipeline
from kog_ace_step.api import ACEStepInput
from kog_ace_step.constants import MUSIC_PORT, MUSIC_URL
from kog_ace_step.logging import setup_logging

logger = setup_logging(root=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run at startup
    logger.info("Starting up the application...")
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    app.pipeline = ACEStepPipeline(
        checkpoint_dir="checkpoints",
        dtype="bfloat16",
        torch_compile=False,
    )
    yield
    # Code to run at shutdown
    logger.info("Shutting down the application...")


app = FastAPI(title="ACEStep Pipeline API", lifespan=lifespan)


@app.post("/generate")
async def generate_audio(input_data: ACEStepInput):
    try:
        # Initialize pipeline
        model_demo: ACEStepPipeline = app.pipeline
        actual_seeds = oss_steps = None
        if input_data.actual_seeds is not None:
            actual_seeds = ", ".join(map(str, input_data.actual_seeds))
        if input_data.oss_steps is not None:
            oss_steps = ", ".join(map(str, input_data.oss_steps))
        # Prepare parameters
        params = {
            "audio_duration": input_data.audio_duration,
            "prompt": input_data.prompt,
            "lyrics": input_data.lyrics,
            "infer_step": input_data.infer_step,
            "guidance_scale": input_data.guidance_scale,
            "scheduler_type": input_data.scheduler_type,
            "cfg_type": input_data.cfg_type,
            "omega_scale": input_data.omega_scale,
            "manual_seeds": actual_seeds,
            "guidance_interval": input_data.guidance_interval,
            "guidance_interval_decay": input_data.guidance_interval_decay,
            "min_guidance_scale": input_data.min_guidance_scale,
            "use_erg_tag": input_data.use_erg_tag,
            "use_erg_lyric": input_data.use_erg_lyric,
            "use_erg_diffusion": input_data.use_erg_diffusion,
            "oss_steps": oss_steps,
            "guidance_scale_text": input_data.guidance_scale_text,
            "guidance_scale_lyric": input_data.guidance_scale_lyric,
        }

        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        output_filename = f"output_{uuid.uuid4().hex}.wav"
        output_path = input_data.output_path or os.path.join(output_dir, output_filename)

        # Run pipeline
        model_demo(save_path=output_path, **params)

        if not os.path.exists(output_path):
            raise HTTPException(status_code=404, detail="Generated file not found.")

        return FileResponse(path=output_path, media_type="audio/wav", filename=os.path.basename(output_path))

    except Exception as e:
        logger.error(f"Error generating audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=MUSIC_URL, port=MUSIC_PORT)

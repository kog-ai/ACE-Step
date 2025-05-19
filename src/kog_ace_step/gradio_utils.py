import logging
import os

import gradio as gr

from kog_ace_step.client_utils import generate_song

logger = logging.getLogger(__name__)


def generate(prompt: str, duration, guidance_scale, guidance_interval, lyrics: str, tmp_dir: str, req: gr.Request):
    data = generate_song(
        prompt=prompt,
        duration=duration,
        guidance_scale=guidance_scale,
        guidance_interval=guidance_interval,
        lyrics=lyrics,
    )
    user_dir = os.path.join(tmp_dir, str(req.session_hash))
    full_output_path = os.path.join(user_dir, "sample.wav")

    with open(full_output_path, "wb") as out_file:
        out_file.write(data["audio_data"])
    return full_output_path


def create_music_interface(tmp_dir: str):
    """
    Create a Gradio interface for the music generation model.

    Args:
        tmp_dir (str): Path to the temporary directory for storing outputs.

    Returns:
        gr.Interface: The Gradio interface object.
    """
    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column():
                prompt = gr.Textbox(label="Prompt", placeholder="Enter your prompt here...")
                lyrics = gr.Textbox(label="Lyrics", value="[instrumental]\n")
                duration = gr.Number(label="Audio Duration (seconds)", value=30, precision=0)
                guidance_scale = gr.Number(label="Guidance Scale", value=15, precision=1)
                guidance_interval = gr.Number(label="Guidance Interval", value=0.5, precision=1)
                generate_button = gr.Button("Generate")
            with gr.Column():
                output_audio = gr.Audio(label="Generated Audio")

        def wrapper_generate(prompt, duration, guidance_scale, guidance_interval, lyrics, req: gr.Request):
            return generate(prompt, duration, guidance_scale, guidance_interval, lyrics, tmp_dir, req)

        generate_button.click(
            fn=wrapper_generate,
            inputs=[prompt, duration, guidance_scale, guidance_interval, lyrics],
            outputs=output_audio,
        )

    return demo

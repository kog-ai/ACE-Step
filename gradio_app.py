import logging
import os
import shutil

import gradio as gr

from kog_ace_step.gradio_utils import create_music_interface
from kog_ace_step.logging import setup_logging

logger = setup_logging()

MODULE_ABSPATH = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = os.path.join(MODULE_ABSPATH, "outputs", "tmp")
os.makedirs(TMP_DIR, exist_ok=True)


def get_tmp_user_dir(session_hash: str):
    return os.path.join(TMP_DIR, str(session_hash))


def start_session(req: gr.Request):
    logger.info(f"Starting session: {req.session_hash}")
    user_dir = get_tmp_user_dir(req.session_hash)
    os.makedirs(user_dir, exist_ok=True)


def end_session(req: gr.Request):
    logger.info(f"Ending session: {req.session_hash}")
    user_dir = get_tmp_user_dir(req.session_hash)
    if os.path.exists(user_dir):
        shutil.rmtree(user_dir)


with gr.Blocks() as demo:
    output_image = create_music_interface(TMP_DIR)

    demo.load(start_session)
    demo.unload(end_session)

if __name__ == "__main__":
    logging.info("Launching Gradio demo.")

    demo.launch(server_name="0.0.0.0")

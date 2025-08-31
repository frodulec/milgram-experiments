import os
import asyncio
from pathlib import Path
import ffmpeg
from io import BytesIO
from audio.tts import generate_tts
from utils.general import load_experiments
from loguru import logger
from models import Roles



def load_mp3(filename: str) -> BytesIO:
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File {filename} does not exist.")
    
    # Construct the full path to the file
    filepath = Path(filename)

    # Use ffmpeg to load the MP3 file and convert it to bytes
    try:
        out, _ = ffmpeg.input(str(filepath)).output('pipe:', format='mp3', codec='copy').run(capture_stdout=True, capture_stderr=True)
        return BytesIO(out) # Wrap the bytes in BytesIO
    except ffmpeg.Error as e:
        raise RuntimeError(f"Error loading MP3 file: {e.stderr.decode()}") from e
    except Exception as e:
        # Handle other potential exceptions from ffmpeg-python
        raise RuntimeError(f"Error loading MP3 file: {str(e)}") from e


async def generate_all_audios():
    """
    1. Load all conversations from the results folder
    2. For each conversation, generate the audio for each message
    """
    conversations = load_experiments()
    for conversation in conversations:
        for message in conversation["messages"]:
            try:
                await generate_tts(message["text"], Roles(message["speaker"]))
                logger.info(f"Generated audio for {message['speaker']}")
            except Exception as e:
                logger.error(f"Error generating audio for {message['speaker']}: {str(e)}")


if __name__ == "__main__":
    asyncio.run(generate_all_audios())
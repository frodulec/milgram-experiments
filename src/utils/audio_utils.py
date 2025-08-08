import os
from pathlib import Path
import ffmpeg
from io import BytesIO



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

if __name__ == "__main__":
    load_mp3("static/electric-shock-cut.mp3")
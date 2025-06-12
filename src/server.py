import io
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse, Response
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware

from loguru import logger

from typing import Tuple, List, Dict, Union
import json
import asyncio
import base64
from .utils.chat_utils import load_conversation_dictionary
from .utils.drawing_utils import resize_sprite, adjust_cloud
import tempfile
import os

                   
# Add TTS imports
from audio.tts import (
    generate_tts,
    tts_worker,
    playback_worker,
    trigger_next_playback,
)
from models import Roles


def draw_message_on_cloud(
    composite_image: Image.Image, message: str, tail_anchor: Tuple[int, int], flip=False
) -> None:
    """
    Draws the message on the cloud with proper text wrapping.
    """
    cloud = Image.open("static/cloud.png").convert("RGBA")
    cloud = resize_sprite(cloud, 0.15)
    if flip:
        cloud = cloud.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf", size=16
    )

    # Adjust the cloud and get wrapped text lines
    cloud, text_lines, line_spacing = adjust_cloud(cloud, message, font)

    # Position the cloud with bottom-left anchor or right-bottom anchor if flipped
    if flip:
        cloud_position = (
            tail_anchor[0] - cloud.size[0],
            tail_anchor[1] - cloud.size[1],
        )
    else:
        cloud_position = (tail_anchor[0], tail_anchor[1] - cloud.size[1])

    composite_image.paste(cloud, cloud_position, cloud)

    # Add text to the cloud
    draw = ImageDraw.Draw(composite_image)

    # Get cloud dimensions
    cloud_width, cloud_height = cloud.size

    # Calculate total text block height
    total_text_height = len(text_lines) * line_spacing

    CLOUD_OFFSET = -11  # because of the tail of the cloud

    start_y = cloud_position[1] + (cloud_height - total_text_height) // 2 + CLOUD_OFFSET

    for i, line in enumerate(text_lines):
        # Calculate bounding box for this specific line
        text_bbox = draw.textbbox((0, 0), line, font=font)
        text_width = text_bbox[2] - text_bbox[0]

        text_x = cloud_position[0] + (cloud_width - text_width) // 2
        text_y = start_y + (i * line_spacing)
        draw.text((text_x, text_y), line, font=font, fill="black")

    return None


def create_game_image(
    student_message: str | None = None,
    professor_message: str | None = None,
    learner_message: str | None = None,
    display_shock: bool = False,
) -> io.BytesIO:
    """
    Generates the game image by layering sprites on a background.
    Optionally adds a message in a cloud with proper text wrapping.
    """
    background = Image.open("static/background.jpg").convert("RGBA")
    professor_sprite = Image.open("static/professor_w.png").convert("RGBA")
    student_sprite = Image.open("static/student.png").convert("RGBA")
    learner_sprite = Image.open("static/learner.png").convert("RGBA")
    shock_sprite = Image.open("static/electricity.png").convert("RGBA")

    # make the sprites smaller
    professor_sprite = resize_sprite(professor_sprite, 0.58)
    # flip the professor sprite to face the student
    # professor_sprite = professor_sprite.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    student_sprite = resize_sprite(student_sprite, 0.15)
    learner_sprite = resize_sprite(learner_sprite, 1.1)
    shock_sprite = resize_sprite(shock_sprite, 0.05)

    # Create a new image canvas to paste everything on
    composite_image = background.copy()

    # 2. Add sprites to the background
    # The third argument is a mask that respects the PNG transparency
    composite_image.paste(professor_sprite, (630, 660), professor_sprite)
    composite_image.paste(student_sprite, (360, 660), student_sprite)
    composite_image.paste(learner_sprite, (673, 275), learner_sprite)

    # 3. Add a message in a cloud if a message is provided
    if student_message:
        draw_message_on_cloud(composite_image, student_message, (450, 670))

    if professor_message:
        draw_message_on_cloud(composite_image, professor_message, (650, 670), True)

    if learner_message:
        draw_message_on_cloud(composite_image, learner_message, (673, 275), True)

    if display_shock:
        composite_image.paste(shock_sprite, (673, 300), shock_sprite)

    # 4. Save the final image to an in-memory buffer
    img_buffer = io.BytesIO()
    composite_image.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    return img_buffer


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/game-view")
async def get_game_view(
    participant_message: str | None = Query(default=None, max_length=1000),
    professor_message: str | None = Query(default=None, max_length=1000),
    learner_message: str | None = Query(default=None, max_length=1000),
    display_shock: bool = False,
):
    """
    Endpoint to get the current game view with messages from both characters.
    - Student message: /game-view?student_message=Hello professor!
    - Professor message: /game-view?professor_message=Hello student!
    - Both: /game-view?student_message=Hello!&professor_message=Hi there!
    """
    # Generate the image with specific messages for each character
    image_buffer = create_game_image(participant_message, professor_message, learner_message, display_shock)
    return StreamingResponse(image_buffer, media_type="image/png")


async def generate_example_sequence(messages):
    for message in messages:
        yield f"data: {json.dumps({'type': 'message', **message})}\n\n"

    yield f"data: {json.dumps({'type': 'end'})}\n\n"


@app.get("/api/game-sequence-example")
async def game_sequence_example():
    messages = load_conversation_dictionary("conversation.json")
    
    return StreamingResponse(
        generate_example_sequence(messages),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        },
    )


@app.get("/api/game-sequence")
@app.post("/api/tts")
async def generate_tts_endpoint(request: dict):
    """Generate TTS audio for a message"""
    role = request.get("role")
    message = request.get("message", "")
    
    logger.info(f"Generating TTS for role: {role}, message: {message}")
    audio_data = await generate_tts(message, Roles(role))
    return StreamingResponse(
        BytesIO(audio_data.getvalue()),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "attachment; filename=tts.mp3"}
    )
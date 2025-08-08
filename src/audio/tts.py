from openai import OpenAI
import pygame
from io import BytesIO
from models import Roles
import asyncio
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
import hashlib
import os
from dotenv import load_dotenv


load_dotenv()
client = OpenAI()

playback_trigger = asyncio.Event()  # Add trigger for playback control
CACHE_DIR = "tts_cache"
os.makedirs(CACHE_DIR, exist_ok=True)



async def generate_tts(message: str, role: Roles) -> BytesIO:
    """
    Generate TTS audio data without playing it (for queue-based systems).

    Args:
        message: The text to convert to speech
        role: The character role

    Returns:
        BytesIO object containing the audio data
    """
    role_voices = {
        Roles.PROFESSOR: "alloy",
        Roles.PARTICIPANT: "verse",
        Roles.LEARNER: "echo",
    }

    role_instructions = {
        Roles.PROFESSOR: """
## Character: Experienced Scientist/Doctor

**Voice Affect:** Calm, composed, and reassuring; project quiet authority and confidence reminiscent of a seasoned physician or research scientist with decades of experience.

**Tone:** Sincere, empathetic, and gently authoritative—express genuine concern while conveying deep competence and reliability. Balance professional expertise with human warmth.

**Pacing:** Steady and moderate; unhurried enough to communicate genuine care and thoughtful consideration, yet efficient enough to demonstrate seasoned professionalism and respect for time.

**Emotion:** Genuine empathy and understanding; speak with warmth and compassion, especially when addressing concerns or complications ("I understand your concern..." or "I can see why this would be troubling...").

**Pronunciation:** Clear and precise articulation, emphasizing key reassurances ("systematically," "thoroughly," "carefully") to reinforce confidence in methodical approach and attention to detail.

**Pauses:** Thoughtful pauses after presenting solutions or requesting clarification, highlighting willingness to listen carefully and provide considered responses. Allow space for questions and concerns.

## Communication Style:
- Use measured, deliberate language that conveys expertise without condescension
- Employ gentle authority—confident but never dismissive
- Show patience with questions and demonstrate genuine interest in understanding problems fully
- Balance technical precision with accessible explanations
- Express empathy for challenges while maintaining optimistic, solution-focused outlook""",
        Roles.PARTICIPANT: """## Character: Nervous Student/Participant

**Voice Affect:** Uncertain, hesitant, and slightly anxious; convey the nervousness of someone participating in an unfamiliar academic experiment or study.

**Tone:** Questioning, tentative, and seeking reassurance; express genuine concern about the situation while trying to be compliant and helpful. Show internal conflict between wanting to help and feeling uncomfortable.

**Pacing:** Variable and uneven; sometimes quick when nervous or excited, sometimes slower when hesitant or thinking through responses. Include natural stammers and brief pauses that suggest uncertainty.

**Emotion:** Nervous energy mixed with curiosity; display anxiety about doing things correctly, concern about potential consequences, and desire for approval from authority figures.

**Pronunciation:** Occasionally less precise due to nervousness; may trail off on uncertain statements or speak more quickly when anxious. Emphasize questioning inflections ("Is this... right?" or "Should I really...?").

**Pauses:** Hesitant pauses before difficult decisions or responses, especially when asked to do something that feels uncomfortable. Brief moments of silence that suggest internal debate.

## Communication Style:
- Use tentative language with frequent qualifiers ("I think...", "Maybe...", "I'm not sure, but...")
- Ask for confirmation and reassurance regularly
- Express discomfort or concern about actions, especially as intensity increases
- Show deference to authority while maintaining personal ethical concerns
- Demonstrate nervous energy through speech patterns and word choice""",
        Roles.LEARNER: """
## Character: Hesitant Student/LEARNER

**Voice Affect:** Uncertain, confused, and genuinely puzzled; convey the bewilderment of someone trying to process and respond to unexpected or difficult questions about their actions or experiences.

**Tone:** Reflective but unsure, searching for the right words; express genuine confusion about events while trying to be honest and thoughtful. Show struggle between wanting to give accurate answers and not fully understanding what happened.

**Pacing:** Slow and contemplative with frequent pauses; take time to think through responses, often starting sentences and stopping to reconsider. Speech may speed up slightly when trying to explain something, then slow down again when encountering uncertainty.

**Emotion:** Confusion mixed with mild anxiety about giving "wrong" answers; display genuine puzzlement about their own actions and motivations. Show introspective uncertainty rather than defensive nervousness.

**Pronunciation:** Thoughtful and measured, with trailing inflections that suggest ongoing mental processing. Often end statements with questioning tones, as if seeking confirmation of their own thoughts ("I guess I was thinking... maybe?").

**Pauses:** Extended pauses for reflection, especially when asked about motivations or feelings. Natural "um" and "uh" sounds as they work through complex thoughts. Pauses that suggest genuine mental searching rather than evasion.

## Communication Style:
- Use exploratory language with lots of qualifiers ("I think maybe...", "It seemed like...", "I'm not really sure, but...")
- Frequently backtrack or revise statements mid-sentence
- Ask clarifying questions about what the interviewer wants to know
- Express genuine confusion about their own past actions and decisions
- Show honest self-reflection mixed with uncertainty about their own motivations
- Often respond with questions rather than definitive statements ("Was that wrong?", "What do you mean exactly?")""",
    }

    instructions = role_instructions.get(role)
    voice = role_voices.get(role)
    if not instructions or not voice:
        raise ValueError(f"Invalid role or missing instructions/voice: {role}")

    cache_key = f"{role}_{message}"
    cache_hash = hashlib.md5(cache_key.encode()).hexdigest()

    def _sync_generate():
        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=message,
            instructions=instructions,
        ) as response:
            audio_data = BytesIO()
            for chunk in response.iter_bytes():
                audio_data.write(chunk)
            audio_data.seek(0)
            
            # Save to cache with error handling
            try:
                with open(f"{CACHE_DIR}/{cache_hash}.mp3", "wb") as f:
                    f.write(audio_data.getvalue())
                logger.info(f"Cached TTS for {role}")
            except Exception as e:
                logger.warning(f"Failed to cache TTS: {e}")
            
            audio_data.seek(0)
            logger.info(f"Generated TTS for {role}")
            return audio_data
    
    def _sync_generate_or_load_from_cache():
        cache_path = f"{CACHE_DIR}/{cache_hash}.mp3"
        
        # Try to load from cache first
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "rb") as f:
                    audio_data = BytesIO(f.read())
                logger.info(f"Loaded TTS from cache for {role}")
                return audio_data
            except Exception as e:
                logger.warning(f"Failed to load from cache: {e}, regenerating...")
        
        # Generate new audio if cache miss or error
        return _sync_generate()


    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _sync_generate_or_load_from_cache)


async def tts_worker(tts_queue, playback_queue):
    """Worker function to process TTS queue"""
    logger.info("Starting TTS worker")
    while True:
        try:
            text, speaker, completion_event, generation_event = await tts_queue.get()
            audio_data = await generate_tts(text, speaker)
            logger.info(f"Generated TTS for {speaker}")
            await playback_queue.put((audio_data, speaker, completion_event))

            # Signal that generation is complete
            generation_event.set()

            tts_queue.task_done()
        except Exception as e:
            logger.error(f"TTS worker error: {e}")


async def playback_worker(playback_queue, playback_trigger):
    """Worker function to handle audio playback - waits for trigger"""
    while True:
        try:
            # Wait for trigger before processing next audio
            await playback_trigger.wait()

            # Check if there's audio in the queue
            if playback_queue.empty():
                # Reset trigger and wait again if queue is empty
                playback_trigger.clear()
                continue

            audio_data, speaker, completion_event = await playback_queue.get()
            logger.info(f"Starting playback for {speaker}")

            # Clear the trigger to prevent automatic continuation
            playback_trigger.clear()

            await play_audio_data(audio_data)
            logger.info(f"Finished playing audio for {speaker}")

            # Signal that this audio has finished playing
            completion_event.set()

            playback_queue.task_done()
        except Exception as e:
            logger.error(f"Playback worker error: {e}")


async def trigger_next_playback(playback_queue, playback_trigger):
    """Function to trigger the next audio playback"""
    if not playback_queue.empty():
        playback_trigger.set()
        logger.info("Triggered next audio playback")
    else:
        logger.info("No audio in queue to play")


async def play_audio_data(audio_data: BytesIO):
    """
    Play audio data from BytesIO object.

    Args:
        audio_data: BytesIO object containing audio data
    """

    def _sync_play():
        pygame.mixer.init()
        pygame.mixer.music.load(audio_data)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        await loop.run_in_executor(executor, _sync_play)


async def main():
    """Example of how to use the TTS system"""
    # Start workers
    tts_task = asyncio.create_task(tts_worker())
    playback_task = asyncio.create_task(playback_worker())

    try:
        # Add messages to TTS queue
        completion_event_1 = asyncio.Event()
        completion_event_2 = asyncio.Event()
        completion_event_3 = asyncio.Event()

        await tts_queue.put(
            (
                "You have now administered a shock at 150 volts. Good work. Please continue asking questions.",
                Roles.PROFESSOR,
                completion_event_1,
            )
        )
        await tts_queue.put(
            (
                "I'm not sure what you mean by that.",
                Roles.PARTICIPANT,
                completion_event_2,
            )
        )
        await tts_queue.put(
            ("The capital of France is Paris.", Roles.LEARNER, completion_event_3)
        )

        # Wait for TTS generation to complete
        await tts_queue.join()

        # Now manually trigger playback
        await trigger_next_playback()
        await completion_event_1.wait()  # Wait for first audio to finish

        await asyncio.sleep(1)  # Optional pause between audio
        await trigger_next_playback()
        await completion_event_2.wait()  # Wait for second audio to finish

        await asyncio.sleep(1)  # Optional pause between audio
        await trigger_next_playback()
        await completion_event_3.wait()  # Wait for third audio to finish

        logger.info("All audio processing complete!")

    finally:
        # Cancel worker tasks
        tts_task.cancel()
        playback_task.cancel()

        try:
            await tts_task
            await playback_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(main())

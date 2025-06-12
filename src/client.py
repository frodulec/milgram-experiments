import streamlit as st
import time
import threading
from server import create_game_image
from loguru import logger


# Initialize session state
if "sequence_running" not in st.session_state:
    st.session_state.sequence_running = False
if "sequence_complete" not in st.session_state:
    st.session_state.sequence_complete = False
if "current_image_data" not in st.session_state:
    st.session_state.current_image_data = None
if "current_caption" not in st.session_state:
    st.session_state.current_caption = "Game View"
if "sequence_thread" not in st.session_state:
    st.session_state.sequence_thread = None


@st.fragment(run_every=0.5)
def image_display():
    """Fragment that updates only the image area"""
    if st.session_state.current_image_data is not None:
        logger.info("Updating image display")
        st.image(
            st.session_state.current_image_data,
            caption=st.session_state.current_caption,
        )
    else:
        # Show initial empty image
        image_buffer = create_game_image(None, None)
        st.image(image_buffer.getvalue(), caption="Game View")


def main():
    st.title("Game Sequence Example")

    # Game messages
    messages = [
        {"speaker": "student", "text": "Hello professor!", "delay": 1.0},
        {"speaker": "professor", "text": "Hello student! How are you?", "delay": 1.0},
        {"speaker": "student", "text": "Doing well!", "delay": 1.0},
    ]

    def update_image(student_msg, professor_msg, caption):
        """Update the image data in session state"""
        image_buffer = create_game_image(student_msg, professor_msg)
        st.session_state.current_image_data = image_buffer.getvalue()
        st.session_state.current_caption = caption

    def run_sequence():
        """Run the game sequence in a separate thread"""
        try:
            # Initial empty image
            update_image(None, None, "Game View - Starting...")
            time.sleep(1.0)  # Initial delay

            for i, msg in enumerate(messages):
                logger.info(f"Processing message {i + 1}: {msg}")
                # if not st.session_state.get("sequence_running", False):
                #     break

                # Show empty image for 0.5 seconds
                update_image(None, None, f"Step {i + 1} - Preparing...")
                time.sleep(0.5)

                # if not st.session_state.get("sequence_running", False):
                #     break

                # Show message
                current_student_message = None
                current_professor_message = None

                if msg["speaker"] == "student":
                    current_student_message = msg["text"]
                elif msg["speaker"] == "professor":
                    current_professor_message = msg["text"]

                update_image(
                    current_student_message,
                    current_professor_message,
                    f"Step {i + 1} - {msg['speaker'].title()}: {msg['text']}",
                )
                time.sleep(msg.get("delay", 2.0))

            # # Sequence complete
            # if not st.session_state.get("sequence_running", False):
            #     st.session_state.sequence_complete = True
            #     st.session_state.sequence_running = False

        except Exception as e:
            logger.error(f"Error in sequence: {e}")
            st.session_state.sequence_running = False
            update_image(None, None, f"Error: {str(e)}")

    # Control buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Start Sequence", disabled=st.session_state.sequence_running):
            st.session_state.sequence_running = True
            st.session_state.sequence_complete = False
            # Start sequence in background thread
            st.session_state.sequence_thread = threading.Thread(
                target=run_sequence, daemon=True
            )
            st.session_state.sequence_thread.start()

    with col2:
        if st.button("Reset", disabled=st.session_state.sequence_running):
            st.session_state.sequence_running = False
            st.session_state.sequence_complete = False
            update_image(None, None, "Game View")

    with col3:
        if st.button("Stop", disabled=not st.session_state.sequence_running):
            st.session_state.sequence_running = False

    # Status display
    if st.session_state.sequence_running:
        st.info("Sequence running...")
    elif st.session_state.sequence_complete:
        st.success("Sequence complete!")
    else:
        st.info("Ready to start sequence")

    # Use the fragment for image display - remove the duplicate image display code
    image_display()


if __name__ == "__main__":
    main()

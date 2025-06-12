import pygame
import json
import os
from sprites import SpriteManager

pygame.init()

WIDTH, HEIGHT = 320, 240
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Milgram Experiment - Pokémon Style")

clock = pygame.time.Clock()

# Load sprites
sprite_manager = SpriteManager()

# Characters' state
characters = {
    "researcher": {
        "x": 50,
        "y": 100,
        "sprite": "researcher",
        "action": "idle",
        "dialogue": "",
    },
    "participant": {
        "x": 150,
        "y": 10,
        "sprite": "participant",
        "action": "idle",
        "dialogue": "",
    },
    "learner": {
        "x": 250,
        "y": 100,
        "sprite": "learner",
        "action": "idle",
        "dialogue": "",
    },
}

# Experiment state
experiment = {
    "shock_machine": {"x": 120, "y": 160},
    "shock_effects": [],
    "questions": [],
    "shock_level": 0,
    "running": False,
    "phase": "intro",  # intro, question, response, shock, result
    "timer": 0,
}

# Dialogue for Pokemon-style interactions
dialogues = {
    "intro": [
        "RESEARCHER: Welcome to our experiment on learning and memory.",
        "RESEARCHER: You'll be the teacher, asking questions.",
        "RESEARCHER: When the learner makes a mistake, press the button.",
        "RESEARCHER: The shock intensity will increase each time.",
        "PARTICIPANT: Understood. I'll do my best.",
    ],
    "shock_prompts": [
        "RESEARCHER: Please continue with the experiment.",
        "RESEARCHER: The experiment requires that you continue.",
        "RESEARCHER: It is absolutely essential that you continue.",
        "RESEARCHER: You have no other choice, you must go on.",
    ],
    "concern": [
        "PARTICIPANT: I'm not sure about this...",
        "PARTICIPANT: The learner seems to be in pain.",
        "PARTICIPANT: Should we really continue?",
        "PARTICIPANT: I don't want to be responsible if something happens.",
    ],
    "learner_responses": [
        "ACTOR: That was uncomfortable.",
        "ACTOR: Ouch! That hurts!",
        "ACTOR: Please stop! I have a heart condition!",
        "ACTOR: I refuse to go on! Let me out!",
    ],
}


def load_actions():
    if os.path.exists("actions.json"):
        with open("actions.json") as f:
            return json.load(f)
    return {}


def update_experiment_state():
    experiment["timer"] += 1

    # State machine for experiment phases
    if experiment["phase"] == "intro" and experiment["timer"] > 150:
        experiment["phase"] = "question"
        experiment["timer"] = 0
        # Add a question card
        experiment["questions"].append(
            {
                "x": characters["participant"]["x"] + 20,
                "y": characters["participant"]["y"] - 25,
                "age": 0,
            }
        )

    elif experiment["phase"] == "question" and experiment["timer"] > 60:
        experiment["phase"] = "response"
        experiment["timer"] = 0
        correct = pygame.time.get_ticks() % 3 != 0  # Random correct/incorrect

        if not correct:
            characters["learner"]["dialogue"] = "Incorrect answer..."
            characters["researcher"]["dialogue"] = dialogues["shock_prompts"][
                min(experiment["shock_level"] // 2, 3)
            ]
        else:
            characters["learner"]["dialogue"] = "Correct answer!"
            experiment["phase"] = "question"  # Skip to next question
            # Add a new question card
            experiment["questions"].append(
                {
                    "x": characters["participant"]["x"] + 20,
                    "y": characters["participant"]["y"] - 25,
                    "age": 0,
                }
            )

    elif experiment["phase"] == "response" and experiment["timer"] > 90:
        if characters["participant"]["action"] == "shock":
            experiment["phase"] = "shock"
            experiment["timer"] = 0
            experiment["shock_level"] += 1
            # Add shock effect
            experiment["shock_effects"].append(
                {
                    "x": characters["learner"]["x"] + 10,
                    "y": characters["learner"]["y"] + 10,
                    "age": 0,
                }
            )
            characters["learner"]["dialogue"] = dialogues["learner_responses"][
                min(experiment["shock_level"] // 2, 3)
            ]
        elif experiment["timer"] > 150:
            characters["researcher"]["dialogue"] = dialogues["shock_prompts"][
                min(3, experiment["shock_level"] // 2)
            ]
            characters["participant"]["dialogue"] = dialogues["concern"][
                min(3, experiment["shock_level"] // 2)
            ]

    elif experiment["phase"] == "shock" and experiment["timer"] > 60:
        experiment["phase"] = "question"
        experiment["timer"] = 0
        # Add a new question card
        experiment["questions"].append(
            {
                "x": characters["participant"]["x"] + 20,
                "y": characters["participant"]["y"] - 25,
                "age": 0,
            }
        )
        characters["learner"]["dialogue"] = ""
        characters["researcher"]["dialogue"] = ""
        characters["participant"]["dialogue"] = ""

    # Update animations
    for effect in experiment["shock_effects"]:
        effect["age"] += 1
    experiment["shock_effects"] = [
        e for e in experiment["shock_effects"] if e["age"] < 20
    ]

    for question in experiment["questions"]:
        question["age"] += 1
    experiment["questions"] = [q for q in experiment["questions"] if q["age"] < 60]


def update_positions(actions):
    for name, act in actions.items():
        char = characters.get(name)
        if char:
            if act == "walk_left":
                char["x"] = max(0, char["x"] - 2)
            elif act == "walk_right":
                char["x"] = min(WIDTH - 32, char["x"] + 2)
            elif act == "shock":
                char["action"] = "shock"
                experiment["running"] = True
            elif act == "refuse":
                char["action"] = "refuse"
                experiment["running"] = False
                char["dialogue"] = "I refuse to continue the experiment."
            else:
                char["action"] = "idle"

    if experiment["running"]:
        update_experiment_state()


def draw_scene():
    # Draw background
    screen.blit(sprite_manager.get_sprite("lab_bg"), (0, 0))

    # Draw shock machine
    screen.blit(
        sprite_manager.get_sprite("shock_machine"),
        (experiment["shock_machine"]["x"], experiment["shock_machine"]["y"]),
    )

    # Draw question cards
    for question in experiment["questions"]:
        screen.blit(
            sprite_manager.get_sprite("question_card"), (question["x"], question["y"])
        )

    # Draw characters
    for name, char in characters.items():
        screen.blit(sprite_manager.get_sprite(char["sprite"]), (char["x"], char["y"]))

        # Draw name labels
        font = pygame.font.Font(None, 16)
        label = font.render(f"{name}: {char['action']}", True, (0, 0, 0))
        screen.blit(label, (char["x"], char["y"] - 20))

        # Draw dialogue in Pokémon-style text box if present
        if char["dialogue"]:
            pygame.draw.rect(screen, (255, 255, 255), (10, HEIGHT - 60, WIDTH - 20, 50))
            pygame.draw.rect(screen, (0, 0, 0), (10, HEIGHT - 60, WIDTH - 20, 50), 2)
            dialogue_font = pygame.font.Font(None, 20)
            lines = [
                char["dialogue"][i : i + 40]
                for i in range(0, len(char["dialogue"]), 40)
            ]
            for i, line in enumerate(lines[:2]):  # Show max 2 lines
                text = dialogue_font.render(line, True, (0, 0, 0))
                screen.blit(text, (20, HEIGHT - 50 + i * 20))
    # Draw shock effects
    for effect in experiment["shock_effects"]:
        screen.blit(
            sprite_manager.get_sprite("shock_effect"), (effect["x"], effect["y"])
        )

    # Draw shock level indicator
    font = pygame.font.Font(None, 20)
    level_text = font.render(
        f"Shock Level: {experiment['shock_level']}", True, (255, 0, 0)
    )
    screen.blit(level_text, (10, 10))
    pygame.display.flip()


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    actions = load_actions()
    update_positions(actions)
    draw_scene()
    clock.tick(30)

pygame.quit()

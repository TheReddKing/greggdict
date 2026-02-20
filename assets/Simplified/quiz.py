import pygame
import json
from PIL import Image
import subprocess
import random

# Load the JSON data
with open("output2.json", "r") as file:
    new_word_dict = json.load(file)

with open("reference.json", "r") as file:
    references = json.load(file)


# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Word Quiz Game")
font = pygame.font.Font(None, 36)

with open("google-10000-english.txt", "r") as file:
    common_words = [word.strip() for word in file.readlines()]
    common_word_weights = {
        word: (len(common_words) - i) for i, word in enumerate(common_words)
    }

# Initialize variables
word_keys = list(new_word_dict.keys())

# Build weighted word list
weighted_words = []
for word in word_keys:
    if word in common_word_weights:
        # Weight by commonness (earlier = more common)
        weight = 10 + common_word_weights[word] // 100  # tune divisor for spread
        weighted_words.extend([word] * weight)
    else:
        weighted_words.append(word)

# Shuffle for randomness
random.shuffle(weighted_words)

# Track recently seen words
recent_words = []
RECENT_WORDS_MAX = 20
RECENT_WORDS_BOOST = 5  # how much more often to repeat recent words


def define_new_boosted_list():
    boosted_list = weighted_words[:]
    for word in recent_words:
        boosted_list.extend([word] * RECENT_WORDS_BOOST)
    random.shuffle(boosted_list)
    return boosted_list


def get_next_word(current_index, list):
    # Boost recent words
    return list[current_index % len(list)]


current_index = 0
guess_text = ""
message = ""
image_path = ""
boosted_list = define_new_boosted_list()


def load_image(word):
    """Loads and crops image based on JSON data."""
    global image_path
    image_path = new_word_dict[word]["page"]
    img = Image.open("output2/" + image_path).convert("RGB")
    img = img.crop(
        (new_word_dict[word]["x_start"], 0, new_word_dict[word]["x_end"], img.height)
    )
    length = new_word_dict[word]["x_end"] - new_word_dict[word]["x_start"]
    height = img.height
    img = img.resize((length * 2, height * 2))
    return pygame.image.fromstring(img.tobytes(), img.size, img.mode)


def display_text(text, y_position):
    """Renders text on the screen at specified y position."""
    text_surface = font.render(text, True, (255, 255, 255))
    screen.blit(text_surface, (20, y_position))


def check_guess():
    """Checks if the guess is correct and returns a message."""
    global message
    word = get_next_word(current_index, boosted_list)
    message = word


def edit():
    global image_path
    current_word = get_next_word(current_index, boosted_list)
    n = image_path.split(".")[0]
    found_word = False
    x = 0
    y = 0
    for page in references:
        if page["page"] == int(n):
            for word in page["words"]:
                if word["t"] == current_word:
                    x = word["x"]
                    y = word["y"]
                    found_word = True
            break

    print(x, y)
    subprocess.run(
        ["open", "-a", "gimp", f"pages/{image_path}"]
    )  # Replace with your command


def reprocess():
    global image_path
    global guess_text
    subprocess.Popen(["python", "command.py", image_path.split(".")[0]])
    guess_text = "REPROCESSING"
    # load_image(word_keys[current_index])


# Main loop
running = True
image_surface = load_image(get_next_word(current_index, boosted_list))

while running:
    screen.fill((0, 0, 0))  # Clear screen
    screen.blit(image_surface, (50, 50))  # Display image
    display_text("Word:", 20)
    display_text(guess_text, 450)
    display_text(message, 470)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT or (
                (event.key == pygame.K_n or event.key == pygame.K_RETURN)
                and pygame.key.get_mods() & pygame.KMOD_META
            ):  # Move to next image
                current_index = (current_index + 1) % len(weighted_words)
                current_word = get_next_word(current_index, boosted_list)
                image_surface = load_image(current_word)
                guess_text = ""
                message = ""
                # Track recent words
                recent_words.append(current_word)
                if len(recent_words) > RECENT_WORDS_MAX:
                    recent_words.pop(0)
            elif event.key == pygame.K_b and pygame.key.get_mods() & pygame.KMOD_META:
                boosted_list = define_new_boosted_list()
                message = "Boosted list updated"
                current_index = 0
                current_word = get_next_word(current_index, boosted_list)
                image_surface = load_image(current_word)
            elif event.key == pygame.K_RETURN:
                check_guess()
            elif event.key == pygame.K_e and pygame.key.get_mods() & pygame.KMOD_META:
                edit()
            elif event.key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_META:
                reprocess()
            elif event.key == pygame.K_LEFT:  # Move to previous image
                current_index = (current_index - 1) % len(weighted_words)
                current_word = get_next_word(current_index, boosted_list)
                image_surface = load_image(current_word)
                guess_text = ""
                message = ""
                # Track recent words
                recent_words.append(current_word)
                if len(recent_words) > RECENT_WORDS_MAX:
                    recent_words.pop(0)
            elif event.key == pygame.K_BACKSPACE:
                guess_text = guess_text[:-1]
            else:
                guess_text += event.unicode
                if guess_text == get_next_word(current_index, boosted_list):
                    message = "CORRECT"

    pygame.display.flip()

pygame.quit()

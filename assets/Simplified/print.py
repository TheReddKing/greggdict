from nltk.stem import WordNetLemmatizer
import sys
import json
import re
from datetime import datetime
with open('reference.json', 'r') as file:
    # Load the JSON data
    data = json.load(file)
from unidecode import unidecode

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import nltk
from nltk.corpus import cmudict

# Load the CMU Pronouncing Dictionary
pronunciation_dict = cmudict.dict()

# Initialize the WordNet lemmatizer
lemmatizer = WordNetLemmatizer()


# img = mpimg.imread("pages/001.png")
img = np.asarray(Image.open('pages/001.png'))
image_path = 'simple.png'
rgb_image = Image.open(image_path)

# Convert the RGB image to grayscale
grayscale_image = rgb_image.convert('L')

# Save the grayscale image
output_path = 'output2/simple.png'
grayscale_image.save(output_path)

with open('output2.json', 'r') as file:
    # Load the JSON data
    new_word_dict = json.load(file)

simple = [[["\"", "'"], 215, 230],
          [["may"], 10, 110],
          [["in"], 120, 120+30],
          [["i"], 165, 178+21],
          [["a", "an"], 250, 256],
          [["."], 275, 300],
          [["me"], 310, 310+80]
          ]

for (words, x_start, x_end) in simple:
    for word in words:
        new_word_dict[word] = {"page": "simple.png",
                               "x_start": x_start, "x_end": x_end}

# in the form IN_DICT, [ REPLACES... ]
replacements = {"maid": ["made"],
                "his": ["is"],
                "add": ["ad"],
                "wear": ["ware"],
                "down": ["done"],
                "document": ["doc"],
                "saloon": ["salon"],
                "present": ["per"],
                "need": ["knead"],
                "let": ["lett"]
                }
for replacement in replacements:
    for word in replacements[replacement]:
        new_word_dict[word] = new_word_dict[replacement]


def replace_if_ends_with(word, ends_with, replace_with):
    if word.endswith(ends_with):
        return (word[:-len(ends_with)] + replace_with, ends_with)
    return (word, None)


def resize(array, new_shape):
    pad_width = [(0, max(new_dim - old_dim, 0))
                 for new_dim, old_dim in zip(new_shape, array.shape)]
    array = np.pad(array, pad_width, mode='constant', constant_values=255)
    return array


def find_single_word(maps, word):
    possible_words = [
        (word, None),
        (word.capitalize(), "//"),
        (word[:-1], word[-1:]),
        replace_if_ends_with(word, "ing", ""),
        replace_if_ends_with(word, "ing", "e"),
        replace_if_ends_with(word, "ed", "e"),
        replace_if_ends_with(word, "ed", ""),
        replace_if_ends_with(word, "er", ""),
        replace_if_ends_with(word, "ers", ""),
        replace_if_ends_with(word, "es", ""),
        replace_if_ends_with(word, "'s", ""),
        replace_if_ends_with(word, "ly", ""),
        replace_if_ends_with(word, "able", ""),
        replace_if_ends_with(word, "al", ""),
        replace_if_ends_with(word, "ive", ""),
        replace_if_ends_with(word, "ful", ""),
        replace_if_ends_with(word, "ise", ""),
        replace_if_ends_with(word, "ning", ""),
        replace_if_ends_with(word, "ting", ""),
    ]
    # Find first
    for t_word, ends_with in possible_words:
        if t_word in maps:
            return (maps[t_word], ends_with)

    # Try stemming
    lem_word = lemmatizer.lemmatize(word)
    if (lem_word in maps):
        return (maps[lem_word], word[len(lem_word):])

    # Find dups with endings
    for t_word, ends_with in possible_words:
        if len(t_word) > 2 and t_word[-1] == t_word[-2]:
            t_word = t_word[:-1]
            if t_word in maps:
                return (maps[t_word], ends_with)

    # Find homophones of the word
    if word in pronunciation_dict:
        homophones = [key for key, pronunciations in pronunciation_dict.items() if any(
            pron == pronunciation_dict[word][0] for pron in pronunciations)]
        for homophone in homophones:
            if (homophone in maps):
                return (maps[homophone], "")

    return (None, None)


def find_word(maps, original_word):
    # We will find words using this simple trick

    res = find_single_word(maps, original_word)

    if (res[0] is not None):
        return ([res[0]], res[1])
    
    # Try splitting
    # i.e. meetups
    #      0123456
    modder = 0
    bad_endings = ["ing", "er", "est"]
    for bad_ending in bad_endings:
        if bad_ending in original_word[-len(bad_ending):]:
            modder = len(bad_ending)

    for i in range(2, len(original_word) - 1 - modder):
        word1 = original_word[0:i]
        word2 = original_word[i:]
        res = find_single_word(maps, word2)
        if (word1 in maps and res[0] is not None):
            return ([maps[word1], res[0]], res[1])

    return (None, None)


def expand_apostrophes(string):
    contractions = {
        "ain't": "am not",
        "aren't": "are not",
        "can't": "can not",
        "couldn't": "could not",
        "didn't": "did not",
        "doesn't": "does not",
        "don't": "do not",
        "hadn't": "had not",
        "hasn't": "has not",
        "haven't": "have not",
        "he's": "he is",
        "he'll": "he will",
        "he'd": "he would",
        "i'm": "i am",
        "i've": "i have",
        "i'd": "i would",
        "isn't": "is not",
        "it's": "it is",
        "it'll": "it will",
        "it'd": "it would",
        "let's": "let us",
        "mustn't": "must not",
        "shan't": "shall not",
        "she's": "she is",
        "she'll": "she will",
        "she'd": "she would",
        "shouldn't": "should not",
        "that's": "that is",
        "there's": "there is",
        "they're": "they are",
        "they'll": "they will",
        "they'd": "they would",
        "we're": "we are",
        "we've": "we have",
        "we'll": "we will",
        "we'd": "we would",
        "weren't": "were not",
        "what's": "what is",
        "where's": "where is",
        "who's": "who is",
        "won't": "will not",
        "wouldn't": "would not",
        "you're": "you are",
        "you've": "you have",
        "you'll": "you will",
        "you'd": "you would",
        "oh":"" # OH is not a valid word
    }

    for contraction, expansion in contractions.items():
        string = string.replace(contraction, expansion)

    return string


max_width = 1120  # 1000/160 = 8.5
max_lines = max_width * 11 / 8.5 // 160 # 160*11 = 11


def write_sentence(sentence, add_text=False, is_practice=False):
    sentence = unidecode(sentence)
    replacement_words = [["that's", "that is"],
                         ["don't", "do not"],
                         ["wasn't", "was not"],
                         ["he'd", "he would"],
                         ["couldn't", "could not"],
                         ["i've", "i have"]
                         ]
    words = sentence.lower()
    for a, b in replacement_words:
        words = words.replace(a, b)
    words = expand_apostrophes(words)
    words += " "
    words = words.replace(",", " ").replace("-", " ").replace(
        ":", " ").replace("? ", " ? ").replace(
        "\"", " \" ").replace("\'", "").replace("/", " / ").replace(
        "(", " ").replace(")", " ").replace("...", ". ").replace(".\n", " .\n").replace(". ", " . ").replace("\n\n", "\n").replace("\n", " \n ")
    split_words = re.split(r' +', words)
    # Re combine words
    words = []
    i = 0
    while (i < len(split_words)):
        if (i != len(split_words) - 1):
            combined_word = split_words[i] + "-" + split_words[i+1]
            if find_single_word(new_word_dict, combined_word)[0] is not None:
                words.append(combined_word)
                i += 2
                continue
        words.append(split_words[i])
        i += 1

    current_page = []
    combined_image = None
    width = 0
    for word in words:
        maybe_images, ends_with = find_word(new_word_dict, word)
        page_name = []
        new_width = 0
        maybe_image = None
        if maybe_images is not None:
            for id, ref_image in enumerate(maybe_images):
                page_name.append(ref_image["page"].split(".")[0])
                img = np.asarray(Image.open(f'output2/{ref_image["page"]}'))
                x_start = ref_image["x_start"]
                x_end = ref_image["x_end"]
                buffer = 15 if id == len(maybe_images) - 1 else 0
                img = resize(
                    img[0:160, x_start:x_end], (160, x_end-x_start + buffer))
                new_width += len(img[0])
                if maybe_image is None:
                    maybe_image = img
                else:
                    maybe_image = np.concatenate(
                        [maybe_image, img], axis=1)
            if ends_with and len(ends_with) > 0:
                this_img = Image.fromarray(maybe_image)
                draw = ImageDraw.Draw(this_img)
                font_path = 'font.ttf'  # Path to the font file
                font_size = 15  # Increase the font size for bigger text

                font = ImageFont.truetype(font_path, font_size)

                text_width = int(draw.textlength(ends_with, font=font))
                draw.text((max(2, new_width - text_width - 30), 110),
                          f"({ends_with})", font=font, fill=80)
                maybe_image = np.asarray(this_img)

        page_name = ", ".join(page_name)
        if maybe_image is None or add_text:
            font_path = 'font.ttf'  # Path to the font file
            font_size = 12
            if is_practice:
                fill = 160
            else:
                fill = 80
            coords = (0, 10)
            if maybe_image is None:
                # Increase the font size for bigger text
                font_size = 24
                fill = 60
                coords = (5, 60)
                new_image = Image.new(
                    'L', (max(max_width - 1 - width, 200), 160), 255)
                word += " "
            else:
                maybe_image = np.concatenate(
                    [maybe_image, np.asarray(Image.new('L', (100, 160), 255))], axis=1)
                new_image = Image.fromarray(maybe_image)
                if (page_name == "simple"):
                    pass
                else:
                    word += " (" + page_name + ")"
            draw = ImageDraw.Draw(new_image)

            font = ImageFont.truetype(font_path, font_size)
            if ("\n" in word):
                text_width = max_width - 11 - width
            else:
                text_width = int(draw.textlength(word, font=font))
                draw.text(coords, word, font=font, fill=fill)
            new_width = max(new_width, text_width + 10)
            new_image = np.asarray(new_image)[0:160, 0:new_width]
            maybe_image = new_image

        width += new_width
        if width > max_width:
            current_page.append(combined_image)
            combined_image = None
            width = new_width
        if maybe_image is not None:
            if combined_image is not None:
                combined_image = np.concatenate(
                    [combined_image, maybe_image], axis=1)
            else:
                combined_image = maybe_image
    if combined_image is not None:
        current_page.append(combined_image)
    combined_page = None
    combined_pages = []
    height = 0
    for (i, line) in enumerate(current_page):
        if combined_page is not None:
            new_shape = (160, max_width)
            combined_page = resize(combined_page, new_shape)

            line = resize(line, new_shape)

            combined_page = np.concatenate([combined_page, line], axis=0)
        else:
            combined_page = line
        height += 160
        if (i % max_lines == max_lines-1):
            combined_pages.append(combined_page)
            combined_page = None
    if combined_page is not None:
        combined_pages.append(combined_page)
    return combined_pages


args = sys.argv[1].split(".")
filename = "".join(args[:-1])
extension = args[-1]
practice = len(sys.argv) >= 3
with open(filename + "." + extension, "r") as file:
    text = file.read()
    print(text)
    with PdfPages(f'{filename}.pdf') as pdf:
        if practice:
            cs = write_sentence(text, add_text=True, is_practice=True)
        else:
            cs = write_sentence(text, add_text=False) + \
                write_sentence(text, add_text=True)
        for i, c in enumerate(cs):
            fig = plt.figure(figsize=(8.5, 11), dpi=100)
            ax = fig.add_axes([0, 0, 1, 1])
            ax.axis('off')
            ax.imshow(c, cmap='gray')
            # plt.savefig(f"story-{i}.png", pad_inches=0)
            pdf.savefig(fig, bbox_inches='tight', pad_inches=0.5)
            plt.close()

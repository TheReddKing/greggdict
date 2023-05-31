import json
from datetime import datetime
with open('reference.json', 'r') as file:
    # Load the JSON data
    data = json.load(file)
from unidecode import unidecode

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image, ImageDraw,ImageFont
import numpy as np
# img = mpimg.imread("pages/001.png")
img = np.asarray(Image.open('pages/001.png'))
image_path = 'simple.png'
rgb_image = Image.open(image_path)

# Convert the RGB image to grayscale
grayscale_image = rgb_image.convert('L')

# Save the grayscale image
output_path = 'output2/simple.png'
grayscale_image.save(output_path)

import json
with open('output2.json', 'r') as file:
    # Load the JSON data
    new_word_dict = json.load(file)

simple = [[["is"], 215, 230],
          [["may"], 10, 80],
          [["in"],120, 120+30],
          [["i"], 172, 178+21],
          [["a","an"], 250, 256],
          [["."], 275, 300],
          [["me"], 310, 310+80]
          ]
replacements = [["maid", ["made"]]]
for (replacement, for_) in replacements:
    for word in for_:
        new_word_dict[word] = new_word_dict[replacement]
        
for (words, x_start, x_end) in simple:
    for word in words:
        new_word_dict[word] = {"page": "simple.png",
                               "x_start": x_start, "x_end": x_end}
def replace_if_ends_with(word, ends_with, replace_with):
    if word.endswith(ends_with):
        return (word[:-len(ends_with)] + replace_with, ends_with)
    return (word, None)


def resize(array, new_shape):
    pad_width = [(0, max(new_dim - old_dim, 0))
                 for new_dim, old_dim in zip(new_shape, array.shape)]
    array = np.pad(array, pad_width, mode='constant', constant_values=255)
    return array


def find_word(maps, word):
    # We will find words using this simple trick
    possible_words = [
        (word, None),
        (word[:-1], word[-1:]),
        replace_if_ends_with(word, "ing", ""),
        replace_if_ends_with(word, "ing", "e"),
        replace_if_ends_with(word, "ed", "e"),
        replace_if_ends_with(word, "ed", ""),
        replace_if_ends_with(word, "er", ""),
        replace_if_ends_with(word, "es", ""),
        replace_if_ends_with(word, "'s",""),
        replace_if_ends_with(word, "ly", ""),
        replace_if_ends_with(word, "able", ""),
        replace_if_ends_with(word, "al", ""),
        replace_if_ends_with(word, "ive", ""),
        replace_if_ends_with(word, "ful", ""),
        ]
    # Find first
    for word, ends_with in possible_words:
        if word in maps:
            return (maps[word], ends_with)
        
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
        "you'd": "you would"
    }

    for contraction, expansion in contractions.items():
        string = string.replace(contraction, expansion)

    return string

def write_sentence(sentence, add_text=False):
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
    words = words.replace(",", " ").replace("-"," - ").replace(
        ":", "").replace(
        "\"", " ").replace("\'", " ").replace("/"," / ").replace(
        "(", " ").replace(")", " ").replace("...",".").replace(".", " . ").replace("\n", " pp ")
    words = words.split(" ")
    current_page = []
    combined_image = None
    width = 0
    for word in words:
        maybe_image, ends_with = find_word(new_word_dict, word)
        dic = maybe_image
        new_width = 0
        if maybe_image is not None:
            # print(maybe_image)
            img = np.asarray(Image.open(f'output2/{maybe_image["page"]}'))
            x_start = maybe_image["x_start"]
            x_end = maybe_image["x_end"]
            maybe_image = resize(
                img[0:160, x_start:x_end], (160, x_end-x_start + 15))
            new_width = len(maybe_image[0])
            if ends_with and len(ends_with) > 0:
                this_img = Image.fromarray(maybe_image)
                draw = ImageDraw.Draw(this_img)
                font_path = 'font.ttf'  # Path to the font file
                font_size = 15  # Increase the font size for bigger text

                font = ImageFont.truetype(font_path, font_size)
                draw.text((new_width / 20, 110), f"({ends_with})", font=font, fill=80)
                maybe_image = np.asarray(this_img) 

        if maybe_image is None or add_text:
            font_path = 'font.ttf'  # Path to the font file
            font_size = 12  
            fill = 100
            coords = (0, 10)
            if maybe_image is None:
                # Increase the font size for bigger text
                font_size = 24
                fill = 60
                coords = (5, 60)
                new_image = Image.new('L', (200, 160), 255)
                word += " "
            else:
                maybe_image = np.concatenate(
                        [maybe_image, np.asarray(Image.new('L', (100, 160), 255))], axis=1) 
                new_image = Image.fromarray(maybe_image)
                word += " (" + dic["page"].split(".")[0] + ")"
            draw = ImageDraw.Draw(new_image)

            font = ImageFont.truetype(font_path, font_size)
            text_width = int(draw.textlength(word, font=font))
            draw.text(coords, word, font=font, fill=fill)
            new_width = max(new_width, text_width + 10)
            new_image = np.asarray(new_image)[0:160, 0:new_width]
            maybe_image = new_image
            
        if maybe_image is not None:
            if combined_image is not None:
                combined_image = np.concatenate(
                    [combined_image, maybe_image], axis=1)
            else:
                combined_image = maybe_image
        width += new_width 
        if width > 1100:
            current_page.append(combined_image)
            combined_image = None
            width = 0
    if combined_image is not None:
        current_page.append(combined_image)
    combined_page = None
    combined_pages = []
    height = 0
    for (i, line) in enumerate(current_page):
        if combined_page is not None:
            new_shape = (160, 1400)
            combined_page = resize(combined_page, new_shape)

            line = resize(line, new_shape)

            combined_page = np.concatenate([combined_page, line], axis=0)
        else:
            combined_page = line
        height += 160
        if (i % 15 == 14):
            combined_pages.append(combined_page)
            combined_page = None
    if combined_page is not None:
        combined_pages.append(combined_page)
    return combined_pages

import sys 
filename = sys.argv[1]
with open(filename, "r") as file:
  text = file.read()
  print(text)
  with PdfPages(f'{filename}.pdf') as pdf:
    cs = write_sentence(text, add_text=False) + write_sentence(text, add_text=True)
    for i, c in enumerate(cs):
      plt.figure(figsize=(len(c[0])/10, len(c)/10), dpi=30)
      plt.imshow(c,cmap='gray')
      plt.axis('off')
      # plt.savefig(f"story-{i}.png", pad_inches=0)
      pdf.savefig(pad_inches=0)
      plt.close()
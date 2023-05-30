import sys
import json
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from datetime import datetime


def getmaxx(x, xs):
    for xx in xs:
        if (xx > x + 5):
            return int(xx) - 5


def flood_fill(img, x, y, processed_pixels, new_processed_pixels, master_set, new_set):
    coords = (x, y)
    new_processed_pixels.add(coords)
    try:
        if (coords not in processed_pixels and coords not in master_set and img[y, x] < 150.0):
            # NOT WHITE
            new_set.add(coords)
            diff = 1
            for dx in range(-diff, diff+1):
                for dy in range(-diff, diff+1):
                    coords = (x + dx, y + dy)
                    if (coords not in new_processed_pixels and coords not in processed_pixels):
                        flood_fill(
                            img, coords[0], coords[1], processed_pixels, new_processed_pixels, master_set, new_set)
    except:
        pass


def find_islands(already_assigned_pixels, new_pixels, maxx):
    # THOSE PESKY DOTS

    all_new_assigned_pixels = set()
    all_new_island_pixels = set()
    pixels_seen_ourselves = set()
    for (x, y) in new_pixels:
        diff = 8
        for dx in range(-diff, diff+1):
            for dy in range(-diff, diff+1):
                coords = (x + dx, y + dy)
                if coords in pixels_seen_ourselves or coords in new_pixels:
                    continue
                pixels_seen_ourselves.add(coords)
                new_assigned_pixels = set()
                new_island_pixels = set()
                flood_fill(img, x + dx, y + dy, already_assigned_pixels,
                           new_assigned_pixels, new_pixels, new_island_pixels)
                pixels_seen_ourselves.update(new_assigned_pixels)
                if (len(new_island_pixels) > 0 and max([x for (x, y) in new_island_pixels]) > maxx):
                    continue
                all_new_assigned_pixels.update(new_assigned_pixels)
                all_new_island_pixels.update(new_island_pixels)
    already_assigned_pixels.update(all_new_assigned_pixels)
    new_pixels.update(all_new_island_pixels)


def find(minx, maxx, y, pixels, processed_pixels, max_shapes=0, must_be_bigger_than=0):
    new_processed_pixels = set()
    new_pixels = set()
    shapes = 0
    last_x = 0
    found_a_big_one = False
    for x in range(minx, maxx):
        if (max_shapes > 0 and shapes >= max_shapes):
            break
        new_processed_pixels.clear()
        new_pixels.clear()
        flood_fill(img, x, y, processed_pixels,
                   new_processed_pixels, pixels, new_pixels)
        if (len(new_pixels) == 0):
            continue
        max_y = max([y for (x, y) in new_pixels] + [y])
        min_y = min([y for (x, y) in new_pixels] + [y])
        height = max_y - min_y

        # if (height > 60 and min_y > y) or (max_y < y and height > 60):
        #     # We are too greedy and looked too far
        #     continue
        if (max_shapes > 0 and last_x > 0 and x - last_x > 20):
            # SKIP TO THE BEST PART!
            max_shapes = shapes + 1
        max_x = max([x for (x, y) in new_pixels] + [x])
        min_x = min([x for (x, y) in new_pixels] + [x])
        last_x = max(last_x, max_x)
        width = max_x - min_x
        prints("FOUND", width, height)
        if (width > 8 or height > 8):
            if (must_be_bigger_than > 0):
                if(len(new_processed_pixels) < must_be_bigger_than):
                    continue
            if (max_shapes == 1 and len(new_processed_pixels) < must_be_bigger_than):
                continue
            if (width > 30 or height > 30) and (shapes > 2 or max_shapes < 2):
                found_a_big_one = True
            processed_pixels.update(new_processed_pixels)
            pixels.update(new_pixels)
            # prints(len(new_pixels))
            shapes += 1
    if (max_shapes > 0):
        prints(max_shapes, shapes)

    return max(max_shapes - shapes, 0), found_a_big_one

_print = print
all_output = ""
def prints(*x):
    global all_output
    _print(*x)
    all_output += " ".join(list(map(lambda y:str(y), x))) + "\n"

def print(*x):
    prints(*x)

def get_pixels_for_words(words, img):
    xs = set([word['x'] for word in words] + [len(img[0])])
    xs = sorted(list(xs))
    xs

    # FIND ALL PIXELS FOR EACH IMAGE
    time = datetime.now()
    processed_pixels = set()
    pixels_for_words = dict()
    for word in words:
        prints("D0", word['t'])
        # MAX FIND ONE BIG ONE
        pixels = set()
        y = int(word["y"])
        minx = int(word["x"])
        maxx = getmaxx(minx, xs)
        # Ws are annoying and sometimes might be confused as 2 words, therefore increase the max words for them by one.
        max_shapes = len(word["t"]) + 1 + word["t"].count("w")
        shapes, found_a_big_one = find(minx, maxx, y, pixels, processed_pixels,
                                       max_shapes=max_shapes, must_be_bigger_than=40)
        if (shapes > 0 or (not found_a_big_one and len(word["t"]) > 5)):
            # OH NO we didn't find something so let's be a bit greedy
            prints("Did not find what we wanted - GREEDY", minx, maxx)
            true_break = False
            for dy in range(0, 30, 3):
                for sign in [-1, 1]:
                    yy = y + dy * sign
                    shapes, found_a_big_one = find(minx + 50, maxx, yy, pixels, processed_pixels,
                                                   max_shapes=1, must_be_bigger_than=80)
                    if (found_a_big_one):
                        true_break = True
                        break
                if true_break:
                    break

        pixels_for_words[word["t"]] = pixels

    prints("D1 - word found", datetime.now() - time)
    for dy in range(-30, 30, 3):
        for word in words:
            pixels = pixels_for_words[word["t"]]
            y = int(word["y"]) + dy
            minx = int(word["x"])

            maxx = getmaxx(minx, xs)
            prints("larger word catching")
            find(minx, maxx, y, pixels, processed_pixels,
                 max_shapes=1, must_be_bigger_than=400)

    prints("D1.5", datetime.now() - time)
    for word in words:
        # Find islands last
        minx = int(word["x"])
        maxx = getmaxx(minx, xs)
        pixels = pixels_for_words[word["t"]]
        find_islands(processed_pixels, pixels, maxx)

    prints("D1.7", datetime.now() - time)

    for dy in range(0, 30, 3):
        for sign in [-1, 1]:
            for word in words:
                pixels = pixels_for_words[word["t"]]
                y = int(word["y"]) + dy * sign
                minx = int(word["x"])

                maxx = getmaxx(minx, xs)

                find(minx, maxx, y, pixels, processed_pixels)

    prints("D2", datetime.now() - time)
    # TRIM PIXELS
    trimmed_pixels_for_words = dict()
    for word in words:
        pixels = pixels_for_words[word["t"]]
        # find all "gaps"
        allx = set([x for (x, y) in pixels])
        # prints(allx)
        minx = int(word["x"])
        maxx = getmaxx(minx, xs)
        gaps = []
        ingap = 0
        all_y_for_x = set()
        for x in range(minx, maxx+200):
            if (x in allx):
                all_y_for_x.update(set([y for (x1, y) in pixels if x == x1]))
                ingap += 1
            else:
                if ingap >= 10 or (len(all_y_for_x) > 0 and max(all_y_for_x) - min(all_y_for_x) > 10):
                    gaps.append(x)
                ingap = 0
                all_y_for_x = set()
        # prints(word["t"],gaps)
        try:
            minx, maxx = (gaps[-2], gaps[-1])
            if len(gaps) >= 3:
                minp, minx, maxx = (gaps[-3], gaps[-2], gaps[-1])     
                if minx - minp  > maxx - minx:
                    minx = minp
            trimmed_pixels_for_words[word["t"]] = set(
                [(x, y) for (x, y) in pixels if x >= minx and x <= maxx])
        except:
            pass

    prints("D3", datetime.now() - time)
    return trimmed_pixels_for_words, pixels_for_words


with open('reference.json', 'r') as file:
    # Load the JSON data
    data = json.load(file)


new_word_dict = dict()  # maps word -> { page, x_start, x_end }

with open('output2.json', 'r') as file:
    # Load the JSON data
    val = json.load(file)
    if (val):
        new_word_dict = val

specific_page = None
if len(sys.argv) >= 2:
    specific_page = int(sys.argv[1])
    data = data[specific_page-1: specific_page]


donotsave = False
if len(sys.argv) >= 3:
    donotsave = True

PADME = np.full((160, 2), 0, dtype=np.uint8)
PADME_WHITE = np.full((160, 5), 255, dtype=np.uint8)
PADME2 = np.full((2, 1300), 0, dtype=np.uint8)

for page in data:
    all_output = ""
    filename = f'pages/{page["page"]}.png'
    output_filename = f"{page['page']}.png"
    prints("PAGE", filename)
    words = page["words"]
    img = np.asarray(Image.open(filename), dtype=np.uint8)
    pixels_for_words, untrimmed_pixels_for_words = get_pixels_for_words(
        words, img)
    combined_image = None
    combined_image_for_debugging = None
    width = 0
    for word in words:
        pixels = pixels_for_words[word["t"]]
        untrimmed_pixels = untrimmed_pixels_for_words[word["t"]]
        allx = set([x for (x, y) in pixels])
        # x, y = int(word['x']), int(word['y']) - 80
        # z, v = x+400,y+160

        wy = int(word['y'])

        myx = int(word['x'])
        x, y = min(allx) - 2, int(word['y']) - 80
        z, v = max(allx) + 2, y + 160
        new_width = z - x
        cleanimg = np.full((160, new_width), 255, dtype=np.uint8)
        untrimmed_cleanimg = np.full((160, 400), 255, dtype=np.uint8)
        for (c, r) in pixels:
            if 0 <= (r-y) and (r-y) < 160 and \
                    0 <= c-x and c-x < new_width:
                cleanimg[r-y, c-x] = 0
        for (c, r) in untrimmed_pixels:
            if 0 <= (r-y) and (r-y) < 160 and \
                    0 <= c-myx and c-myx < 400:
                untrimmed_cleanimg[r-y, c-myx] = 0
        # cleanimg = img[y:v,x:z].copy()
        # for r in range(len(cleanimg)):
        #     for c in range(len(cleanimg[0])):
        #         if (c+x, r+y) not in pixels:
        #             cleanimg[r,c] = 255
        newimage = cleanimg
        new_word_dict[word['t']] = {
            "page": output_filename,
            "x_start": width,
            "x_end": width + new_width}
        if combined_image is not None:
            combined_image = np.concatenate([combined_image, newimage], axis=1)
        else:
            combined_image = newimage
        untrimmed_cleanimg = np.concatenate(
            [img[y:v, myx:myx+330], PADME, untrimmed_cleanimg, PADME, PADME_WHITE, newimage], axis=1)
        # Define the desired size
        desired_size = (160, 1300)

        # Calculate the amount of padding required for each dimension
        pad_width = ((0, desired_size[0] - untrimmed_cleanimg.shape[0]),
                     (0, desired_size[1] - untrimmed_cleanimg.shape[1]))
        # Pad the array with zeros
        untrimmed_cleanimg = np.pad(
            untrimmed_cleanimg, pad_width, mode='constant', constant_values=255)

        if combined_image_for_debugging is not None:
            combined_image_for_debugging = np.concatenate(
                [combined_image_for_debugging, PADME2, untrimmed_cleanimg], axis=0)
        else:
            combined_image_for_debugging = untrimmed_cleanimg
        width += new_width
    prints(len(combined_image[0]), width)
    prints(len(combined_image), 160)
    prints(combined_image[0])
    image = Image.fromarray(combined_image, mode='L')
    image.save(f"output2/{output_filename}")
    image = Image.fromarray(combined_image_for_debugging, mode='L')
    image.save(f"output2_debug/{output_filename}")
    with open(f"output2_debug/{output_filename}.log", "w") as file:
        file.write(all_output)
        
    # plt.figure(figsize=(width/100, 160/100), dpi=80)
    # plt.imshow(combined_image, cmap='gray')
    # plt.axis('off')
    # plt.savefig(f"output/{output_filename}",bbox_inches=(width/100, 160/100), pad_inches=0)
    # plt.close()
    # plt.show()
    if not donotsave:
        with open("output2.json", 'w') as file:
            # Write the JSON data to the file
            json.dump(new_word_dict, file)

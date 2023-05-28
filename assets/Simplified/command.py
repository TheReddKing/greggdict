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
        diff = 4
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
                if (len(new_island_pixels) > 0 and max([x for (x,y) in new_island_pixels]) > maxx):
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
    skipped_to_word = False
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
            skipped_to_word = True
        max_x = max([x for (x, y) in new_pixels] + [x])
        min_x = min([x for (x, y) in new_pixels] + [x])
        last_x = max(last_x, max_x)
        width = max_x - min_x
        print("FOUND", width, height)
        if (width > 8 or height > 8):
            if (must_be_bigger_than > 0 and skipped_to_word):
                if(len(new_processed_pixels) < must_be_bigger_than):
                    continue
            if (max_shapes == 1 and len(new_processed_pixels) < must_be_bigger_than):
                continue
            processed_pixels.update(new_processed_pixels)
            pixels.update(new_pixels)
            # print(len(new_pixels))
            shapes += 1
    if (max_shapes > 0):
        print(max_shapes, shapes)

    return max(max_shapes - shapes, 0)


def get_pixels_for_words(words, img):
    xs = set([word['x'] for word in words] + [len(img[0])])
    xs = sorted(list(xs))
    xs

    # FIND ALL PIXELS FOR EACH IMAGE
    time = datetime.now()
    processed_pixels = set()
    pixels_for_words = dict()
    for word in words:
        # MAX FIND ONE BIG ONE
        pixels = set()
        y = int(word["y"])
        minx = int(word["x"])
        maxx = getmaxx(minx, xs)
        max_shapes = len(word["t"])+1
        shapes = find(minx, maxx, y, pixels, processed_pixels,
             max_shapes=max_shapes, must_be_bigger_than=40)
        if (shapes > 0):
            # OH NO we didn't find something so let's be a bit greedy
            print("GREEDY", minx, maxx)
            for y in range(-30 + y, 30 + y, 3):
                shapes = find(minx, maxx, y, pixels, processed_pixels,
                    max_shapes=1, must_be_bigger_than=80)

        pixels_for_words[word["t"]] = pixels

    print("D1", datetime.now() - time)
    for dy in range(-30, 30, 3):
        for word in words:
            pixels = pixels_for_words[word["t"]]
            y = int(word["y"]) + dy
            minx = int(word["x"])

            maxx = getmaxx(minx, xs)
            print("larger word catching")
            find(minx, maxx, y, pixels, processed_pixels, max_shapes=1, must_be_bigger_than=400)

    print("D1.5", datetime.now() - time)
    for word in words:
        # Find islands last
        minx = int(word["x"])
        maxx = getmaxx(minx, xs)
        pixels = pixels_for_words[word["t"]]
        find_islands(processed_pixels, pixels, maxx)

    print("D1.7", datetime.now() - time)

    for dy in range(-30, 30, 3):
        for word in words:
            pixels = pixels_for_words[word["t"]]
            y = int(word["y"]) + dy
            minx = int(word["x"])

            maxx = getmaxx(minx, xs)
            
            find(minx, maxx, y, pixels, processed_pixels)

    print("D2", datetime.now() - time)
    # TRIM PIXELS
    for word in words:
        pixels = pixels_for_words[word["t"]]
        # find all "gaps"
        allx = set([x for (x, y) in pixels])
        # print(allx)
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
        # print(word["t"],gaps)
        try:
            minx, maxx = (gaps[-2], gaps[-1])
            pixels_for_words[word["t"]] = set(
                [(x, y) for (x, y) in pixels if x >= minx and x <= maxx])
        except:
            pass

    print("D3", datetime.now() - time)
    return pixels_for_words


with open('reference.json', 'r') as file:
    # Load the JSON data
    data = json.load(file)


new_word_dict = dict()  # maps word -> { page, x_start, x_end }

with open('output2.json', 'r') as file:
    # Load the JSON data
    val = json.load(file)
    if (val):
        new_word_dict = val

specific_page=None
import sys
if len(sys.argv) >= 2:
    specific_page = int(sys.argv[1])
    data = data[specific_page-1: specific_page]
    
for page in data:
    filename = f'pages/{page["page"]}.png'
    output_filename = f"{page['page']}.png"
    print("PAGE", filename)
    words = page["words"]
    img = np.asarray(Image.open(filename), dtype=np.uint8)
    pixels_for_words = get_pixels_for_words(words, img)
    combined_image = None
    width = 0
    for word in words:
        pixels = pixels_for_words[word["t"]]
        allx = set([x for (x, y) in pixels])
        # x, y = int(word['x']), int(word['y']) - 80
        # z, v = x+400,y+160

        wy = int(word['y'])
        x, y = min(allx) - 2, int(word['y']) - 80
        z, v = max(allx) + 2, y + 160
        new_width = z - x
        cleanimg = np.full((160, new_width), 255, dtype=np.uint8)
        for (c, r) in pixels:
            if 0 <= (r-y) and (r-y) < 160 and \
                    0 <= c-x and c-x < new_width:
                cleanimg[r-y, c-x] = 0
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
        width += new_width
    print(len(combined_image[0]), width)
    print(len(combined_image), 160)
    print(combined_image[0])
    image = Image.fromarray(combined_image, mode='L')
    image.save(f"output2/{output_filename}")

    # plt.figure(figsize=(width/100, 160/100), dpi=80)
    # plt.imshow(combined_image, cmap='gray')
    # plt.axis('off')
    # plt.savefig(f"output/{output_filename}",bbox_inches=(width/100, 160/100), pad_inches=0)
    # plt.close()
    # plt.show()

    with open("output2.json", 'w') as file:
        # Write the JSON data to the file
        json.dump(new_word_dict, file)

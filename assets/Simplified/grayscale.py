import sys
import json
from datetime import datetime
with open('reference.json', 'r') as file:
    # Load the JSON data
    data = json.load(file)
from unidecode import unidecode

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import fitz  # PyMuPDF
import numpy as np

pageName = "A" + str(sys.argv[1]).zfill(2)

# Open the PDF file
pdf_document = fitz.open(f"unclean/{pageName}.pdf")

# Select the page you want to extract (e.g., the first page)
page_number = 0
page = pdf_document.load_page(page_number)

# Render the page to an image (pixmap)
pix = page.get_pixmap()

# Convert the pixmap to a PIL Image
rgb_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

# Convert the RGB image to grayscale
grayscale_image = rgb_image.convert('L')

# Save the grayscale image
output_path = f'pages/{pageName}.png'
grayscale_image.save(output_path)
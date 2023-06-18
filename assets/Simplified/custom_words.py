from reportlab.lib.pagesizes import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json
from wand.image import Image


# Set the desired width and height of the PDF in inches
width = 8.5 * inch * 2  # 8.5 inches
height = 11 * inch * 2 # 11 inches

# Create a new canvas with the specified width and height

page = "A01"
c = canvas.Canvas(page+".pdf", pagesize=(width, height))

pdfmetrics.registerFont(TTFont('OpenSans', 'font.ttf'))

# Set the font and font size
font_size = 30
c.setFont("OpenSans", font_size)
c.translate(0, height)

words="""
us
her
I-am
per
my
been
I-can

""".strip().split("\n")

c.setStrokeColor(colors.black)
c.rect(0, 0, 400, 5, fill=True, stroke=True)
w_dict = []
diff = 80
for i, word in enumerate(words):
  d = {"t": word, "x": 20, "y": 20 + (i * 2 * diff + diff)}
  c.drawString(d["x"] + 3, -d["y"] - font_size / 4, word)


  # c.setStrokeColor(colors.black)
  # c.rect(d["x"], -d["y"] + diff, 400, 2*diff, fill=False, stroke=True)
  w_dict.append(d)

# Save the canvas as a PDF file
c.showPage()
c.save()


with Image(filename=page+'.pdf') as img:
    img.format = 'png'
    img.save(filename=page+'.png')

js = {"page":page,"words":w_dict}
print(js)

try:
  with open('reference_personal.json', 'r') as file:
      # Load the JSON data
      data = json.load(file)
except:
   data = []


with open('reference_personal.json', 'w') as file:
    #find and replace
    found_page = False
    new_data = []
    for data_page in data:
       if (data_page["page"] == page):
          new_data.append(js)
          found_page = True
       else:
          new_data.append(data_page)
    if not found_page:
      new_data.append(js)
    json.dump(new_data, file)
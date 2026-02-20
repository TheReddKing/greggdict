from reportlab.lib.pagesizes import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json
from wand.image import Image
from custom_words_data import wordsOnPages


# Set the desired width and height of the PDF in inches
width = 8.5 * inch * 2  # 8.5 inches
height = 11 * inch * 2 # 11 inches

# Create a new canvas with the specified width and height

stroke = colors.HexColor(0xEEEEEE)
for (pageI, wordsOnPage) in enumerate(wordsOnPages):
   pageI += 1
   page = "A" + str(pageI).zfill(2)
   c = canvas.Canvas("pages_empty/" + page+".pdf", pagesize=(width, height))

   pdfmetrics.registerFont(TTFont('OpenSans', 'font.ttf'))

   # Set the font and font size
   font_size = 30
   c.setFont("OpenSans", font_size)
   c.translate(0, height)
   c.setFillColor(colors.white)
   c.rect(0,-height,width,height,fill=1)
   w_dict = []
   diff = 80
   for i, word in enumerate(wordsOnPage):
      modx = i // 9
      mody = i % 9
      x =  20 + modx * 400
      y = 20 + (mody * 1.4 * diff + diff)
      d = {"t": word, "x": x, "y": y}
      c.setStrokeColor(stroke)
      c.setFillColor(stroke)
      c.rect(x, -y - diff/2, 380, diff, fill=1)
      c.setFillColor(colors.black)
      c.drawString(x + 3, -y - font_size / 4, word)
      w_dict.append(d)

   # Save the canvas as a PDF file
   c.showPage()
   c.save()


   with Image(filename="pages_empty/" + page+'.pdf') as img:
      img.format = 'png'
      img.save(filename="pages_empty/" + page+'.png')

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
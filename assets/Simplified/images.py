from PIL import Image, ImageDraw, ImageFont

width = 5
fill="black"
# Define the bounding box for the arc

def drawG(draw, x, y):
  draw.arc([x, y - 20, x + 80, y +20], start=180, end=360, fill="black", width=width)
  return (x + 80, y)

def drawK(draw, x, y):
  draw.arc([x, y-15, x + 60, y + 15], start=180, end=360, fill="black", width=width)
  return (x + 60, y)

def drawT(draw, x, y):

  draw.line([x,y, x+20, y-20],fill=fill, width=width, joint="curve")
  return (x + 20, y-20)

def drawA(draw, x, y):
  draw.ellipse([x-10,y ,x+10,y+20], outline=fill, width=width)
  return (x,y)
  


def drawInSequence(fs):
  im = Image.new('RGBA', (400, 400), (0, 255, 0, 0))
  draw = ImageDraw.Draw(im) 
  x,y = 20, 200
  for f in fs:
    x,y= f(draw, x, y)
  im.show()

  
drawInSequence([
  drawG, drawK, drawA, drawT
]
)
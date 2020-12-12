from PIL import Image
import PIL
import os
import glob

image = Image.open('./images/pythonexplained.png')
image = image.convert('RGB')
image.save('./images/pythonexplained.webp', 'webp')


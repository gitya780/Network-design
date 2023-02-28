# -*- coding: utf-8 -*-
"""
Created on Wed Feb 23 23:34:35 2022

@author: Geetesh
"""

from PIL import Image
import random

im = Image.open('a.bmp')
w, h = im.size

pixels = im.load()

# Curruption by adding black pixels (make it grainy):
for _ in range(10000):
    pixels[random.randint(0, w - 1), random.randint(0, h - 1)] = (0, 0, 0)

im.save('thumbnail.bmp', 'bmp')
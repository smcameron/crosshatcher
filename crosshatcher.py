#!/usr/bin/python
#
# Copyright (c) 2013 Stephen M. Cameron
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import pygame
import time
import os, sys
import Image
import random
import math
import time

imagename = "image.jpg";
if (len(sys.argv) >= 2):
  imagename = sys.argv[1];

im = Image.open(imagename)

pix = im.load()
image_width = 0.0 + im.size[0];
image_height = 0.0 + im.size[1];
screen_width = 3000 
screen_height = int(screen_width * image_height / image_width);
print image_width, image_height, screen_width, screen_height

# origin on screen
osx = 0;
osy = 0;

black = (0, 0, 0)
white = (255, 255, 255)
nlayers = 15;
linespacing = 20;

radius = math.sqrt(2.0) * (1.1 * screen_height);

if screen_width > screen_height:
   radius = math.sqrt(2.0) * (1.1 * screen_width)

screen = pygame.display.set_mode([screen_width, screen_height])
pygame.display.update()

# screen x to image x
def sxtoix(sx):
  return (image_width * sx) / screen_width;

def sytoiy(sy):
  return (image_height * sy) / screen_height;

def sampleimg(sx, sy):
   ix = sxtoix(sx)
   iy = sytoiy(sy)
   if ix < 0:
      return 0
   if iy < 0:
      return 0
   if ix >= image_width:
      return 0
   if iy >= image_height:
      return 0
   return pix[ix, iy]

def rotate_point(p, angle):
   x = p[0];
   y = p[1];
   rx = x * math.cos(angle) - y * math.sin(angle);
   ry = x * math.sin(angle) + y * math.cos(angle);
   return (rx, ry);

def hypot(p1, p2):
   return math.sqrt((p1[0] - p2[0]) * (p1[0] - p2[0]) +
			(p1[1] - p2[1]) * (p1[1] - p2[1]));

def do_a_line(threshold, p1, p2):
   d = hypot(p1, p2);
   seglen = linespacing * 2.0;
   nsegs = int(d / seglen);

   dx = (p2[0] - p1[0]) / nsegs;
   dy = (p2[1] - p1[1]) / nsegs;
   for i in range(0, nsegs - 1):
      x1 = p1[0] + dx * i;
      y1 = p1[1] + dy * i;
      x2 = p1[0] + dx * (i + 1);
      y2 = p1[1] + dy * (i + 1);
      mx = (x2 - x1 / 2.0) + x1;
      my = (y2 - y1 / 2.0) + y1;
      s = sampleimg(mx, my);
      if s <= threshold:
         pygame.draw.line(screen, black, (x1, y1), (x2, y2), 1);

def do_layer(layer, threshold, angle):
   count = int((radius * 2.0) / linespacing);
   cx = screen_width / 2.0;
   cy = screen_height / 2.0;
   for i in range(-count / 2, count / 2):
      x1 = cx + (i * linespacing);
      y1 = cy - radius * 2;
      x2 = x1;
      y2 = cy + radius * 2;
      p1 = rotate_point((x1, y1), angle);
      p2 = rotate_point((x2, y2), angle); 
      do_a_line(threshold, p1, p2);
      pygame.display.update()

screen.fill(white)
for i in range(1, nlayers):
   do_layer(i, i * 256 / nlayers, i * 127 * math.pi / 180.0);

pygame.image.save(screen, "output.png");
print
print
print "Saved output image to output.png"
print
print


#!/usr/bin/python
#
#       Copyright (C) 2013 Stephen M. Cameron
#       Author: Stephen M. Cameron
#
#       This file is part of crosshatcher.
#
#       crosshatcher is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       crosshatcher is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with crosshatcher; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import pygame
import time
import os, sys
from PIL import Image
import random
import math
import time

imagename = "image.jpg";
if len(sys.argv) >= 2:
  imagename = sys.argv[1];


im = Image.open(imagename)

pix = im.load()
image_width = 0.0 + im.size[0];
image_height = 0.0 + im.size[1];
screen_width = 3000 
if len(sys.argv) >= 3:
  screen_width = int(sys.argv[2]);
  if screen_width == 0:
    screen_width = 3000;

screen_height = int(screen_width * image_height / image_width);
print image_width, image_height, screen_width, screen_height

# origin on screen
osx = 0;
osy = 0;

black = (0, 0, 0)
white = (255, 255, 255)
linespacing = 20;
if len(sys.argv) >= 4:
  linespacing = int(sys.argv[3]);
  if linespacing == 0:
    linespacing = 20;

nlayers = 10;
if len(sys.argv) >= 5:
  nlayers = int(sys.argv[4]);
  if nlayers == 0:
    nlayers = 10;

myfile = open('lines.txt', 'w+');
svgfile = open('lines.svg', 'w+');
print >> svgfile, "<svg height=\"%d\" width=\"%d\" style=\"background-color:#ffffff00\" version=\"1.1\"  xmlns=\"http://www.w3.org/2000/svg\">" % (screen_height, screen_width)
print >> svgfile, "<path d=\"",

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

def rotate_point(p, c, angle):
   x = p[0];
   y = p[1];
   cx = c[0];
   cy = c[1];
   rx = (x - cx) * math.cos(angle) - (y - cy) * math.sin(angle);
   ry = (x - cx) * math.sin(angle) + (y - cy) * math.cos(angle);
   return (rx + cx, ry + cy);

def hypot(p1, p2):
   return math.sqrt((p1[0] - p2[0]) * (p1[0] - p2[0]) +
			(p1[1] - p2[1]) * (p1[1] - p2[1]));

def do_a_line(threshold, p1, p2):
   d = hypot(p1, p2);
   seglen = linespacing;
   nsegs = int(d / seglen);
   if nsegs == 0:
     return;
   pendown = 0;
   startx = p1[0];
   starty = p1[1];

   dx = (p2[0] - p1[0]) / nsegs;
   dy = (p2[1] - p1[1]) / nsegs;
   for i in range(0, nsegs - 1):
      x1 = p1[0] + dx * i;
      y1 = p1[1] + dy * i;
      x2 = p1[0] + dx * (i + 1);
      y2 = p1[1] + dy * (i + 1);
      mx = ((x2 - x1) / 2.0) + x1;
      my = ((y2 - y1) / 2.0) + y1;
      s = sampleimg(mx, my);
      if s <= threshold:
         if pendown != 1:
            pendown = 1;
            print >> myfile, "start line ", x1, y1
            startx = x1;
            starty = y1;
         else:
            if pendown == 1 and i == nsegs - 2:
               print >> myfile, "end line ", x2, y2;
	       print >> svgfile, "M ", startx, starty, "L ", x2, y2
               pygame.draw.line(screen, black, (startx, starty), (x1, y1), 1);
               pendown = 0;
      else:
         if pendown == 1:
            pendown = 0;
            print >> myfile, "end line ", x2, y2;
            print >> svgfile, "M ", startx, starty, "L ", mx, my
            pygame.draw.line(screen, black, (startx, starty), (mx, my), 1);

def is_zero(v):
  if v > -0.0000001 and v < 0.0000001:
    return True;
  return False;

def point_inside(clip_window, x, y):
  return x >= clip_window[0] and x <= clip_window[2] and y >= clip_window[1] and y <= clip_window[3];

def clipT(num, denom, tE, tL):
  if is_zero(denom):
    return (num < 0.0, tE, tL);
  t = num / denom;
  if (denom > 0.0):
    if t > tL:
      return (False, tE, tL);
    if t > tE:
	tE = t;
  else:
    if t < tE:
      return (False, tE, tL);
    if t < tL:
      tL = t;
  return (True, tE, tL);

def clip_line(left, top, right, bottom, x1, y1, x2, y2):
  clip = (left, top, right, bottom)
  dx = x2 - x1;
  dy = y2 - y1;
  if is_zero(dx) and is_zero(dy) and point_inside(clip, x1, y1):
    return (True, x1, y1, x2, y2);
  tE = 0;
  tL = 1;
  cr = clipT(clip[0] - x1, dx, tE, tL);
  tE = cr[1];
  tL = cr[2];
  if cr[0]:
    cr = clipT(x1 - clip[2], -dx, tE, tL);
    tE = cr[1];
    tL = cr[2];
    if cr[0]:
      cr = clipT(clip[1] - y1, dy, tE, tL);
      tE = cr[1];
      tL = cr[2];
      if cr[0]:
        cr = clipT(y1 - clip[3], -dy, tE, tL);
        tE = cr[1];
        tL = cr[2];
        if cr[0]:
          if tL < 1:
            x2 = x1 + tL * dx;
            y2 = y1 + tL * dy;
          if tE > 0:
            x1 = x1 + tE * dx;
            y1 = y1 + tE * dy;
          return (True, x1, y1, x2, y2);
  return (False, x1, y1, x2, y2);

def do_layer(layer, threshold, angle):
   count = int((radius * 2.0) / linespacing);
   cx = screen_width / 2.0;
   cy = screen_height / 2.0;
   for i in range(-count / 2, count / 2):
      x1 = cx + (i * linespacing);
      y1 = cy - radius * 2;
      x2 = x1;
      y2 = cy + radius * 2;
      p1 = rotate_point((x1, y1), (cx, cy), angle);
      p2 = rotate_point((x2, y2), (cx, cy), angle); 

      clipped_line = clip_line(0, 0, screen_width, screen_height, p1[0], p1[1], p2[0], p2[1]);
      if not clipped_line[0]:
         continue;
      p1 = (clipped_line[1], clipped_line[2])
      p2 = (clipped_line[3], clipped_line[4])
      do_a_line(threshold, p1, p2);
      pygame.display.update()

screen.fill(white)
for i in range(1, nlayers):
   do_layer(i, i * 256 / nlayers, i * 127 * math.pi / 180.0);

myfile.close();

print >> svgfile, "Z \" style=\"fill:none;stroke:black;stroke-width:1\"/>"
print >> svgfile, "</svg>"
svgfile.close();

pygame.image.save(screen, "output.png");
print
print
print "Saved output image to output.png, lines.txt, and lines.svg"
print
print


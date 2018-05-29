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
import Image
import random
import math
import time

imagename = "mona-lisa.jpg";
# imagename = "cyclekart-blue.jpg";
if (len(sys.argv) >= 2):
  imagename = sys.argv[1];

im = Image.open(imagename)

pix = im.load()
image_width = 0.0 + im.size[0];
image_height = 0.0 + im.size[1];
screen_width = 2500 
screen_height = int(screen_width * image_height / image_width);
print image_width, image_height, screen_width, screen_height

# origin on screen
osx = 0;
osy = 0;

white = (0, 0, 0)
black = (255, 255, 255)
cyan = (0, 255, 255)
yellow = (255, 255, 0)
magenta = (255, 0, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
rgb_not_cmy = 1;
cmy = (cyan, magenta, yellow)
rgb = (red, green, blue)

if (rgb_not_cmy):
	colortriad = rgb;
else:
	colortriad = cmy;
	
nlayers = 15;
linespacing = 20;

myfile = open('lines.txt', 'w+');

radius = math.sqrt(2.0) * (1.1 * screen_height);

if screen_width > screen_height:
   radius = math.sqrt(2.0) * (1.1 * screen_width)

screen = pygame.display.set_mode([screen_width, screen_height])
pygame.display.update()

def max3(a, b, c):
   if (a > b and a > c):
      return a;
   if (b > c):
      return b;
   return c;

def rgb_to_cmy(color):
   rf = color[0] / 255.0;
   gf = color[1] / 255.0;
   bf = color[2] / 255.0;
   k = 1.0 - max3(rf, gf, bf);
   if (k > 0.99999):
      return (0, 0, 0);
   c = (1.0 - rf - k) / (1.0 - k);
   m = (1.0 - gf - k) / (1.0 - k);
   y = (1.0 - bf - k) / (1.0 - k);
   return (c, m, y);

# screen x to image x
def sxtoix(sx):
  return (image_width * sx) / screen_width;

def sytoiy(sy):
  return (image_height * sy) / screen_height;

def sampleimg(sx, sy, color):
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
   if (rgb_not_cmy):
      return pix[ix, iy][color];
   else:
      return rgb_to_cmy(pix[ix, iy])[color] * 255;

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

def do_a_line(threshold, p1, p2, color):
   d = hypot(p1, p2);
   seglen = linespacing;
   nsegs = int(d / seglen);
   if nsegs == 0:
     return;
   pendown = 0;

   dx = (p2[0] - p1[0]) / nsegs;
   dy = (p2[1] - p1[1]) / nsegs;
   for i in range(0, nsegs - 1):
      x1 = p1[0] + dx * i;
      y1 = p1[1] + dy * i;
      x2 = p1[0] + dx * (i + 1);
      y2 = p1[1] + dy * (i + 1);
      mx = ((x2 - x1) / 2.0) + x1;
      my = ((y2 - y1) / 2.0) + y1;
      s = sampleimg(mx, my, color);
      if s >= threshold:
         if pendown != 1:
            pendown = 1;
            print >> myfile, "start line ", x1, y1
         pygame.draw.line(screen, colortriad[color], (x1, y1), (x2, y2), 1);
      else:
         if pendown == 1:
            pendown = 0;
            print >> myfile, "end line ", x1, y1;

      if pendown == 1:
            pendown = 0;
            print >> myfile, "end line ", x1, y1;

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

def do_layer(layer, threshold, angle, color):
   count = int((radius * 2.0) / linespacing);
   cx = screen_width / 2.0;
   cy = screen_height / 2.0;
   for i in range(-count / 2, count / 2):
      x1 = cx + (i * linespacing) + color;
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
      do_a_line(threshold, p1, p2, color);
      pygame.display.update()

screen.fill(white)

for i in range(1, nlayers):
   for color in range(0, 3):
      do_layer(i, i * 256 / nlayers, (i * 127 + color * 7) * math.pi / 180.0, color);

myfile.close();

pygame.image.save(screen, "output.png");
print
print
print "Saved output image to output.png"
print
print


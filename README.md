Crosshatcher
============

Crosshatcher renders an image in a crosshatching technique via an
interesting method.

Note, the image must be grayscale (to convert to grayscale in Gimp, Image->Mode->grayscale)

By default the input image is in "image.jpg".
Output files are: "output.png" and "lines.txt", and "lines.svg".

You can specify the input image and output file width and line spacing.
For example:

  ./crosshatcher input-file.jpg 1000 10

uses input-file.jpg as the input file, and produces output 1000 units wide
with line spacing of 10 units.


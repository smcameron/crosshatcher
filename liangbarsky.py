# This software is distributed under the Public Domain.
#
# In cases, where the law prohibits the recognition of Public Domain
# software, this software can be licensed under the zlib lincese as
# stated below:
#
# Copyright (C) 2012 Marcus von Appen <marcus@sysfault.org>
# 
# This software is provided 'as-is', without any express or implied
# warranty. In no event will the authors be held liable for any damages
# arising from the use of this software.
# 
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
# 
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.

def liangbarsky(left, top, right, bottom, x1, y1, x2, y2):
    """Clips a line to a rectangular area.

    This implements the Liang-Barsky line clipping algorithm.  left,
    top, right and bottom denote the clipping area, into which the line
    defined by x1, y1 (start point) and x2, y2 (end point) will be
    clipped.

    If the line does not intersect with the rectangular clipping area,
    four None values will be returned as tuple. Otherwise a tuple of the
    clipped line points will be returned in the form (cx1, cy1, cx2, cy2).
    """
    dx = x2 - x1
    dy = y2 - y1
    dt0, dt1 = 0, 1

    checks = ((-dx, x1 - left),
              (dx, right - x1),
              (-dy, y1 - top),
              (dy, bottom - y1))

    for p, q in checks:
        if p == 0 and q < 0:
            return None, None, None, None
        dt = q / (p * 1.0)
        if p < 0:
            if dt > dt1:
                return None, None, None, None
            dt0 = max(dt0, dt)
        else:
            if dt < dt0:
                return None, None, None, None
            dt1 = min(dt1, dt)
    if dt0 > 0:
        x1 += dt0 * dx
        y1 += dt0 * dy
    if dt1 < 1:
        x2 = x1 + dt1 * dx
        y2 = y1 + dt1 * dy
    return x1, y1, x2, y2

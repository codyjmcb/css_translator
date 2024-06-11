"""
File: classDefs.py
Name: Cody J. McBride
Contact: cody.mcbride@unh.edu
Description: This file contains the class definitions for the data types used by AI/S100 SVGs
Version: 0.1
Date: 07/17/2023
General Notes:
Version History
[0.1]
    Created file
    Added the following classes
        [S100]
            Rect
        [Illustrator]
            cssClass
            Rect
            Circle
            Line
            Path
"""
import math
import re
import matplotlib.pyplot as plt
import numpy
import bezier
import numpy as np
from scipy import interpolate
from scipy.optimize import curve_fit
from scipy.interpolate import CubicSpline


# TODO change a to something meaningful (class)
class s100Rect:
    def __init__(self):
        self.a = 0
        self.x = 0
        self.y = 0
        self.height = 0
        self.width = 0
        self.style = 0
        pass

    def __str__(self):
        return f"<rect x=\"{self.x}\" y=\"{self.y}\" height=\"{self.height}\" width=\"{self.width}\" " \
               f"class=\"{self.a}\" style=\"{self.style}\" />\n"


'''
    Contains Style Information
    Each "style" gets made into a css class
    Each "shape" that uses the same styling uses the same css class
    Classes containing no stroke width are the default 1pt
    Fill and Stroke are hex color codes (#FFFFFF)
'''
class illustratorCssClass:
    def __init__(self):
        self.name = 0
        self.fill = 0
        self.stroke = 0
        self.strokeMiterLimit = 0
        self.strokeWidth = 1
        self.opacity = 1.0

    def __str__(self):
        return f"\t{self.name}" "{" f"fill:{self.fill};stroke:{self.stroke};stroke-width:{self.strokeWidth};stroke-miterlimit:{self.strokeMiterLimit};" "}\n"


'''
    Default rectangle shape (non-rounded corners, unmodified)
    x,y is the center of the rectangle
    x/y + 0.5(width/height) gives you the edges of the rectangle
    _class is the css styling added by Illustrator
    
    <rect x="298.5" y="421" class="st0" width="233" height="178"/>
    
    Class Members:
        x               x-coordinate for the center of the rectangle
        y               y-coordinate for the center of the rectangle
        width           width of the rectangle
        height          height of the rectangle
        style
        strokeWidth
        opacity
'''
class illustratorRect:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.style = 0
        self.strokeWidth = 0.32  #default
        self.opacity = 1.0
        self.transformation = -1

    def hasTransformation(self):
        if self.transformation == -1:
            return False
        else:
            return True

    def hasStrokeWidth(self):
        if self.style != 0:
            if self.style.strokeWidth == 1:
                return self.strokeWidth
            else:
                return self.style.strokeWidth
        return self.strokeWidth

    def hasOpacity(self):
        if self.opacity == 1.0:
            return False
        else:
            return True

    def buildString(self):
        if self.hasTransformation():
            return self.buildTransformation()
        else:
            return f"<rect x=\"{round(self.x - 0.5 * self.width * 0.3527777778, 2)}\" " \
                   f"y=\"{round(self.y - 0.5 * self.height * 0.3527777778, 2)}\" height=\"{self.height}\" " \
                   f"width=\"{self.width}\" " + self.addClass() + f"style=\"stroke-width:{self.strokeWidth};\" />"

    def buildTransformation(self):
        cx = self.x - 0.5 * self.width * 0.3527777778
        cy = self.y - 0.5 * self.height * 0.3527777778
        theta = abs(round(math.degrees(math.atan2(self.transformation[1], self.transformation[0]))))
        x1 = round(cx - (0.5 * self.width * math.cos(math.radians(theta))), 3)
        y1 = round(cy + (0.5 * self.width * math.sin(math.radians(theta))), 3)
        x2 = round(cx + (0.5 * self.width * math.cos(math.radians(theta))), 3)
        y2 = round(cy - (0.5 * self.width * math.sin(math.radians(theta))), 3)

        p1x = round(x1 - (0.5 * self.height * math.sin(math.radians(theta))), 3)
        p1y = round(y1 - (0.5 * self.height * math.cos(math.radians(theta))), 3)

        p2x = round(x2 - (0.5 * self.height * math.sin(math.radians(theta))), 3)
        p2y = round(y2 - (0.5 * self.height * math.cos(math.radians(theta))), 3)

        p3x = round(x2 + (0.5 * self.height * math.sin(math.radians(theta))), 3)
        p3y = round(y2 + (0.5 * self.height * math.cos(math.radians(theta))), 3)

        p4x = round(x1 + (0.5 * self.height * math.sin(math.radians(theta))), 3)
        p4y = round(y1 + (0.5 * self.height * math.cos(math.radians(theta))), 3)

        return f"<path d=\" M {p1x},{p1y} L {p2x},{p2y} L {p3x},{p3y} L {p4x},{p4y}, L {p1x},{p1y}\"" + self.addClass() + f"style=\"stroke-width:{self.hasStrokeWidth() * 0.32};\" />"

    def addClass(self):
        if self.style != 0:
            if self.style.fill != 0:
                if self.style.fill == 'none':
                    return f"fill=\"{self.style.fill}\" class=\"s{self.style.stroke}\" "
                else:
                    return f"class=\"s{self.style.stroke} f{self.style.fill}\" "
            return f"class=\"s{self.style.stroke} f#000000\" "  # AI defaults to black fill
        return ""

    def __str__(self):
        return self.buildString()


class illustratorCircle:
    def __init__(self):
        self.cx = 0
        self.cy = 0
        self.r = 0
        self.style = 0
        self.strokeWidth = 0.32
        self.transformation = -1

    def hasStrokeWidth(self):
        if self.style != 0:
            if self.style.strokeWidth == 1:
                return self.strokeWidth
            else:
                return self.style.strokeWidth
        return self.strokeWidth

    def hasOpacity(self):
        if self.opacity == 1.0:
            return False
        else:
            return True

    def buildString(self):
        print('debug')
        return f"<circle cx=\"{round(self.cx, 3)}\" cy=\"{round(self.cy, 3)}\" r=\"{round(self.r, 3)}\" " + self.addClass() + f" style=\"stroke-width:{self.hasStrokeWidth() * 0.32};\" />"

    def addClass(self):
        if self.style != 0:
            if self.style.fill != 0:
                if self.style.fill == 'none':
                    return f"fill=\"{self.style.fill}\" class=\"s{self.style.stroke}\" "
                else:
                    return f"class=\"s{self.style.stroke} f{self.style.fill}\" "
        else:
            return ""

    def __str__(self):
        return self.buildString()

'''
    Default circle/ellipse shape
    cx,cy is the center of the ellipse
    rx/ry are the x/y radii (for a perfect circle these would be equal)
    _class is the css styling added by Illustrator
    
    <ellipse class="st1" cx="298" cy="421" rx="116.5" ry="89" />
    
    Class Members:
        cx              x-coordinate for the center of the circle           
        cy              y-coordinate for the center of the circle
        rx              radius of the ellipse along the x-axis
        ry              radius of the ellipse along the y-axis
        style
'''
class illustratorEllipse:
    def __init__(self):
        self.cx = 0
        self.cy = 0
        self.rx = 0
        self.ry = 0
        self.strokeWidth = 0.32
        self.style = 0
        self.transformation = -1

    def hasStrokeWidth(self):
        if self.style.strokeWidth == 1:
            return self.strokeWidth
        else:
            return self.style.strokeWidth

    def hasOpacity(self):
        if self.opacity == 1.0:
            return False
        else:
            return True

    def buildString(self):
        return self.tempSTR()
        #return f"<ellipse cx=\"{self.cx}\" cy=\"{self.cy}\" rx=\"{self.rx}\" ry=\"{self.ry}\" " + self.addClass() + f" style=\"stroke-width:{self.hasStrokeWidth() * 0.32};\" />"

    def addClass(self):
        if self.style.fill != 0:
            return f"fill=\"{self.style.fill}\" class=\"s{self.style.stroke}\""
        return f"class=\"s{self.style.stroke}\""

    def __str__(self):
        return self.buildString()
        #return f"<ellipse class=\"{self.style}\" cx=\"{self.cx}\" cy=\"{self.cy}\" rx=\"{self.rx}\" ry=\"{self.ry}\" />\n"

    def tempSTR(self):
        return f"<path d=\" M {round((self.cx - self.rx) + 0.5 * self.rx * 0.3527777778, 3)},{round((self.cy - self.ry) + 0.5 * self.rx * 0.3527777778, 3)} " \
               f"a {self.rx},{self.ry},0,1,0,{round(self.cx + self.rx, 3)},{self.cy} a {self.rx},{self.ry},0,1,0,{round(-1 * (self.cx + self.rx), 3)},{self.cy}Z\" " \
               f"" + self.addClass() + f" style=\"stroke-width:{self.hasStrokeWidth() * 0.32};\" />"

'''
    Default straight line
    x1,y1 is the starting point for the line
    x2,y2 is the ending point for the line
    _class is the css styling added by Illustrator

    <line class="st1" x1="414.5" y1="332" x2="298" y2="421"/>
'''
class illustratorLine:
    def __init__(self):
        self.x1 = 0
        self.x2 = 0
        self.y1 = 0
        self.y2 = 0
        self.style = 0

    def __str__(self):
        return f"<path d=\"M {round(self.x1, 3)},{round(self.y1, 3)} L {round(self.x2, 3)},{round(self.y2, 3)}\" " + self.addClass() + f"style=\"stroke-width:{self.hasStrokeWidth() * 0.32};\" />"

    def addClass(self):
        if self.style != 0:
            if self.style.fill != 0:
                return f"fill=\"{self.style.fill}\" class=\"s{self.style.stroke}\" "
            return f"class=\"s{self.style.stroke}\" "
        return ""

    def hasStrokeWidth(self):
        if self.style != 0:
            if self.style.strokeWidth == 1:
                return self.strokeWidth
            else:
                return self.style.strokeWidth
        return 1
    pass

def fit_func(x, a, b):
    return a * np.exp(b*x)

def bezier_curve(t, *params):
    n = len(params) // 2
    control_points = np.array(params).reshape((n, 2))
    basis = np.array([(1 - t) ** (n - i - 1) * t ** i for i in range(n)]).T
    return basis @ control_points

class illustratorPath:
    def __init__(self):
        self.style = -1
        self.points = 0

    def __str__(self):
        curX = float(0)
        curY = float(0)
        ret = "<path d=\" "
        for p in self.points:
            if p.find("M") >= 0:
                coord = re.findall('[0-9.]+', p)
                curX = (float(coord[0]) / 100)
                curY = (float(coord[1]) / 100)
                ret = ret + f"M {curX.__str__()},{curY.__str__()} "
            if p.find("H") >= 0:
                coord = re.findall('[0-9.]+', p)
                curX = (float(coord[0]) / 100)
                ret = ret + f"L {curX.__str__()},{curY.__str__()} "
            if p.find("h") >= 0:
                coord = re.findall('[0-9.]+', p)
                curX = curX + (float(coord[0]) / 100)
                ret = ret + f"L {curX.__str__()},{curY.__str__()} "
            if p.find("V") >= 0:
                coord = re.findall('[0-9.]+', p)
                curY = (float(coord[0]) / 100)
                ret = ret + f"L {curX.__str__()},{curY.__str__()} "
            if p.find("v") >= 0:
                coord = re.findall('[0-9.]+', p)
                curY = curY + (float(coord[0]) / 100)
                ret = ret + f"L {curX.__str__()},{curY.__str__()} "
            if p.find("C") >= 0:
                coord = re.findall('-?[0-9.]+', p)
                print("absolute C " + "(" + coord[0] + "," + coord[1] + ")\t(" + coord[2] + "," + coord[3] + ")\t(" + coord[4] + "," + coord[5] + ")")
                x1 = round((float(coord[0]) / 100), 3)
                y1 = round((float(coord[1]) / 100), 3)
                x2 = round((float(coord[2]) / 100), 3)
                y2 = round((float(coord[3]) / 100), 3)
                deltaY = y2 - y1
                y2 = y2 - 2 * deltaY

                x3 = round((float(coord[4]) / 100), 3)
                y3 = round((float(coord[5]) / 100), 3)
                y3 = y3 - 2 * deltaY

                x_data = np.array([x1, x2, x3])
                y_data = np.array([y1, y2, y3])

                params, params_covariance = curve_fit(fit_func, x_data, y_data)
                granularity = 5
                delta = x1 - x3
                offset = float(delta / granularity)
                startingY = y1
                for x in range(granularity):
                    xval = x1 - (x * offset)
                    yval = round(fit_func(xval, params[0], params[1]), 3)
                    ret = ret + f"L {xval},{startingY + (startingY - yval)} "
                    print(f"({xval},{startingY + (startingY - yval)})")

            if p.find("c") >= 0:
                coord = re.findall('-?[0-9.]+', p)
                print("relative c " + "(" + coord[0] + "," + coord[1] + ")\t(" + coord[2] + "," + coord[3] + ")\t(" + coord[4] + "," + coord[5] + ")")
                x1 = curX
                y1 = curY

                curX = x1
                curY = y1

                x2 = round((float(coord[2]) / 100), 3) + curX
                y2 = round((float(coord[3]) / 100), 3) + curY

                curX = x2
                curY = y2

                x3 = round((float(coord[4]) / 100), 3) + curX
                y3 = round((float(coord[5]) / 100), 3) + curY

                curX = x3
                curY = y3

                x_data = [x1, x2, x3]
                y_data = [y1, y2, y3]

                cs = interpolate.CubicSpline(x_data, y_data)

                granularity = 10
                delta1 = x_data[1] - x_data[0]

                for x in range(granularity):
                    val = round((float(x / granularity) * delta1) + x_data[0], 3)
                    ret = ret + f"L {val}, {cs(val)} "

                delta2 = x_data[2] - x_data[1]

                for x in range(granularity):
                    val = round((float(x / granularity) * delta2) + x_data[1], 3)
                    ret = ret + f"L {val}, {cs(val)} "

                #ret = ret + f"L {x_data[0]},{cs(x_data[0])} "
                #ret = ret + f"L {x_data[1]},{cs(x_data[1])} "
                #ret = ret + f"L {x_data[2]},{cs(x_data[2])} "
                pass
            if p.find("z") >= 0:
                ret = ret + "z"
                pass

        ret = ret + "\" class=\"s1 f0 sCHBLK\" style=\"stroke-width:0.32;\"/>"
        return ret

class illustratorPolygon:
    def __init__(self):
        self.style = -1
        self.startingPoint = 0
        self.points = 0
        self.vbHeight = 0
        self.vbWidth = 0

    def __str__(self):
        self.startingPoint = self.startingPoint.split(",")
        ret = f"<path d=\"M {float(self.startingPoint[0]) * 0.3527777778 * 0.039408866995 - (self.vbWidth / 2) * 0.3527777778 * 0.039408866995}," \
              f"{float(self.startingPoint[1]) * 0.3527777778 * 0.039408866995 - (self.vbHeight / 2) * 0.3527777778 * 0.039408866995} "
        lastPoint = None
        for p in self.points:
            coord = p.split(",")
            ret = ret + f"L {float(coord[0]) * 0.3527777778 * 0.039408866995 - (self.vbWidth / 2) * 0.3527777778 * 0.039408866995}," \
                        f"{float(coord[1]) * 0.3527777778 * 0.039408866995 - (self.vbHeight / 2) * 0.3527777778 * 0.039408866995} "

        ret = ret + f"L {float(self.startingPoint[0]) * 0.3527777778 * 0.039408866995 - (self.vbWidth / 2) * 0.3527777778 * 0.039408866995}," \
                    f"{float(self.startingPoint[1]) * 0.3527777778 * 0.039408866995 - (self.vbHeight / 2) * 0.3527777778 * 0.039408866995}\" "
        ret = ret + "class=\"s#00AEEF\" style=\"stroke-width:0.32;\" />"
        return ret

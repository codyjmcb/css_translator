"""
File: main.py
Name: Cody J. McBride
Contact: cody.mcbride@unh.edu
Description: XML to IHO-schema SVG files for the Center for Coastal and Ocean Mapping (CCOM)
Version: 0.2
Date: 07/17/2023
General Notes:
    Adobe Illustrator defines css classes for style information.
        an example:
               .st1{fill:#FFFFFF;stroke:#39B54A;stroke-width:2;stroke-miterlimit:10;}
                    fill color    outline color  pen width         ???
    These style classes get consumed by drawn items:
        an example
            <rect x="298.5" y="421" class="st0" width="233" height="178"/>

    Adobe Illustrator defines location 0,0 as the top left corner of the page
    S100 toolkit defines location 0,0 as the center of the page
    The calculated X/Y offsets assume using the A4 Adobe Illustrator Template (default)

Version History
[0.1]
    Initial GUI project with 2 buttons
        1 button allows the user to select a file
            Selected file gets parsed into lines
            The lines are printed to the console
        1 button that quits the program
    Includes 2 text boxes
        1 for the full file path of the selected file
        1 for the file name
[0.2]
    Added classDefs.py (see that file for revision history)
    Added stringConstants.py (see that file for revision history)
[0.3]
    Added parsing functions to parse out Illustrator:
        Rect
        Ellipse (Circle)
        Line
        StyleClasses
"""
import math
import numpy as np
import os

# import UI libraries
import tkinter
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# import items from other project files
from classDefs import illustratorRect, illustratorCssClass, illustratorCircle, illustratorLine, illustratorEllipse, illustratorPath, illustratorPolygon
from stringConstants import XML_VERSION, STYLE_SHEET, METADATA, PIVOT_POINT, buildTitle, buildDescription, DEFAULT_TITLE, DEFAULT_DESCRIPTION

# import regular expression library
import re

# define global variables
newFile = ""
items = []
classes = []
viewBoxWidth = 0
viewBoxHeight = 0
title = DEFAULT_TITLE
description = DEFAULT_DESCRIPTION
filePointer = None
folder = None

# TODO: button_listener should just get the file to convert
# TODO: split responsibility unto multiple methods
def button_listener(sFolder, sFile, dFile):
    global items
    global classes
    global newFile
    global title
    global description
    global filePointer
    global folder

    filename = filedialog.askopenfile(mode='r')  # returns <_io.TextIOWrapper name='{FILE_PATH}/{FILE_NAME}' mode='r' encoding='cp1252'>
    filePointer = open(filename.name, "r")  # filename.name is the file, 'r' for read
    sFolder.config(state='normal')
    sFile.config(state='normal')
    sFolder.insert(tkinter.END, filePointer.name)
    folder = os.path.dirname(filePointer.name)
    sFile.insert(tkinter.END, os.path.basename(filePointer.name))
    dFile.insert("1.0", "converted_" + os.path.basename(filePointer.name))
    sFolder.update()
    sFile.update()
    sFolder.config(state='disabled')
    sFile.config(state='disabled')
    sFolder.master.update()


def button_listener_destination(dFolder):
    folder = filedialog.askdirectory()
    dFolder.delete("1.0", 'end')
    dFolder.insert("1.0", folder)

def button_listener_convert(sFolder, sFile, dFolder, dFile):
    try:
        global filePointer
        global newFile
        global folder
        newFolder = folder
        folderCheck = dFolder.get("1.0", "end")
        if folderCheck.find("optional") >= 0:
            pass
        else:
            newFolder = folderCheck

        newFile = newFolder.__str__() + "/" + dFile.get("1.0", "end")
        newFile = newFile.replace("\n", "")
        y = filePointer.read()

        # TODO: Explain this RegEx
        # lines = re.findall("<[^>]*>|..*}", y)
        lines = re.findall("<text[a-zA-Z0-9 \"=:)(><\/.]+|<[^>]*>|..*}", y)

        for x in lines:  # this is functionally equivalent to _while(file.readline() != null)_
            if x.find("<rect") >= 0:
                temp = parseRect(x)
                if temp.hasTransformation():
                    items.append(tempFunc(temp))
                else:
                    items.append(temp)
            if x.find(".st") >= 0:
                classes.append(parseClass(x))
            if x.find("<ellipse") >= 0:
                temp = parseEllipse(x)
                #    items.append(tempEllipseFunc(temp))
                items.append(temp)
            if x.find("<circle") >= 0:
                items.append(parseCircle(x))
            if x.find("<line") >= 0:
                items.append(parseLine(x))
            if x.find("<svg") >= 0:
                parseHeader(x)
            if x.find("<path") >= 0:
                items.append(parsePath(x))
            if x.find("<text") >= 0:
                parseText(x)
            if x.find("<polygon") >= 0:
                items.append(parsePolygon(x))
        writeNewFile(newFile)
        resetApp(sFolder, sFile, dFolder, dFile)
        tkinter.messagebox.showinfo("Conversion Successful", "Success!")
    except Exception as e:
        #this should be error
        tkinter.messagebox.showinfo("Error", str(e))
        print(str(e))
    pass

def resetApp(sFolder, sFile, dFolder, dFile):
    global title
    global description
    items.clear()
    classes.clear()
    title = DEFAULT_TITLE
    description = DEFAULT_DESCRIPTION
    sFolder.config(state='normal')
    sFile.config(state='normal')
    sFolder.delete(1.0, 'end')
    sFile.delete(1.0, 'end')
    sFolder.config(state="disabled")
    sFile.config(state="disabled")
    dFolder.delete(1.0, "end")
    dFolder.insert(1.0, "optional (if different than source folder)")
    dFile.delete(1.0, "end")

def parseText(text):
    global title
    global description
    s = re.findall('>.*<', text)

    for item in s:
        if item.find("Title:") >= 0:
            t = re.findall("[a-zA-Z0-9 ]+", item)
            title = t[1]
        if item.find("Description:") >= 0:
            t = re.findall("[a-zA-Z0-9 ]+", item)
            description = t[1]

def tempEllipseFunc(ell):
    theta = abs(round(math.degrees(math.atan2(ell.transformation[1], ell.transformation[0]))))
    spx = round(ell.cx - (ell.rx * math.cos(math.radians(theta))), 3)
    spy = round(ell.cy + (ell.rx * math.sin(math.radians(theta))), 3)
    epx = round(ell.cx + (ell.rx * math.cos(math.radians(theta))), 3)
    epy = round(ell.cy - (ell.rx * math.sin(math.radians(theta))), 3)

    return f"<path d=\" M {spx},{spy} a {ell.rx},{ell.ry},0,1,0,{epx},{epy} a {ell.rx},{ell.ry},0,1,0,{-1 * spx},{-1 * spy}Z\" class=\"s1 f0 sCHBLK\" style=\"stroke-width:0.32;\" />"
    pass

#TODO: Explain what is going on here
#TODO: Move this into rect class
# NOTE: this has the correct corner points for the translated rectangle
def tempFunc(rec):
    cx = rec.x + 0.5 * rec.width
    cy = rec.y + 0.5 * rec.height
    theta = abs(round(math.degrees(math.atan2(rec.transformation[1], rec.transformation[0]))))
    x1 = round(cx - (0.5 * rec.width * math.cos(math.radians(theta))), 3)
    y1 = round(cy + (0.5 * rec.width * math.sin(math.radians(theta))), 3)
    x2 = round(cx + (0.5 * rec.width * math.cos(math.radians(theta))), 3)
    y2 = round(cy - (0.5 * rec.width * math.sin(math.radians(theta))), 3)

    p1x = round(x1 - (0.5 * rec.height * math.sin(math.radians(theta))), 3)
    p1y = round(y1 - (0.5 * rec.height * math.cos(math.radians(theta))), 3)

    p2x = round(x2 - (0.5 * rec.height * math.sin(math.radians(theta))), 3)
    p2y = round(y2 - (0.5 * rec.height * math.cos(math.radians(theta))), 3)

    p3x = round(x2 + (0.5 * rec.height * math.sin(math.radians(theta))), 3)
    p3y = round(y2 + (0.5 * rec.height * math.cos(math.radians(theta))), 3)

    p4x = round(x1 + (0.5 * rec.height * math.sin(math.radians(theta))), 3)
    p4y = round(y1 + (0.5 * rec.height * math.cos(math.radians(theta))), 3)

    return f"<path d=\" M {p1x},{p1y} L {p2x},{p2y} L {p3x},{p3y} L {p4x},{p4y}, L {p1x},{p1y}\" class=\"s1 f0 sCHBLK\" style=\"stroke-width:0.32;\" />"

def parseRect(st):
    ret = illustratorRect()

    #TODO: Explain this RegEx
    fields = re.findall('[a-z]+=\"[a-z(0-9.) -]+\"', st)

    for f in fields:
        if f.find("x=") >= 0:
            x = re.findall('[0-9.]+', f)
            ret.x = (float(x[0]) - (viewBoxWidth / 2)) / 100
            pass
        if f.find("y=") >= 0:
            y = re.findall('[0-9.]+', f)
            ret.y = (float(y[0]) - (viewBoxHeight / 2)) / 100
            pass
        if f.find("class=") >= 0:
            sty = re.findall('st[0-9]*', f)
            for c in classes:
                if c.name == "." + sty[0]:
                    ret.style = c
            pass
        if f.find("width=") >= 0:
            width = re.findall('[0-9.]+', f)
            ret.width = round(float(width[0]) * 0.3527777778 * 0.039408866995, 2)
            pass
        if f.find("height=") >= 0:
            height = re.findall('[0-9.]+', f)
            ret.height = round(float(height[0]) * 0.3527777778 * 0.039408866995, 2)
            pass
        if f.find("transform=\"matrix") >= 0:
            values = re.findall('-?[0-9.]+', f)

            ret.transformation = list(map(float, values))

    return ret
    pass

'''
    If the fill is the same as the stroke, it is left out
'''
def parseClass(cl):
    ret = illustratorCssClass()
    name = re.findall('.st[0-9]*', cl)
    ret.name = name[0]

    if cl.find('fill') >= 0:
        fill = re.findall('fill:#[0-9A-Fa-f]*|fill:none;', cl)
        fill2 = re.findall('#[0-9a-fA-F]{6}|none', fill[0])
        ret.fill = fill2[0]

    if cl.find('stroke:') >= 0:
        stroke = re.findall('stroke:#[0-9A-Fa-f]*;', cl)
        stroke2 = re.findall('#[0-9a-fA-F]{6}', stroke[0])
        ret.stroke = stroke2[0]

    if cl.find('stroke-width') >= 0:
        strokeWidth = re.findall('stroke-width:[0-9]+', cl)
        strokeWidth2 = re.findall('[0-9]+', strokeWidth[0])
        ret.strokeWidth = float(strokeWidth2[0]) * 0.32

    # opacity only appears if not 100% and there is a fill
    if cl.find('opacity') >= 0:
        opacity = re.findall('opacity:[0-9].[0-9]', cl)
        opacity2 = re.findall('[0-9].[0-9]', opacity[0])
        ret.opacity = float(opacity2[0])
        pass

    if cl.find('stroke-miterlimit:') >= 0:
        miter = re.findall('stroke-miterlimit:[0-9]+', cl)
        miter2 = re.findall('[0-9]+', miter[0])
        ret.strokeMiterLimit = miter2[0]

    return ret

# TODO: Stress test this
def parseEllipse(e):
    ret = illustratorEllipse()
    fields = re.findall('[a-z]+=\"[a-z(0-9.) -]+\"', e)
    for f in fields:
        if f.find("cx=") >= 0:
            cx = re.findall('[0-9.]+', f)
            ret.cx = round((float(cx[0]) - (viewBoxWidth / 2)) / 100, 3)
            pass
        if f.find("cy=") >= 0:
            cy = re.findall('[0-9.]+', f)
            ret.cy = round((float(cy[0]) - (viewBoxHeight / 2)) / 100, 3)
            pass
        if f.find("rx=") >= 0:
            rx = re.findall('[0-9.]+', f)
            ret.rx = round(float(rx[0]) * 0.3527777778 * 0.039408866995, 3)
            pass
        if f.find("ry=") >= 0:
            ry = re.findall('[0-9.]+', f)
            ret.ry = round(float(ry[0]) * 0.3527777778 * 0.039408866995, 3)
            pass
        if f.find("class=") >= 0:
            sty = re.findall('st[0-9]*', f)
            for c in classes:
                if c.name == "." + sty[0]:
                    ret.style = c
            pass
        if f.find("transform=\"matrix") >= 0:
            values = re.findall('-?[0-9.]+', f)
            ret.transformation = list(map(float, values))
    return ret

def parsePath(p):
    ret = illustratorPath()
    fields = re.findall('[a-z]+=\"[a-z(0-9.) -]+\"|d=\".+\s?.+\"', p)
    for f in fields:
        if f.find("class=") >= 0:
            pass
        if f.find("d=") >= 0:
            path = re.findall('[a-zA-Z][0-9.,-]+|z', f)
            ret.points = path
            for segment in path:
                print(segment)
            pass

    return ret

def parseCircle(line):
    ret = illustratorCircle()
    fields = re.findall('[a-z]+=\"[a-z(0-9.) -]+\"', line)
    for f in fields:
        if f.find("cx=") >= 0:
            cx = re.findall('[0-9.]+', f)
            ret.cx = (float(cx[0]) - (viewBoxWidth / 2)) / 100
            pass
        if f.find("cy=") >= 0:
            cy = re.findall('[0-9.]+', f)
            ret.cy = (float(cy[0]) - (viewBoxHeight / 2)) / 100
            pass
        if f.find("r=") >= 0:
            r = re.findall('[0-9.]+', f)
            ret.r = round(float(r[0]) * 0.3527777778 * 0.039408866995, 2)
            pass
        if f.find("class=") >= 0:
            sty = re.findall('st[0-9]*', f)
            for c in classes:
                if c.name == "." + sty[0]:
                    ret.style = c
            pass
    return ret

def parsePolygon(poly):
    ret = illustratorPolygon()
    ret.vbWidth = float(viewBoxWidth)
    ret.vbHeight = float(viewBoxHeight)
    fields = re.findall('[a-zA-Z]*[0-9]*=\"[a-zA-Z0-9., ]*\"', poly)
    for f in fields:
        if f.find("class=") >= 0:
            pass
        if f.find("points=") >= 0:
            pairs = re.findall("[0-9.?]+,[0-9.?]+", f)
            ret.startingPoint = pairs[0]
            ret.points = pairs
    return ret

# TODO: Fix parsing to not use x1[1] index. Specifically construct RegEx to get 1 match
# TODO: Stress test this
def parseLine(li):
    ret = illustratorLine()
    fields = re.findall('[a-zA-Z]*[0-9]*=\"[a-zA-Z0-9.]*\"', li)
    for f in fields:
        if f.find("x1=") >= 0:
            x1 = re.findall('[0-9.]+', f)
            ret.x1 = float(x1[1]) * 0.3527777778 * 0.039408866995 - (viewBoxWidth / 2) * 0.3527777778 * 0.039408866995
            pass
        if f.find("x2=") >= 0:
            x2 = re.findall('[0-9.]+', f)
            ret.x2 = float(x2[1]) * 0.3527777778 * 0.039408866995 - (viewBoxWidth / 2) * 0.3527777778 * 0.039408866995
            pass
        if f.find("y1=") >= 0:
            y1 = re.findall('[0-9.]+', f)
            ret.y1 = float(y1[1]) * 0.3527777778 * 0.039408866995 - (viewBoxHeight / 2) * 0.3527777778 * 0.039408866995
            pass
        if f.find("y2=") >= 0:
            y2 = re.findall('[0-9.]+', f)
            ret.y2 = float(y2[1]) * 0.3527777778 * 0.039408866995 - (viewBoxHeight / 2) * 0.3527777778 * 0.039408866995
            pass
        if f.find("class=") >= 0:
            sty = re.findall('st[0-9]*', f)
            for c in classes:
                if c.name == "." + sty[0]:
                    ret.style = c
            pass
    return ret

def parseHeader(line):
    global viewBoxWidth
    global viewBoxHeight
    fields = re.findall('[a-zA-Z:]+=\"[a-zA-Z0-9/:._ -;]+\"', line)
    for f in fields:
        if f.find("viewBox=") >= 0:
            vb = re.findall('[0-9.]+', f)
            viewBoxWidth = math.ceil(float(vb[2]))
            viewBoxHeight = math.ceil(float(vb[3]))
    pass

# TODO: Identify which data in <svg... string is constant across files
# TODO: Identify what non-constant data corresponds to
#           viewBox is defined by the shapes in the image
#                i.e. it is a 'bounding box' around all of the items
def writeNewFile(fp):
    global classes
    global items
    with open(fp, 'w') as fil:
        fil.write(XML_VERSION)
        fil.write(STYLE_SHEET)
        fil.write("<svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.2\" baseProfile=\"tiny\" "
                            "xml:space=\"preserve\" style=\"shape-rendering:geometricPrecision; fill-rule:evenodd;\" "
                            "width=\"3.33mm\" height=\"2.78mm\" viewBox=\"-0.5 -0.5 3.33 2.78\">\n")
        fil.write(buildTitle(title))
        fil.write(buildDescription(description))
        fil.write(METADATA)
        fil.write(PIVOT_POINT)
        for it in items:
            fil.write(it.__str__())
            fil.write("\n")
        fil.write("</svg>")


if __name__ == '__main__':
    # make the UI window
    master = tk.Tk()  # tkinter.Tk() is the base class for the window
    master.geometry("800x300")  # window dimensions
    master.title("CCOM_AI_Image_Translator")  # changes the title of the window

    # declare UI elements
    # source folder
    lblSourceFolder = tkinter.Label(master, text="Source Folder")
    lblSourceFolder.place(x=0, y=0)
    txtSourceFolder = tkinter.Text(master, height=1, width=75)  # text box for the folder
    txtSourceFolder.config(state='disabled')  # makes the text box read-only
    txtSourceFolder.place(x=125, y=0)

    # source file
    lblSourceFile = tkinter.Label(master, text="Source File")
    lblSourceFile.place(x=0, y=30)
    txtSourceFile = tkinter.Text(master, height=1, width=75)  # text box for the file
    txtSourceFile.config(state='disabled')  # makes the text box read-only
    txtSourceFile.place(x=125, y=30)

    #destination folder
    lblDestinationFolder = tkinter.Label(master, text="Destination Folder")
    lblDestinationFolder.place(x=0, y=75)
    txtDestinationFolder = tkinter.Text(master, height=1, width=75)
    txtDestinationFolder.insert("1.0", "optional (if different than source folder)")
    txtDestinationFolder.place(x=125, y=75)

    # destination file
    lblDestinationFile = tkinter.Label(master, text="Destination File Name")
    lblDestinationFile.place(x=0, y=105)
    txtDestinationFile = tkinter.Text(master, height=1, width=75)
    txtDestinationFile.place(x=125, y=105)

    # select file button
    btnSelectFile = ttk.Button(master, text="Select File", command=lambda: button_listener(txtSourceFolder, txtSourceFile, txtDestinationFile))  # runs button_listener on click
    btnSelectFile.place(x=0, y=200)

    # convert button
    btnConvert = ttk.Button(master, text="Convert", command=lambda: button_listener_convert(txtSourceFolder, txtSourceFile, txtDestinationFolder, txtDestinationFile))
    btnConvert.place(x=0, y=225)

    # destination folder button
    btnDestFolder = ttk.Button(master, text="Select Destination Folder", command=lambda: button_listener_destination(txtDestinationFolder))
    btnDestFolder.place(x=0, y=275)

    # quit button
    btnQuit = ttk.Button(master, text="Quit", command=lambda: master.quit())  # quits the program on click
    btnQuit.place(x=0, y=250)

    # starts the window
    master.mainloop()

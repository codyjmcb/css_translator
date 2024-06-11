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
"""
from datetime import datetime

XML_VERSION = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
STYLE_SHEET = "<?xml-stylesheet href=\"SVGStyle.css\" type=\"text/css\"?>\n"
DEFAULT_TITLE = "This is the default title"
DEFAULT_DESCRIPTION = "This is the default description"

# TODO: Identify if it is ALWAYS this text block
now = datetime.now()
METADATA = f"\t<metadata>\n" \
           f"\t\t<iho:S100SVG xmlns:iho=\"http://www.iho.int/SVGMetadata\">\n" \
           f"\t\t\t<iho:Description publisher=\"IHO\" creationDate=\"{now.month}/{now.day}/{now.year}\" source=\"S52Preslib4.0\" format=\"S100SVG\" version=\"0.1\" />\n" \
           f"\t\t</iho:S100SVG>\n" \
           f"\t</metadata>\n"
def buildTitle(title):
    return f"\t<title>{title}</title>\n"
def buildDescription(desc):
    return f"\t<desc>{desc}</desc>\n"

# This is the default pivot point generated from S100 tool kit
PIVOT_POINT = "<circle class=\"pivotPoint layout\" fill=\"none\" cx=\"0.00\" cy=\"0.00\" r=\"0.4\" />\n"
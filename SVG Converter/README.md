# CCOM_File_Converter


# Adobe Illustrator Image Creator Notes:
#   TODO: Obsolete this comment, illustrator saves images in points regardless of chosen units
#       Points * 0.3527777778 == MM
#   For an accurate image translations, the units used for Illustrator should be millimeters
#   From Illustrator:
#       Edit->Preferences->Units    (change _General_, _Stroke_, _Type_ to be in millimeters)
#   Conversion of color from Adobe Illustrator so S100 is non-trivial
#        Instead of a massive look-up table, color information is inserted into the converted file as the hex color code
#           These will need to be manually replaced with the appropriate S100 color code

# General Notes:
#   When saving an Illustrator drawing as a .SVG, the viewbox (size of drawing space) is defined in pixels.
#       I don't know that this is 'fixable', but for this converter, that information is only used for relative positioning
#       That is, that drawn images will be placed in the same relative position in the S100 compliant file 

# Developer Notes:
#   Add in notes for explaining what each Regular Expression is parsing
# TODO: Circles are different from ellipses in illustrator
# Make new function/class for parsing circles

# CSS Translator

## Requirements
[Python 3.9 or higher](https://www.python.org/downloads/)

## About
This tool is used to convert SVG 1.1 compliant styling to SVG tiny compliant styling.

[TinySVG 1.2 Specification](https://www.w3.org/TR/SVGTiny12/index.html)
 
## Example of compliant/non-compliant style attributes
SVG 1.1 supports the style attribute. An example of SVG 1.1 compliant styling includes:
* <.... style="stroke-width: 0.32;" ..../>

The above example is not Tiny SVG compliant. Rather, the equivalent Tiny SVG compliant styling would be:
* <.... stroke-width="0.32" ..../>
	
## Running the program
* From the executable
  * Download "CSS Translator.exe"
  * Double click to run
* From the command line
  * Download main.py
  * In a terminal, navigate to the directory the file was downloaded into
  * Run the command python main.py
"""
File: main.py
Name: Cody J. McBride
Contact: cody.j.mcbride@gmail.com
Description: Translates 'style' attribute from SVG 1.1 compliant to SVG tiny compliant (see notes)
Version: 0.1
Date: 01/05/2024
Notes:
    Requires Python 3 (I used Python 3.9)
    Invoking the python script (command line)
        Navigate to the directory of this file
        Enter the command: python main.py
    SVG 1.1 supports the style attribute. An example of SVG 1.1 compliant styling includes:
        <.... style="stroke-width: 0.32;" ..../>
    This example is not Tiny SVG compliant. Rather, the equivalent Tiny SVG compliant styling would be:
        <.... stroke-width="0.32" ..../>
    This tool is used to convert SVG 1.1 compliant styling to SVG tiny compliant styling
"""

# import system libraries
import os  # used to handle file I/O
import re  # regular expressions
import time  # datetime
import signal

# import UI libraries
import tkinter
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from datetime import datetime

# list of modified files for history
files_modified = []

# function to be called on button click
def button_listener(source_folder, current_file):
    # request directory from user
    directory = filedialog.askdirectory()

    # update textbox to reflect directory name
    source_folder.config(state='normal')
    source_folder.delete(1.0, 'end')
    source_folder.insert(1.0, directory)
    source_folder.config(state='disabled')

    # iterate over the files in the directory
    for filename in os.listdir(directory):
        # prepend the converted file with css_removed_
        modified_file_name = "css_removed_" + filename
        modified_file_path = os.path.join(directory, modified_file_name)

        # don't modify the history file
        if "list_of_modified_files" not in filename:
            # don't try to modify a file that's already been modified
            if not os.path.exists(modified_file_path):
                # don't try to modify a 'modified' file
                if "css_removed" not in filename:
                    if ".svg" in filename:
                        # update the text box to show the current file
                        current_file.config(state='normal')
                        current_file.delete(1.0, 'end')
                        current_file.insert(1.0, filename)
                        current_file.config(state='disabled')
                        current_file.master.update()
                        check_for_style(filename, directory)
                        time.sleep(2)

    nam = write_history_file(directory)
    tkinter.messagebox.showinfo("Success!",
                                f"Number of files modified: {len(files_modified)}, list of files modified in the file: {nam}")
    reset_app(source_folder, current_file)
    pass


# function to check if the file has style information that needs to be replaced
def check_for_style(filename, filepath):
    global files_modified
    whole_path = os.path.join(filepath, filename)

    # pointer to the current file
    filePointer = open(whole_path, "r")

    # contiguous string of all the file contents
    fileContents = filePointer.read()

    # collection of individual lines in the file as defined by brackets <>
    # TODO: Explain this Regular Expression
    lines = re.findall("<text[a-zA-Z0-9 \"=:)(><\/.]+|<[^>]*>|..*|[a-z]+}", fileContents)

    # check all the lines for 'style'
    for line in lines:
        if line.find("style") >= 0:

            # ignore style in the header ??
            if line.find("xml") >= 0:
                pass

            # this file needs style information replaced
            else:
                lines = replace_style_information(lines)
                if not os.path.exists(filepath + "/css_removed/"):
                    os.makedirs(filepath + "/css_removed/")
                new_file = os.path.join(filepath + "/css_removed/", filename)
                write_new_file(lines, new_file)
                if filename not in files_modified:
                    files_modified.append(filename)

    pass


# function for replacing all the style information
# Argument: lines
# all lines in the file
def replace_style_information(lines):
    new_lines = []
    for line in lines:
        if "style" in line and "xml" not in line:
            new_lines.append(re.sub("style=\"[a-zA-Z0-9- :.;]*\"", parse_style(line), line))
        else:
            new_lines.append(line)
    return new_lines


# replace all style information with new format
# Argument: line
# the current line in the file. Ex. <path d=" M 0,-1.5 L 0,1.5" class="sl f0 sCHBLK" style="stroke-width: 0.64;"/>
def parse_style(line):
    # This Regular Expression only handles style components with numeric values
    # TODO: Update this to support 'any' value for a style component
    style_lines = re.findall("[a-zA-Z-]+:\s*[0-9.]+;*", line)

    # TODO: using style_lines[0] is an error. Any style component with more than 1 style attribute will be mis-translated
    # TODO: This should be 2 empty collections, then append to the collections in a for loop
    style_type_collection = re.findall("[a-zA-Z-]+:\s*", style_lines[0])
    value_collection = re.findall("[0-9.]+", style_lines[0])

    string_return = ""

    # iterate over the style components and their values
    for style, value in zip(style_type_collection, value_collection):
        style = style.replace(":", "=\"")
        style = style.replace(" ", "")
        string_return = string_return + style + value + "\""

    return string_return


def write_new_file(lines, filepath):
    file_writer = open(filepath, "w")
    for line in lines:
        file_writer.write(line)
        file_writer.write("\n")
    pass


def write_history_file(directory):
    history = "list_of_modified_files.txt"
    mod_file = os.path.join(directory, history)

    # append to the history
    file_writer = open(mod_file, 'a')

    # Get the current date and time
    current_datetime = datetime.now()

    # Format the datetime
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    # Write the history to the file
    file_writer.write(formatted_datetime)
    file_writer.write("\n")
    for file in files_modified:
        file_writer.write("\t" + file)
        file_writer.write("\n")
    file_writer.write("\n")
    file_writer.close()

    return history


# clears the text boxes
# resets the modified files collection to an empty collection
def reset_app(source_folder, current_file):
    source_folder.config(state='normal')
    source_folder.delete(1.0, 'end')
    source_folder.config(state='disabled')

    current_file.config(state='normal')
    current_file.delete(1.0, 'end')
    current_file.config(state='disabled')

    current_file.master.update()

    global files_modified
    files_modified = []

    pass


# main program entry point
if __name__ == '__main__':
    # make the UI window
    master = tk.Tk()  # tkinter.Tk() is the base class for the window
    master.geometry("800x300")  # window dimensions
    master.title("CCOM_CSS_Style_Translator")  # changes the title of the window

    # source folder
    lblsource_folder = tkinter.Label(master, text="Source Folder")
    lblsource_folder.place(x=0, y=0)
    txtsource_folder = tkinter.Text(master, height=1, width=75)  # text box for the folder
    txtsource_folder.config(state='disabled')  # makes the text box read-only
    txtsource_folder.place(x=125, y=0)

    # source file
    lblcurrent_file = tkinter.Label(master, text="Source File")
    lblcurrent_file.place(x=0, y=30)
    txtcurrent_file = tkinter.Text(master, height=1, width=75)  # text box for the file
    txtcurrent_file.config(state='disabled')  # makes the text box read-only
    txtcurrent_file.place(x=125, y=30)

    # select file button
    btnSelectFile = ttk.Button(master, text="SelectDirectory",
                               command=lambda: button_listener(txtsource_folder, txtcurrent_file))
    btnSelectFile.place(x=0, y=200)

    # quit button
    btnQuit = ttk.Button(master, text="Quit", command=lambda: master.quit())  # quits the program on click
    btnQuit.place(x=0, y=250)

    # exit normally when clicking the X
    master.protocol("WM_DELETE_WINDOWS", master.quit())

    master.mainloop()
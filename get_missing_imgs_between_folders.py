"""
####################################################################################################
# ________  ___  ___  ________  _________        ________  ________  _________       ___   ___     #
#|\   ____\|\  \|\  \|\   __  \|\___   ___\     |\   ____\|\   __  \|\___   ___\    |\  \ |\  \    #
#\ \  \___|\ \  \\\  \ \  \|\  \|___ \  \_|     \ \  \___|\ \  \|\  \|___ \  \_|    \ \  \\_\  \   #
# \ \  \    \ \   __  \ \   __  \   \ \  \       \ \  \  __\ \   ____\   \ \  \      \ \______  \  #
#  \ \  \____\ \  \ \  \ \  \ \  \   \ \  \       \ \  \|\  \ \  \___|    \ \  \      \|_____|\  \ #
#   \ \_______\ \__\ \__\ \__\ \__\   \ \__\       \ \_______\ \__\        \ \__\            \ \__\#
#    \|_______|\|__|\|__|\|__|\|__|    \|__|        \|_______|\|__|         \|__|             \|__|#
#                                                                                                  #
####################################################################################################
#                                                                                                  #
#  Program:         Copy Missing Images Between Two Folders                                        #
#  Author:          Corey Nguyen                                                                   #
#  Build Date:      April 7, 2024                                                                  #
#  Version:         1.0                                                                            #
#  Compatibility:   Python > 3.10                                                                  #
#                                                                                                  #
#  Dependencies:    Pillow (PIL Fork)                                                              #
#                                                                                                  #
#  To install dependencies, run:                                                                   #
#                   pip install Pillow, Tkinter                                                    #
#                                                                                                  #
#  The program allows the user to specify source, upscaled, and missing directories.               #
#  It provides an option to enable corner color check and choose the target color.                 #
#  When executed, it finds and copies missing images to the specified directory.                   #
#                                                                                                  #
#  Note: This code was AI-assisted by ChatGPT, model GPT-4.                                        #
#                                                                                                  #
####################################################################################################
"""

import os
import shutil
from tkinter import Tk, Label, Button, Entry, Checkbutton, IntVar, messagebox, colorchooser
from tkinter.filedialog import askdirectory
from PIL import Image

def list_files(directory):
    """List files in a directory."""
    return os.listdir(directory)

def is_corner_color(pixel, target_color=(0, 0, 0), threshold=10):
    """Check if a corner pixel is close to the target color based on a threshold."""
    return all(abs(pixel[i] - target_color[i]) <= threshold for i in range(3))

def check_corners_color(image_path, target_color, threshold=10):
    """Check if all four corners of the image are close to the target color."""
    try:
        with Image.open(image_path) as img:
            pixels = img.load()
            width, height = img.size
            corners = [pixels[0, 0], pixels[0, height - 1], pixels[width - 1, 0], pixels[width - 1, height - 1]]
            return all(is_corner_color(corner, target_color, threshold) for corner in corners)
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return False

def find_and_copy_missing_images():
    source_dir = source_dir_entry.get()
    upscaled_dir = upscaled_dir_entry.get()
    missing_dir = missing_dir_entry.get()

    # Validate directories
    if not os.path.isdir(source_dir) or not os.path.isdir(upscaled_dir):
        messagebox.showerror("Error", "Source or upscaled directory is invalid.")
        return

    # Ensure the missing directory exists
    if not os.path.exists(missing_dir):
        os.makedirs(missing_dir, exist_ok=True)

    # Configuration for corner color checking
    check_black_corners = check_var.get()
    target_color = color_entry.get()
    target_color_rgb = tuple(int(target_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

    # Collect base names of files in the upscaled directory
    upscaled_files_base_names = set(os.path.splitext(f)[0].lower() for f in os.listdir(upscaled_dir))

    copied_files_count = 0

    # Iterate through source files and check against upscaled files
    for filename in os.listdir(source_dir):
        base_name, extension = os.path.splitext(filename)
        base_name_lower = base_name.lower()

        # Skip file if a base-named equivalent exists in the upscaled directory
        if base_name_lower in upscaled_files_base_names:
            continue

        # Perform corner color check if required
        source_path = os.path.join(source_dir, filename)
        if check_black_corners:
            # Skip copying if the image doesn't pass the corner color check
            if not check_corners_color(source_path, target_color_rgb):
                continue

        # Copy the file to the missing directory with its original name
        missing_path = os.path.join(missing_dir, filename)
        shutil.copy(source_path, missing_path)
        copied_files_count += 1

    # Provide feedback to the user
    if copied_files_count == 0:
        messagebox.showinfo("Info", "No files were flagged as missing.")
    else:
        messagebox.showinfo("Info", f"Flagged {copied_files_count} files as missing and copied to the missing directory.")

def select_directory(entry):
    """Open a dialog to select a directory, updating the entry with the chosen path."""
    directory = askdirectory()
    if directory:
        entry.delete(0, "end")
        entry.insert(0, directory)

def choose_color():
    """Open a color chooser dialog and update the Entry widget with the chosen color."""
    color_code = colorchooser.askcolor(title="Choose a color")[1]
    if color_code:
        color_entry.delete(0, "end")
        color_entry.insert(0, color_code)

def on_escape(event=None):
    """Close the application when the Escape key is pressed."""
    root.destroy()

# Set up the UI
root = Tk()
root.title("Image Processing Tool")

# Bind the Escape key to the on_escape function
root.bind('<Escape>', on_escape)

# Source directory
Label(root, text="Source Directory:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
source_dir_entry = Entry(root, width=50)
source_dir_entry.grid(row=0, column=1, padx=5, pady=5)
Button(root, text="...", command=lambda: select_directory(source_dir_entry)).grid(row=0, column=2, padx=5, pady=5)

# Upscaled directory
Label(root, text="Upscaled Directory:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
upscaled_dir_entry = Entry(root, width=50)
upscaled_dir_entry.grid(row=1, column=1, padx=5, pady=5)
Button(root, text="...", command=lambda: select_directory(upscaled_dir_entry)).grid(row=1, column=2, padx=5, pady=5)

# Missing directory
Label(root, text="Missing Directory:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
missing_dir_entry = Entry(root, width=50)
missing_dir_entry.grid(row=2, column=1, padx=5, pady=5)
Button(root, text="...", command=lambda: select_directory(missing_dir_entry)).grid(row=2, column=2, padx=5, pady=5)

# Checkbox for corner color check
check_var = IntVar()
Checkbutton(root, text="Enable corner color check", variable=check_var).grid(row=3, column=0, columnspan=2, sticky='w', padx=5, pady=5)

# Color picker for corner color
color_entry = Entry(root, width=10)
color_entry.grid(row=3, column=1, padx=5, pady=5)
color_entry.insert(0, '#000000')  # Default color black
Button(root, text="Choose Corner Color", command=choose_color).grid(row=3, column=2, padx=5, pady=5)

# Button to start the process
Button(root, text="Find and Copy Missing Images", command=find_and_copy_missing_images).grid(row=4, column=0, columnspan=3, padx=5, pady=5)

root.mainloop()

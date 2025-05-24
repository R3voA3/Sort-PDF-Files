"""
Sorts pdf files in given folder by their sheet size.
Pdf files can also be sorted in custom folder if their name matches a pattern.
See config.toml for settings and to add custom sizes.
"""

import tkinter
import shutil
import tomllib
import logging
import re
import sys
import os

from pathlib import Path
from tkinter import filedialog
from tkinter import messagebox
from pypdf import PdfReader

def module_path():
    """ This will get us the program's directory,
    even if we are frozen using py2exe"""

    if hasattr(sys, "frozen"):
        return os.path.dirname(sys.executable)

    return os.path.dirname(__file__)

def move_or_copy_file(source_file, move_file, target_folder_name, root_folder):
    """Moves or copies given file"""
    target_folder = Path(root_folder).joinpath(target_folder_name)
    Path(target_folder).mkdir(exist_ok = True)

    if move_file:
        target_file = Path(target_folder).joinpath(Path(source_file).name)
        target_file_exists = target_file.exists()

        if target_file_exists:
            oLog.warning('%s already exists! File was not moved', target_file)
        else:
            shutil.move(source_file, target_folder)
            oLog.info('%s was moved to %s', source_file, target_folder)
    else:
        shutil.copy2(source_file, target_folder)
        oLog.info('%s was moved to %s', source_file, target_folder)

def pick_folder():
    """Function printing python version."""
    # we don't want a full GUI, so keep the root window from appearing
    tkinter.Tk().withdraw()

    # show an 'Open' dialog box and return the path to the selected file
    return filedialog.askdirectory()

def are_lists_equal_with_tolerance(list_a, list_b, tolerance):
    """Checks if integers of two lists are identical including a tolerance."""
    for i1, i2 in zip(list_a, list_b):
        if abs(i1-i2) > tolerance:
            return False
    return True

def iterate_files(root_folder):
    """Loops over all pdf files in given folder and moves them if appropriate"""
    for file in list(Path(root_folder).glob('*.pdf')):
        file_name = file.name

        try:
            # Handle special files
            if not dict_special_files is None:
                for key in dict_special_files.keys():

                    value = dict_special_files.get(key)
                    pattern = value[0]
                    folder_name = value[1]

                    if (pattern == '' or folder_name == ''):
                        continue

                    if re.search(pattern, file_name):
                        move_or_copy_file(file, move_files, folder_name, root_folder)
                        break

            arr_size = [-1, -1]
            different_sizes = False

            for page in PdfReader(file).pages:
                bounding_box = page.trimbox
                width = round(bounding_box.width)
                height = round(bounding_box.height)

                # Set arr_size initially
                if arr_size[0] == -1 or arr_size[1] == -1:
                    arr_size[0] = width
                    arr_size[1] = height
                else:
                    # If new width and height are different
                    # from previous width and height
                    # then pages don't have the same arr_size
                    if arr_size[0] != width or arr_size[1] != height:
                        different_sizes = True
                        continue

            file_handled = False

            # Move files to folder_name_unknown folder if
            # page sizes are different
            if not different_sizes:
                for arr_size_preset in dict_sizes.values():
                    if are_lists_equal_with_tolerance \
                    (arr_size, [arr_size_preset[0], arr_size_preset[1]], size_tolerance):
                        move_or_copy_file(file, move_files, arr_size_preset[2], root_folder)
                        file_handled = True
                        break

            if (different_sizes or not file_handled):
                move_or_copy_file(file, move_files, folder_name_unknown, root_folder)
                file_handled = True
                continue
        except Exception:
            oLog.error('%s could not be opened', file_name),

if __name__ == '__main__':
    module_location = module_path()

    oLog = logging.getLogger(__name__)
    logging.basicConfig(filename=Path(str(module_location)).joinpath('logfile.log'),
                        level=logging.INFO, encoding='UTF-8')

    path_to_config = Path(str(module_location)).joinpath('config.toml')

    # Check if config.toml exists
    if not Path(path_to_config).exists():
        messagebox.showerror('config.toml not found',
                             'The configuration file config.toml is missing! Program aborted!')
        oLog.error('The configuration file config.toml is missing! Program aborted')
        sys.exit()

    # Load config.toml
    with open(path_to_config, 'rb') as f:
        data = tomllib.load(f)

    # Check for valid config.toml
    if data.get('SIZES') is None:
        messagebox.showerror('SIZES not found',
                        'config.toml does not contain sizes. Program aborted!')
        oLog.error('config.toml does not contain sizes. Program aborted')
        sys.exit()

    if data.get('OPTIONS') is None:
        messagebox.showerror('OPTIONS not found',
                        'config.toml does not contain options. Program aborted!')
        oLog.error('config.toml does not contain options. Program aborted')
        sys.exit()

    dict_special_files = data.get('SPECIAL_FILES')
    dict_sizes = data.get('SIZES')
    dictOptions = data.get('OPTIONS')

    # Use default values if not defined in config.toml
    move_files = dictOptions.get('moveFiles', False)
    size_tolerance = dictOptions.get('sizeTolerance', 10)
    folder_name_unknown = dictOptions.get('unknownSize', '@manuelSortingRequired')

    root = pick_folder()

    if root != '':
        RESULT = messagebox.askquestion('Check Path',
                                        f'Are you sure you want to use this path? {root}')

        if RESULT == 'yes':
            iterate_files(root)
        else:
            oLog.info('Copy operation aborted by the user')
    else:
        oLog.info('Copy operation canceled. Not valid folder was selected')

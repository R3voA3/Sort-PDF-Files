from pathlib import Path
from pypdf import PdfReader
from tkinter import Tk
from tkinter import filedialog
from tkinter import messagebox

import shutil

SIZE_A0 = [3370, 2384]
SIZE_A1 = [2384, 1684]
SIZE_A2 = [1684, 1191]
SIZE_A3 = [1191, 842]
SIZE_A4 = [595, 842]

def pickFolder():
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    return filedialog.askdirectory() # show an 'Open' dialog box and return the path to the selected file

def createExportFolders(path):
    for folderName in ['A0', 'A1', 'A2', 'A3', 'A4', 'BOMs', 'unknown_size']:
        Path(sourceFolderPathObject.joinpath(folderName)).mkdir(exist_ok = True)

def copyFiles(sourceFolderPathObject):
    for file in list(sourceFolderPathObject.glob('*.pdf')):
        reader = PdfReader(file)
        fileName = file.name

        if ('.bom.' in fileName or '.bomall.' in fileName):
            dest = sourceFolderPathObject.joinpath('BOMs')
            if (not Path(dest).is_file()):
                shutil.copy2(file, dest)
                print(f'{fileName} was moved to {dest}.')
            continue

        size = [-1, -1]
        differentSizes = False

        for page in reader.pages:
            boundingBox = page.trimbox
            width = round(boundingBox.width)
            height = round(boundingBox.height)

            # Set size initially
            if (size[0] == -1 or size[1] == -1):
                size[0] = width
                size[1] = height
            else:
                # If new width and height are different
                # from previous width and height
                # then pages don't have the same size
                if (size[0] != width or size[1] != height):
                    differentSizes = True
                    continue

        moved = False

        # Move files to 'unknown_size' folder if
        # page sizes are different
        if (differentSizes):
            dest = sourceFolderPathObject.joinpath('unknown_size')
            shutil.copy2(file, dest)
            print(f'{fileName} was moved to {dest}.')
            continue

        if (size == SIZE_A0):
            dest = sourceFolderPathObject.joinpath('A0')
            shutil.copy2(file, dest)
            print(f'{fileName} was moved to {dest}.')
            continue

        if (size == SIZE_A1):
            dest = sourceFolderPathObject.joinpath('A1')
            shutil.copy2(file, dest)
            print(f'{fileName} was moved to {dest}.')
            continue

        if (size == SIZE_A2):
            dest = sourceFolderPathObject.joinpath('A2')
            shutil.copy2(file, dest)
            print(f'{fileName} was moved to {dest}.')
            continue

        if (size == SIZE_A3):
            dest = sourceFolderPathObject.joinpath('A3')
            shutil.copy2(file, dest)
            print(f'{fileName} was moved to {dest}.')
            continue

        if (size == SIZE_A4):
            dest = sourceFolderPathObject.joinpath('A4')
            shutil.copy2(file, dest)
            print(f'{fileName} was moved to {dest}.')
            continue

        print(f'{fileName} could not be copied!')

def raw_input():
    test = True

if (__name__ == '__main__'):
    sourceFolderPath = pickFolder()

    if (sourceFolderPath != ''):

        result = messagebox.askquestion('Check path', f'Are you sure you want to use this path? <{sourceFolderPath}>')

        if (result ==  'yes'):
            sourceFolderPathObject = Path(sourceFolderPath)
            try:
                createExportFolders(sourceFolderPathObject)
                copyFiles(sourceFolderPathObject)
            except SystemExit as e:
                print('Error!', e)
                print('Press enter to exit (and fix the problem)')
                raw_input()
        else:
            print('Copy operation aborted!')
    else:
        print('Copy operation canceled. Not valid folder was selected!')

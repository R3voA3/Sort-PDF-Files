from pathlib import Path
from pypdf import PdfReader
from tkinter import Tk
from tkinter import filedialog
from tkinter import messagebox

import shutil
import tomllib

def getSizes():
    with open("config.toml", "rb") as f:
        data = tomllib.load(f)

    dictSizes = dict()

    for size in data.get('SIZES'):
        dictSizes[size] = data['SIZES'][size]

    return dictSizes

def pickFolder():
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    return filedialog.askdirectory() # show an 'Open' dialog box and return the path to the selected file

def areListsEqualWithError(list1, list2, tolerance):
    for i1, i2 in zip(list1, list2):
        if (abs(i1-i2) > tolerance): return False
    return True

def copyFiles(sourceFolderPathObject):
    for file in list(sourceFolderPathObject.glob('*.pdf')):
        fileName = file.name

        try:
            reader = PdfReader(file)

            if (handleBOMs):
                if ('.bom.' in fileName or '.bomall.' in fileName or '.bomstrc.' in fileName):
                    dest = sourceFolderPathObject.joinpath(folderNameBOM)
                    Path(dest).mkdir(exist_ok = True)
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

            # Move files to folderNameUnknown folder if
            # page sizes are different
            if (not differentSizes):
                for sizePreset in dictSizes.values():
                    if (areListsEqualWithError(size, [sizePreset[0], sizePreset[1]], sizeTolerance)):
                        dest = sourceFolderPathObject.joinpath(sizePreset[2])
                        Path(dest).mkdir(exist_ok = True)
                        shutil.copy2(file, dest)
                        print(f'{fileName} was moved to {dest}.')
                        moved = True
                        break

            if (differentSizes or not moved):
                dest = sourceFolderPathObject.joinpath(folderNameUnknown)
                Path(dest).mkdir(exist_ok = True)
                shutil.copy2(file, dest)
                print(f'{fileName} was moved to {dest}.')
                moved = True
                continue
        except:
            print(f'{fileName} could not be opened!')

if (__name__ == '__main__'):
    sourceFolderPath = pickFolder()

    if (sourceFolderPath != ''):
        result = messagebox.askquestion('Check path', f'Are you sure you want to use this path? <{sourceFolderPath}>')

        if (result ==  'yes'):
            # Store settings globally
            with open("config.toml", "rb") as f:
                data = tomllib.load(f)

            dictSizes = dict()

            for size in data.get('SIZES'):
                dictSizes[size] = data['SIZES'][size]

            folderNameUnknown = data['FOLDER_NAMES']['unknownSize']
            folderNameBOM = data['FOLDER_NAMES']['bom']
            handleBOMs = data['OPTIONS']['handleBomFiles']
            sizeTolerance = data['OPTIONS']['sizeTolerance']

            sourceFolderPathObject = Path(sourceFolderPath)
            copyFiles(sourceFolderPathObject)
        else:
            print('Copy operation aborted!')
    else:
        print('Copy operation canceled. Not valid folder was selected!')

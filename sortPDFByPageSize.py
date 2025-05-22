
from pathlib import Path
from pypdf import PdfReader
from tkinter import filedialog
from tkinter import messagebox

import tkinter
import shutil
import tomllib
import logging

def moveOrCopyFile(strSourceFile, bMoveFile, strTargetFolderName, strRoot):
    strTargetFolder = Path(strRoot).joinpath(strTargetFolderName)
    Path(strTargetFolder).mkdir(exist_ok = True)

    if (bMoveFile):
        targetFile = Path(strTargetFolder).joinpath(Path(strSourceFile).name)
        targetFileExists = targetFile.exists()

        if (targetFileExists):
            oLog.warning(f'{targetFile} already exists! File was not moved!')
        else:
            shutil.move(strSourceFile, strTargetFolder)
            oLog.info(f'{strSourceFile} was moved to {strTargetFolder}!')
    else:
        shutil.copy2(strSourceFile, strTargetFolder)
        oLog.info(f'{strSourceFile} was moved to {strTargetFolder}!')

def getSizes():
    with open("config.toml", "rb") as f:
        data = tomllib.load(f)

    dictSizes = dict()

    for aSize in data.get('SIZES'):
        dictSizes[aSize] = data['SIZES'][aSize]

    return dictSizes

def pickFolder():
    tkinter.Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    return filedialog.askdirectory() # show an 'Open' dialog box and return the path to the selected oFile

def areListsEqualWithError(lList1, lList2, iTolerance):
    for i1, i2 in zip(lList1, lList2):
        if (abs(i1-i2) > iTolerance): return False
    return True

def iterateFiles(strRoot):
    for oFile in list(Path(strRoot).glob('*.pdf')):
        strFileName = oFile.name

    # try:
        if (bHandleBOMs):
            if ('.bom.' in strFileName or '.bomall.' in strFileName or '.bomstrc.' in strFileName):
                moveOrCopyFile(oFile.__str__(), bMoveFiles, strFolderNameBOM, strRoot)
                continue

        aSize = [-1, -1]
        bDifferentSizes = False

        for page in PdfReader(oFile).pages:
            boundingBox = page.trimbox
            iWidth = round(boundingBox.width)
            iHeight = round(boundingBox.height)

            # Set aSize initially
            if (aSize[0] == -1 or aSize[1] == -1):
                aSize[0] = iWidth
                aSize[1] = iHeight
            else:
                # If new iWidth and iHeight are different
                # from previous iWidth and iHeight
                # then pages don't have the same aSize
                if (aSize[0] != iWidth or aSize[1] != iHeight):
                    bDifferentSizes = True
                    continue

        bFileHandled = False

        # Move files to strFolderNameUnknown folder if
        # page sizes are different
        if (not bDifferentSizes):
            for aSizePreset in dictSizes.values():
                if (areListsEqualWithError(aSize, [aSizePreset[0], aSizePreset[1]], iSizeTolerance)):
                    moveOrCopyFile(oFile.__str__(), bMoveFiles, aSizePreset[2], strRoot)
                    bFileHandled = True
                    break

        if (bDifferentSizes or not bFileHandled):
            moveOrCopyFile(oFile.__str__(), bMoveFiles, strFolderNameUnknown, strRoot)
            bFileHandled = True
            continue
    # except:
        oLog.error(f'{strFileName} could not be opened!'),

if (__name__ == '__main__'):

    oLog = logging.getLogger(__name__)
    logging.basicConfig(filename='logfile.log', level=logging.INFO)

    if (not Path('config.toml').exists()):
        messagebox.showerror('config.toml not found',
                             'The configuration oFile config.toml is missing! Program aborted!')
        oLog.error('The configuration oFile config.toml is missing! Program aborted!')
        exit()

    strRoot = pickFolder()

    if (strRoot != ''):
        strResult = messagebox.askquestion('Check path',
                                        f'Are you sure you want to use this path? {strRoot}')

        if (strResult == 'yes'):
            # Store settings globally
            with open("config.toml", "rb") as f:
                data = tomllib.load(f)

            dictSizes = dict()

            for aSize in data.get('SIZES'):
                dictSizes[aSize] = data['SIZES'][aSize]

            strFolderNameUnknown = data['OPTIONS']['unknownSize']
            strFolderNameBOM = data['OPTIONS']['bom']
            bHandleBOMs = data['OPTIONS']['handleBomFiles']
            iSizeTolerance = data['OPTIONS']['sizeTolerance']
            bMoveFiles = data['OPTIONS']['move']

            iterateFiles(strRoot)
        else:
            oLog.info('Copy operation aborted!')
    else:
        oLog.info('Copy operation canceled. Not valid folder was selected!')
import sys, os, fnmatch, configparser, cv2
from pathlib import Path
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import QMessageBox, QApplication, QLabel
from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex, pyqtSignal, QObject
from PyQt5.QtGui import QPixmap, QPainter, QIcon

class Utils:
    ignoreList = ['metadata', 'metadata.txt', 'systeminfo', 'systeminfo.txt', 'cloud', 'cloud.conf']
    ignoredromdirs = ['model2','xbox360']
    def __init__(self):
        pass

    @staticmethod
    def getFilesInDir(directory):
        files = []
        for f in os.listdir(directory):
            fullPath = os.path.join(directory, f)
            if os.path.isfile(fullPath):
                files.append(fullPath)
        return files

    @staticmethod
    def getDirsInDir(directory):
        dirs = []
        for f in os.listdir(directory):
            fullPath = os.path.join(directory, f)
            if os.path.isdir(fullPath):
                dirs.append(fullPath)
        return dirs

    @staticmethod
    def getFilesInSubDirs(directory):
        files = []
        for dirpath, _, filenames in os.walk(directory):
            for f in filenames:
                files.append(os.path.join(dirpath, f))
        return files

    @staticmethod
    def loadMediaDic(directory):
        # returns a dictionary of {gameName, [media files]}
        mediaList = ['.png','.jpg','.mp4']
        out = {}
        files = Utils.getFilesInSubDirs(directory)
        for file in files:
            filename = Path(file).stem
            extension = Path(file).suffix

            if extension in mediaList:
                if filename not in out:
                    out[filename] = []
                out[filename].append(file)
        return out

    @staticmethod
    def getGameLists(directory, file_mask):
        result = {}
        if not file_mask:
            file_mask = 'gamelist.xml'

        # Walk through the directory
        for root, dirs, files in os.walk(directory):
            for filename in fnmatch.filter(files, file_mask):
                # Use the folder name as the key and the file path as the value
                folderName = os.path.basename(root)
                filePath = os.path.join(root, filename)
                result[folderName] = filePath  # This will overwrite if multiple files in the same folder

        return result

    @staticmethod
    def getRoms(directory):
        filePaths = []

        # Iterate over files in the specified directory
        for fileName in Utils.getFilesInSubDirs(directory):
            if Path(fileName).stem not in Utils.ignoreList:
                filePaths.append(fileName)

        return filePaths

    @staticmethod
    def loadXmlFile(filePath):
        fileContent = Path(filePath).read_text()
        splitXml = fileContent.split('<gameList>', 1)
        finalXml = '<gameList>' + splitXml[1]
        root = ET.fromstring(finalXml)
        return root

    @staticmethod
    def saveXMLToFile(filepath, xmlRoot):
        tree = ET.ElementTree(xmlRoot)
        tree.write(filepath, encoding='utf-8', xml_declaration=True)

    @staticmethod
    def getDirectorySizeAndFileCount(directoryPath):
        # Returns the total size and number of files in the specified directory.
        totalSize = 0
        fileCount = 0

        for dirpath, dirnames, filenames in os.walk(directoryPath):
            for filename in filenames:
                filePath = os.path.join(dirpath, filename)
                if Path(filePath).is_file() and filename not in Utils.ignoreList and os.path.basename(dirpath) not in Utils.ignoredromdirs:
                    try:
                        totalSize += os.path.getsize(filePath)
                        fileCount += 1
                    except:
                        pass
            return totalSize, fileCount


    def showDialog(self, parent, title, text, buttonText):
            msgBox = QMessageBox(parent)
            msgBox.setWindowTitle(title)
            msgBox.setText(text)
            msgBox.addButton(buttonText, QMessageBox.AcceptRole)
            msgBox.exec_()

    @staticmethod
    def findGameByName(root, gameFile):
        for game in root.findall('game'):
            pathElement = game.find('path')
            if pathElement is not None and gameFile in pathElement.text:
                return game
        return None

    @staticmethod
    def setClipboardText(str):
        clipboard = QApplication.clipboard()
        clipboard.setText(str)

    @staticmethod
    def get_video_thumbnail(video_path, time_in_seconds=5):
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_MSEC, time_in_seconds * 1000)  # Set the time in milliseconds
        success, image = cap.read()
        cap.release()
        if success:
            thumbnail_path = "thumbnail.jpg"
            cv2.imwrite(thumbnail_path, image)  # Save the frame as an image
            return thumbnail_path
        return None

class FileSystemModel(QAbstractItemModel):
    def __init__(self, rootPath):
        super().__init__()
        self.rootPath = rootPath

    def rowCount(self, parent=QModelIndex()):
        if not parent.isValid():
            return len(os.listdir(self.rootPath))
        return 0  # More logic needed for child counts

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return os.path.basename(os.listdir(self.rootPath)[index.row()])
        return None
    # Implement other necessary methods (index, parent, etc.)


class SettingsManager:
    def __init__(self, configPath="config.ini"):
        # Get the current script's directory (program folder)
        self.configPath = configPath
        self.config = configparser.ConfigParser()
        self.load()

    def load(self):
        """Load settings from config file or set defaults if not available."""
        if os.path.exists(self.configPath):
            self.config.read(self.configPath)
        else:
            self.config['folders'] = {
                'defaultFolder': '/home/deck',
                'gamelistsFolder': '/home/deck/ES-DE/gamelists/',
                'romsFolder': '/run/media/deck/ed4e9ecc-0701-43e2-9727-91b64daef9dc/Emulation/roms',
                'gameSystemFolder': ''
            }
            self.config['misc'] = {
                'gamelistsMask': 'gamelist.xml',
            }
            self.save()  # Create config file if it doesn't exist

    def get(self, section, option, fallback=None):
        """Retrieve a setting with a fallback value."""
        return self.config.get(section, option, fallback=fallback)

    def set(self, section, option, value):
        """Update or add a setting."""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config[section][option] = value
        self.save_settings()

    def append(self, section, option, value):
        """Append a value to a setting, add if nonexistant."""
        if not self.config.has_section(section):
            self.config.add_section(section)
        if self.config.has_option(section, option):
            self.config[section][option] = ','.join([self.config[section][option], value])
        else:
            self.config[section][option] = value
        #self.save_settings()

    def save(self):
        """Write settings back to the config file."""
        with open(self.configPath, 'w') as configfile:
            self.config.write(configfile)


class Thumbnail(QLabel):
    clicked = pyqtSignal()  # Signal to emit when the label is clicked

    def __init__(self, path='', parent=None):
        super(Thumbnail, self).__init__(parent)
        self.path = path

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:  # Check if the left mouse button was clicked
            self.clicked.emit()  # Emit the clicked signal
        super(Thumbnail, self).mousePressEvent(event)

    def __repr__(self):
        return (f"Thumbnail(path={self.path}")

class Game():
    def __init__(self, name=''):
        self.name = name
        self.romPath = None # path to the rom file
        self.system = None # game system name
        self.mediaFolder = None # downloaded_media path
        self.pictures = [] # paths to jpgs & pngs
        self.video = None # path to video file
        self.updatePath = None # path to game update file
        self.dlc = [] # paths to any DLC files
        self.gamelistEntry = None # a <game> element from xmlRoot

    def __repr__(self):
        return (f"Game(name={self.name}, romPath={self.romPath}, system={self.system}, "
            f"mediaFolder={self.mediaFolder}, pictures={self.pictures}, video={self.video}, "
            f"updatePath={self.updatePath}, dlc={self.dlc}, gamelistEntry={self.gamelistEntry})")

########################################################
#def loadAllMedia():
#    # get media
#    for game in self.games.values():
#        media = Utils.loadMediaDic(game.mediaFolder)
#        for entry in media.get(game.name):
#            folder = os.path.basename(os.path.dirname(entry))
#            if Path(entry).suffix == '.mp4':
#                game.video = entry
#            else:
#                game.pictures.append(entry)

import sys, os, fnmatch, configparser, pickle
from pathlib import Path
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import QMessageBox, QApplication, QLabel, QListWidgetItem
from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex, pyqtSignal, QObject
from PyQt5.QtGui import QPixmap, QPainter, QIcon
import traceback

class Utils:
    ignoreList = ['metadata', 'metadata.txt', 'systeminfo', 'systeminfo.txt', 'cloud', 'cloud.conf']
    ignoredromdirs = ['model2','xbox360']
    programFolder = os.path.dirname(os.path.abspath(__file__))

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
    def renameFile(oldPath, newName):
        newPath = oldPath.replace(item.getGame().name, newName)
        os.rename(oldPath, newPath)
    @staticmethod
    def getGameLists(directory, file_mask='gamelist.xml'):
        #loads all gamelist.xml files into a list
        result = []
        for root, dirs, files in os.walk(directory):
            for filename in fnmatch.filter(files, file_mask):
                filepath = os.path.join(root, filename)
                result.append(filepath)
        return result

    @staticmethod
    def getRoms(directory):
        filePaths = []

        # Iterate over files in the specified directory
        for fileName in Utils.getFilesInDir(directory):
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


    @staticmethod
    def showDialog(parent, title, text, buttonText):
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
    def serializeCollection(collection, name):
        # Serialize (Save) the collection of objects to a file
        path = os.path.join(Utils.programFolder, f'{name}.dat')
        with open(path, 'wb') as f:
            pickle.dump(collection, f)

    @staticmethod
    def deserializeCollection(name):
        # Deserialize (Load) the desired file
        out = None
        path = os.path.join(Utils.programFolder, f'{name}.dat')
        with open(path, 'rb') as f:
            out = pickle.load(f)
        return out

    @staticmethod
    def printObjectPropertiesToFile(obj, filePath):
        with open(filePath, 'w') as file:
            for propName in dir(obj):
                if propName.startswith('_'):
                    continue  # Skip private/internal properties

                propValue = getattr(obj, propName)
                if isinstance(propValue, list):
                    file.write(f"{propName}: {', '.join(map(str, propValue))}\n")
                elif isinstance(propValue, dict):
                    for key, value in propValue.items():
                        if isinstance(value, list):
                            file.write(f"{propName}[{key}]: {', '.join(map(str, value))}\n")
                        else:
                            file.write(f"{propName}[{key}]: {value}\n")
                else:
                    file.write(f"{propName}: {propValue}\n")

    @staticmethod
    def log(val):
        exPath = os.path.join(Utils.programFolder, 'log.txt')
        with open(exPath, 'a') as log_file:  # Append mode
            log_file.write(val + '\n')

    @staticmethod
    def logList(lst):
        out = '\n'.join(lst)
        Utils.log('\n' + out)

    @staticmethod
    def logDic(dic):
        out = '\n'.join(f"{key}:\n  " + '\n  '.join(value) for key, value in dic.items())
        Utils.log('\n' + out)

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

class QListWidgetGame(QListWidgetItem):
    def __init__(self, text='', game=None):
        super().__init__(text)
        self.game = game

    def setGame(self, var):
        self.game = var

    def getGame(self):
        return self.game

    def __repr__(self):
        return (f"Text={self.text()}, Game(name={self.game.name}, romPath={self.game.romPath}, system={self.game.system}, "
            f"mediaFolder={self.game.mediaFolder}, pictures={self.game.pictures}, video={self.game.video}, "
            f"updatePath={self.game.updatePath}, dlc={self.game.dlc}, gamelistEntry={self.game.gamelistEntry})")

class Game():
    def __init__(self, name=''):
        self.name = name
        self.romPath = None # path to the rom file
        self.system = None # game system name
        self.mediaFolder = None # downloaded_media path
        self.pictures = [] # paths to jpgs & pngs
        self.video = None # path to video file
        self.updatePath = None # path to game update file !!!THERE SHOULD ONLY BE 1!!!
        self.dlc = [] # paths to any DLC files
        self.gamelistEntry = None # a <game> element from xmlRoot

    def removeTag(tag):
        self.name = re.sub(r'\s*[\[\(]{tag}?[\]\)]', '', tag)

    def __repr__(self):
        return (f"Game(name={self.name}, romPath={self.romPath}, system={self.system}, "
            f"mediaFolder={self.mediaFolder}, pictures={len(self.pictures)}, video={self.video}, "
            f"updatePath={self.updatePath}, dlc={len(self.dlc)}, gamelistEntry={self.gamelistEntry})")

class DataWarehouse():
    def __init__(self):
        self.systems = {} # dic of name,GameSystem objects
        self.gamelistFiles = [] # paths to gamelist.xml files
        self.gamelists = {} # dic of gamelist XML; k,v = systemName,XMLRoot
        self.mediaFolder = '' # downloaded_media path
        self.media = [] # paths to all pics & vids
        self.updateFolder = '' # path to updates/dlc folder
        self.updates = [] # paths to all game update files
        self.dlc = [] # paths to all DLC files
        self.romsFolder = ''

    def sort(self):
        self.systems = dict(sorted(self.systems.items()))
        self.gamelistFiles = sorted(self.gamelistFiles)
        self.gamelists = dict(sorted(self.gamelists.items()))
        self.media = sorted(self.media)
        self.updates = sorted(self.updates)
        self.dlc = sorted(self.dlc)

    def save(self):
        Utils.serializeCollection(self.systems, 'systems')
        Utils.serializeCollection(self, 'data')

    def load(self):
        self = Utils.deserializeCollection('data')
        return self

    def loadSystems(self):
        for name in self.gamelists.keys():
            try:
                tmp = GameSystem(name)
                tmp.gamelistPath = next((file for file in self.gamelistFiles if f'/{name}/' in file), None)
                tmp.mediaDir = os.path.join(self.mediaFolder, name)
                tmp.updateDlcDir = os.path.join(self.mediaFolder, name)
                tmp.romDir = os.path.join(self.romsFolder, name)
                tmp.loadGamelist()
                tmp.loadMediaFiles(self.media)
                tmp.loadUpdates(self.updates)
                tmp.loadDlc(self.dlc)
                tmp.loadRoms()
                tmp.loadGames()
                self.systems[name] = tmp
            except Exception as e:
                exPath = os.path.join(Utils.programFolder, 'exception.txt')
                with open(exPath, 'a') as log_file:  # Append mode
                    log_file.write("Exception occurred:\n")
                    traceback.print_exc(file=log_file)
        self.sort()

    def __repr__(self):
        return (f"systemCount={len(self.systems)}, "
            f"mediaCount={len(self.media)}, "
            f"updateCount={len(self.updates)}, "
            f"dlcCount={len(self.dlc)}, "
            f"gamelistFiles={len(self.gamelistFiles)}, "
            f"mediaFolder={self.mediaFolder}, "
            f"updateFolder={self.updateFolder}, romsFolder={self.romsFolder}")

class GameSystem():
    def __init__(self, name=''):
        self.name = name
        self.gamelistPath = '' # path to system's gamelist.xml file
        self.gamelist = None # loaded gamelist XML
        self.mediaDir = '' # path to downloaded_media folder
        self.mediaFiles = {} # paths to all media files
        self.updateDlcDir = '' # path to system's updates folder
        self.updateFiles = [] # paths to all update files
        self.dlcFiles = [] # paths to all DLC files
        self.romDir = '' # path to system's /roms directory
        self.roms = [] # paths to all ROMs
        self.games = {} # list of Game objects

    def sort(self):
        # sort all collections
        self.mediaFiles = dict(sorted(self.mediaFiles.items()))
        self.updateFiles = sorted(self.updateFiles)
        self.dlcFiles = sorted(self.dlcFiles)
        self.roms = sorted(self.roms)
        self.games = dict(sorted(self.games.items()))

    def loadGamelist(self):
        # load the gamelist xml into self.gamelist
        self.gamelist = Utils.loadXmlFile(self.gamelistPath)

    def loadMediaFiles(self, files):
        # load all pic & vid files from downloaded_media to self.mediaFiles
        out = {}
        for f in files:
            if self.name in f:
                name = Path(f).stem
                if name not in self.mediaFiles.keys():
                    self.mediaFiles[name] = []
                self.mediaFiles[name].append(f)

    def loadUpdates(self, files):
        # load all update files from downloaded_media to self.updateFiles
        for f in files:
            if self.name in f:
                # files should already be filtered to be only update files
                self.updateFiles.append(f)

    def loadDlc(self, files):
        # load all dlc files from downloaded_media to self.dlcFiles
        for f in files:
            if self.name in f:
                # files should already be filtered to be only DLC files
                self.dlcFiles.append(f)

    def loadRoms(self):
        # build a list of ROM files
        self.roms = Utils.getRoms(self.romDir)

    def loadGames(self):
        # Create the dic of Game objects
        for file in self.roms:
            tmp = Game(Path(file).stem)
            tmp.romPath = file
            tmp.system = self.name
            tmp.mediaFolder = self.mediaDir
            try:
                tmp.pictures = [f for f in self.mediaFiles.get(tmp.name) if '.mp4' not in f]
                tmp.video = next((f for f in self.mediaFiles.get(tmp.name) if '.mp4' in f), None)
            except Exception as e:
                exPath = os.path.join(Utils.programFolder, 'exception.txt')
                with open(exPath, 'a') as log_file:  # Append mode
                    log_file.write(f"SYSTEM:{tmp.system}  GAME:{tmp.name}\n")
                    traceback.print_exc(file=log_file)
                    log_file.write("\n\n")
            tmp.updatePath = next((f for f in self.updateFiles if tmp.name in f), None)
            tmp.dlc = [f for f in self.dlcFiles if tmp.name in f]
            tmp.gamelistEntry = Utils.findGameByName(self.gamelist, tmp.name)
            # change name from the filename to gamelist entry name
            tmp.name = tmp.gamelistEntry.find('name').text
            self.games[tmp.name] = tmp
        self.games = dict(sorted(self.games.items()))


    def getGame(self, name):
        return next((game for game in self.games.values() if game.name == name), None)

    def getGameByProperty(self, propName, value):
        # Use getattr to access the attribute dynamically based on propName
        matchingGame = next((game for game in self.games.values() if getattr(game, propName) == value), None)
        return matchingGame

    def __repr__(self):
        return (f"name={self.name}, mediaFiles={len(self.mediaFiles)}, gamelistPath={self.gamelistPath}, "
                f"mediaDir={self.mediaDir}, updateDlcDir={self.updateDlcDir}, "
                f"romDir={self.romDir}, games.count={self.games.count()})")

class AbandonedFunctions:
    def loadRomsDirectories(self):
        # this logic could be useful for finding active rom directories
        for dir in sorted(Utils.getDirsInDir(self.conman.get('folders', 'romsFolder'))):
            if not Path(dir).is_symlink():
                size, count = Utils.getDirectorySizeAndFileCount(dir)
                if size > 2000: # horrendous active directory detection, fix the fuck outta me
                    self.conman.append('misc', 'activeromdirs', dir.replace(self.conman.get('misc', 'romsdirectory'), ''))
        self.conman.save()

    #these next 2 might be useful for scraping or something?
    def loadMedia(self, game):
        # populate game's .pictures array and .video if exists
        media = Utils.loadMediaDic(game.mediaFolder)
        name = game.name
        if media.get(name):
            for entry in media.get(name):
                if Path(entry).suffix == '.mp4':
                    game.video = entry
                else:
                    game.pictures.append(entry)

    def loadUpdatesDLC(self, game):
        # get updates & DLC
        for root, dirs, files in os.walk(game.updatePath):
            for filename in fnmatch.filter(files, game.name + '*.*'):
                if 'UPDATE' in filename:
                    game.updatePath = filename
                else:
                    game.dlc.append(filename)

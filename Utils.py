import sys, os, fnmatch, configparser
from pathlib import Path
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex

class Utils:
    def __init__(self):
        pass

    def getFilesInDir(directory):
        files = []
        for f in os.listdir(directory):
            fullPath = os.path.join(directory, f)
            if os.path.isfile(fullPath):
                files.append(fullPath)
        return files

    def getFilesInSubDirs(directory):
        files = []
        for dirpath, _, filenames in os.walk(directory):
            for f in filenames:
                files.append(os.path.join(dirpath, f))
        return files

    def loadMediaDic(directory):
        files = getFilesInSubDirs(directory)


    @staticmethod
    def getGameLists(directory, file_mask):
        result = {}
        if not file_mask:
            file_mask = "gamelist.xml"

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
        ignoreList = ["metadata.txt", "systeminfo.txt"]
        filePaths = []

        # Iterate over files in the specified directory
        for fileName in getFilesInDir(directory):
            if fileName not in ignoreList:
                filePaths.append(fileName)

        return filePaths

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

    def getDirectorySizeAndFileCount(directoryPath):
        """
        Returns the total size and number of files in the specified directory.

        :param directoryPath: Path to the directory to analyze.
        :return: A tuple containing the total size in bytes and the file count.
        """
        totalSize = 0
        fileCount = 0

        for dirpath, dirnames, filenames in os.walk(directoryPath):
            for filename in filenames:
                filePath = os.path.join(dirpath, filename)
                totalSize += os.path.getsize(filePath)
                fileCount += 1

        #Example usage
        #size, count = getDirectorySizeAndFileCount('/path/to/directory')
        #print(f'Total Size: {size} bytes, Number of Files: {count}')
        return totalSize, fileCount


    def showDialog(self, parent, title, text, buttonText):
            msgBox = QMessageBox(parent)
            msgBox.setWindowTitle(title)
            msgBox.setText(text)
            msgBox.addButton(buttonText, QMessageBox.AcceptRole)
            msgBox.exec_()

    def findGameByName(root, gameName):
        for game in root.findall('game'):
            nameElement = game.find('name')
            if nameElement is not None and nameElement.text == gameName:
                return game
        return None

    @staticmethod
    def setClipboardText(str):
        clipboard = QApplication.clipboard()
        clipboard.setText(str)


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
            self.config['Folders'] = {
                'defaultFolder': '/home/deck',
                'gamelistsFolder': '/home/deck/ES-DE/gamelists/',
                'romsFolder': '/run/media/deck/ed4e9ecc-0701-43e2-9727-91b64daef9dc/Emulation/roms',
                'gameSystemFolder': ''
            }
            self.config['Misc'] = {
                'gamelistsMask': 'gamelist.xml',
            }
            self.save()  # Create config file if it doesn't exist

    def get(self, section, option, fallback=None):
        """Retrieve a setting with a fallback value."""
        return self.config.get(section, option, fallback=fallback)

    def set(self, section, option, value):
        """Update or add a setting."""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][option] = value
        self.save_settings()

    def save(self):
        """Write settings back to the config file."""
        with open(self.configPath, 'w') as configfile:
            self.config.write(configfile)

######################################
##########v REFERENCE CODE v##########
#for index in range(self.ui.lstCheckedRoms.count()):
#    item = self.ui.lstCheckedRoms.item(index)
#    if item.checkState() == Qt.Checked:
#        print(f"{item.text()} is checked")
#QMessageBox.information(self, "Item Clicked", f"You clicked: {selected_item_text}")
#        # Set the model for the tree view
#        self.ui.tvGamelists.setModel(self.model)
#        # Set the tree view to start at /home/deck
#        self.ui.tvGamelists.setRootIndex(self.model.index('/home/deck/Emulation/roms'))
#        # Set the width of the 'Name' column (index 0)
#        self.ui.tvGamelists.setColumnWidth(0, 250)
#def on_btnLoad_click(self):
#    # Open a folder selection dialog
#    QMessageBox.critical(self, "Exception", "{e}")
#    folderPath = QFileDialog.getExistingDirectory(self, "Select Folder")
#    if folderPath:  # If a folder was selected
#        # Set the model's root path to the selected folder
#        self.model.setRootPath(folderPath)
#        # Expand the tree view to show the contents of the selected folder
#        self.ui.tvGamelists.setRootIndex(self.model.index(folderPath))

#def populateTreeView(self, treeView):
#    model = QStandardItemModel()  # Create the model
#    model.setHorizontalHeaderLabels(["Games"])  # Set header for the tree view

#    for game in self.xmlRoot.findall('game'):
#        gameItem = QStandardItem(game.find('name').text)  # Create a parent item for each game
#        model.appendRow(gameItem)  # Add the game item to the model

#        # Iterate over each property in the game
#        for child in game:
#            if child.tag.upper() == "DESC":
#                desc = child.text if child.text is not None else ""
#                cleanDesc = "\n".join(line for line in desc.splitlines() if line.strip())  # Remove excess blank lines
#                propItem = QStandardItem(f"{child.tag.upper()}:")

#                if cleanDesc:
#                    propItem.appendRow(QStandardItem(cleanDesc))
#                gameItem.appendRow(propItem)
#            else:
#                propItem = QStandardItem(f"{child.tag.upper()}: {child.text}")  # Create item for each property
#                gameItem.appendRow(propItem)

#    self.ui.tvGamelists.setModel(model)  # Set the model to the QTreeView
#    self.ui.txtDesc.setVisible(False)
##########^ REFERENCE CODE ^##########
######################################

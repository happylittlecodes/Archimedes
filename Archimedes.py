import os, sys, configparser
import xml.etree.ElementTree as ET
from ui_form import Ui_MainWindow # generated UI class

from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QLabel, QTextEdit, QTreeView, QFileSystemModel, QFileDialog, QFileSystemModel, QRadioButton, QVBoxLayout, QListWidgetItem
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QUrl

from Utils import Utils, FileSystemModel, SettingsManager

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Create an instance of the UI class
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # Set up the UI in the main window

        # Initialize the QFileSystemModel
        self.model = QFileSystemModel()
        self.model.setRootPath('/home/deck')

        # Instance vars
        self.videoWidget = QVideoWidget(self.ui.tabMedia)
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        programFolder = os.path.dirname(os.path.abspath(__file__))
        self.configPath = os.path.join(programFolder, 'config.ini')
        self.setMan = SettingsManager(self.configPath)
        self.gamelists = {}
        self.mediaDic = {}
        self.xmlRoot = None
        self.romList = None
        self.currentGame = None
        self.currentXmlPath = None
        self.model = None

        # Connect controls to functions
        self.ui.btnLoadRomDir.clicked.connect(self.on_btnLoadRomDir_click)
        self.ui.btnLoadMedia.clicked.connect(self.on_btnLoadMedia_click)
        self.ui.btnGamelists.clicked.connect(self.on_btnGamelists_click)
        self.ui.btnAddGame.clicked.connect(self.on_btnAddGame_click)
        self.ui.btnSaveChanges.clicked.connect(self.on_btnSaveChanges_click)
        self.ui.btnDeleteGamelistEntry.clicked.connect(self.on_btnDeleteGamelistEntry_click)
        self.ui.lvMedia.clicked.connect(self.on_lvMedia_click)
        self.ui.lwGamelists.itemClicked.connect(self.on_lwGamelists_item_clicked)
        self.ui.lwGames.itemClicked.connect(self.on_lwGames_item_clicked)
        self.ui.tcTabs.currentChanged.connect(self.onTabChanged)
        self.ui.btnTemp.clicked.connect(self.on_btnTemp_click)

        # Startup operations
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.videoWidget.setGeometry(420, 10, 640, 480)
        self.videoWidget.hide()
        self.ui.lblImage.hide()
        self.loadGamelists(self.setMan.get('Folders','gamelistsFolder'), self.setMan.get('Misc','gamelistsMask'))

    def onTabChanged(self, index):
        if index == 2:  # Tab 3 is at index 2
            self.resize(1100, 900)  # Set larger size for window
            self.ui.tcTabs.setFixedSize(1098, 800)  # Set larger size for tab container
        else:
            self.resize(1070, 900)  # Revert to original size for window
            self.ui.tcTabs.setFixedSize(1070, 780)  # Revert to original size for tab container

###############################################
###############v GAMELISTS TAB v###############
    def on_btnSaveChanges_click(self):
        updatedValues = self.getGameProperties()
        self.updateCurrentGame(updatedValues)
        Utils.saveXMLToFile(self.currentXmlPath, self.xmlRoot)

    def on_btnAddGame_click(self):
        self.currentGame = ET.Element("game")

        for tag, value in self.getGameProperties().items():
            childElement = ET.SubElement(self.currentGame, tag)
            childElement.text = value

        self.xmlRoot.append(self.currentGame)
        Utils.saveXMLToFile(self.currentXmlPath, self.xmlRoot)

    def on_btnDeleteGamelistEntry_click(self):
        self.xmlRoot.remove(self.currentGame)
        Utils.saveXMLToFile(self.currentXmlPath, self.xmlRoot)

    def getGameProperties(self):
        return {
            'name': self.ui.txtName.text(),
            'path': self.ui.txtPath.text(),
            'rating': self.ui.txtRating.text(),
            'developer': self.ui.txtDeveloper.text(),
            'publisher': self.ui.txtPublisher.text(),
            'genre': self.ui.txtGenre.text(),
            'players': self.ui.txtPlayers.text(),
            'desc': self.ui.txtDesc.toPlainText()
        }

    def updateCurrentGame(self, updatedValues):
        """
        Updates multiple child tags of the current <game> object (self.currentGame).

        :param updatedValues: A dictionary containing the tag names as keys and the new text as values.
        """
        if self.currentGame is None:
            Utils().showDialog(self, "No", "No game selected", "Whoops!")
            return

        # Loop through the updated values and update corresponding child tags
        for tag, newText in updatedValues.items():
            childElement = self.currentGame.find(tag)
            if childElement is not None:
                childElement.text = newText
            else:
                newElement = ET.Element(tag)
                newElement.text = newText
                self.currentGame.append(newElement)  # Add the new element to the current <game>

    def updateXMLRootWithCurrentGame(self):
        gameName = self.currentGame.find('name').text
        existingGame = self.xmlRoot.find(f"./game[name='{gameName}']")
        if existingGame is not None:
            self.xmlRoot.remove(existingGame)
            self.xmlRoot.append(self.currentGame)

    def on_btnGamelists_click(self):
        # Open a folder selection dialog
        folderPath = QFileDialog.getExistingDirectory(self, "Select Gamelists Folder")

        if folderPath:  # If a folder was selected
            try:
                self.loadGamelists(folderPath, "gamelist.xml")
            except Exception as e:
                print(f"An error occurred: {e}")
                QMessageBox.critical(self, "Exception", "{e}")

    def loadGamelists(self, directory, mask):
        self.gamelists = Utils.getGameLists(directory, mask)
        self.gamelists = dict(sorted(self.gamelists.items()))
        self.ui.lwGamelists.addItems(self.gamelists.keys())

    def on_lwGamelists_item_clicked(self, item):
        self.ui.lwGames.clear()
        # Get the string value of the selected item
        self.currentXmlPath = self.gamelists[item.text()]
        self.xmlRoot = Utils.loadXmlFile(self.currentXmlPath)  # Load the XML file
        for game in self.xmlRoot.findall('game'):
            self.ui.lwGames.addItem(game.find('name').text)
        # Clear form controls
        self.ui.txtName.setText("")
        self.ui.txtPath.setText("")
        self.ui.txtRating.setText("")
        self.ui.txtDeveloper.setText("")
        self.ui.txtPublisher.setText("")
        self.ui.txtGenre.setText("")
        self.ui.txtPlayers.setText("")
        self.ui.txtDesc.setPlainText("")

    def on_lwGames_item_clicked(self, item):
        # Get the string value of the selected item
        sGame = item.text()
        self.currentGame = Utils.findGameByName(self.xmlRoot, sGame)

        self.ui.txtName.setText(sGame if sGame is not None else "")

        nameElement = self.currentGame.find('path')
        self.ui.txtPath.setText(nameElement.text if nameElement is not None else "")

        nameElement = self.currentGame.find('rating')
        self.ui.txtRating.setText(nameElement.text if nameElement is not None else "")

        nameElement = self.currentGame.find('developer')
        self.ui.txtDeveloper.setText(nameElement.text if nameElement is not None else "")

        nameElement = self.currentGame.find('publisher')
        self.ui.txtPublisher.setText(nameElement.text if nameElement is not None else "")

        nameElement = self.currentGame.find('genre')
        self.ui.txtGenre.setText(nameElement.text if nameElement is not None else "")

        nameElement = self.currentGame.find('players')
        self.ui.txtPlayers.setText(nameElement.text if nameElement is not None else "")

        nameElement = self.currentGame.find('desc')
        self.ui.txtDesc.setPlainText(nameElement.text if nameElement is not None else "")
###############^ GAMELISTS TAB ^###############
###############################################

###############################################
#################v ROMS TAB v##################
    def on_btnLoadRomDir_click(self):
        folderPath = QFileDialog.getExistingDirectory(self, 'Select ROMs Folder', self.setMan.get('Folders', 'romsFolder'))
        self.romList = Utils.getRoms(folderPath)
        fileNames = [os.path.basename(filePath) for filePath in self.romList]  # Extract filenames
        self.ui.lstRoms.addItems(fileNames)
        uniqueOptions = set()  # Set to hold unique options

        # Iterate over all file names to find values in parentheses
        for fileName in fileNames:
            matches = re.findall(r'\((.*?)\)', fileName)
            for match in matches:
                options = match.split(',')
                uniqueOptions.update(option.strip() for option in options)  # Add stripped options to the set

        if self.ui.grpRadioBtns.layout() is None:
            self.ui.grpRadioBtns.setLayout(QVBoxLayout())

        for value in uniqueOptions:
            radioBtn = QRadioButton(value)
            radioBtn.toggled.connect(self.onRadioButtonChecked)
            self.ui.grpRadioBtns.layout().addWidget(radioBtn)

    def onRadioButtonChecked(self):
        # Get the selected radio button
        selectedButton = self.sender()
        if selectedButton:
            self.ui.lstFilteredRoms.clear()
            text = selectedButton.text()
            for index in range(self.ui.lstRoms.count()):
                item = self.ui.lstRoms.item(index)
                if text in item.text():
                    # Add a new checkable item to the filtered list
                    newItem = QListWidgetItem(item.text())
                    newItem.setFlags(newItem.flags() | Qt.ItemIsUserCheckable)
                    newItem.setCheckState(Qt.Unchecked)
                    self.ui.lstFilteredRoms.addItem(newItem)


#################^ ROMS TAB ^##################
###############################################

###############################################
#################v MEDIA TAB v#################
    def displayImage(self, imagePath):
        self.videoWidget.hide()
        self.mediaPlayer.stop()
        pixmap = QPixmap(imagePath)
        self.ui.lblImage.setPixmap(pixmap)
        self.ui.lblImage.setScaledContents(True)  # Scale the image to fit the label
        self.ui.lblImage.show()

    def playVideo(self, videoPath):
        self.ui.lblImage.hide()
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(videoPath)))
        self.videoWidget.show()
        self.mediaPlayer.play()

    def on_btnTemp_click(self):
        self.displayImage('/run/media/deck/ed4e9ecc-0701-43e2-9727-91b64daef9dc/Emulation/roms/wiiu/roms/media/titlescreens/Legend of Zelda, The - Breath of the Wild (USA) (En,Fr,Es).jpg')

    def on_btnLoadMedia_click(self):
#        self.playVideo('/home/deck/Emulation/tools/downloaded_media/switch/videos/The Legend of Zelda Tears of the Kingdom.mp4')
        folderPath = QFileDialog.getExistingDirectory(self, 'Select Media Folder', self.setMan.get('Folders', 'mediafolder'))
        files = Utils.getRoms(folderPath)
        fileNames = [os.path.basename(filePath) for filePath in self.romList]  # Extract filenames
        self.ui.lstRoms.addItems(fileNames)
        self.model = FileSystemModel(folderPath)


    def on_lvMedia_click(self):
        filePath = os.path.join(self.model.rootPath, self.model.data(index))
        if os.path.isfile(filePath):
            # detect media type, route to Uitls.displayImage()/playVideo() or
            Utils().playVideo(self, filePath)


#################^ MEDIA TAB ^#################
###############################################

if __name__ == "__main__":
    app = QApplication(sys.argv)  # Create the application
    window = MainWindow()  # Create the main window
    window.show()  # Show the window
    sys.exit(app.exec_())  # Execute the application

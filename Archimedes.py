import os, sys, configparser
import xml.etree.ElementTree as ET
from ui_form import Ui_MainWindow # generated UI class
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QLabel, QTextEdit, QTreeView, QFileSystemModel, QFileDialog, QFileSystemModel, QRadioButton, QVBoxLayout, QListWidgetItem
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QUrl, pyqtSlot, QThread
import pickle

from Utils import Utils, FileSystemModel, SettingsManager, Thumbnail, Game

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
        self.videoWidget = QVideoWidget(self.ui.tabGames)
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        programFolder = os.path.dirname(os.path.abspath(__file__))
        self.configPath = os.path.join(programFolder, 'config.ini')
        self.conMan = SettingsManager(self.configPath)
        self.imageExtensions = ['.png','.jpg']
        self.videoExtensions = ['.mp4']
        self.gamelists = {}
        self.mediaDic = {}
        self.xmlRoot = None
        self.romList = None
        self.currentGame = None
        self.currentSystem = None
        self.currentXmlPath = None
        self.model = None
        self.games = {}
        self.thread = None
        self.worker = None

        # Connect controls to event handlers
        self.ui.btnLoadRomDir.clicked.connect(self.on_btnLoadRomDir_click)
        self.ui.btnLoadMedia.clicked.connect(self.on_btnLoadMedia_click)
        self.ui.btnGamelists.clicked.connect(self.on_btnGamelists_click)
        self.ui.btnAddGame.clicked.connect(self.on_btnAddGame_click)
        self.ui.btnSaveChanges.clicked.connect(self.on_btnSaveChanges_click)
        self.ui.btnDeleteGamelistEntry.clicked.connect(self.on_btnDeleteGamelistEntry_click)
        #self.ui.lvMedia.itemClicked.connect(self.on_lvMedia_item_click)
        self.ui.lwGames.itemClicked.connect(self.on_lwGames_item_clicked)
        self.ui.tcTabs.currentChanged.connect(self.onTabChanged)
        self.ui.cmbSystems.activated.connect(self.on_cmbSystems_activated)

        # Startup operations
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.videoWidget.setGeometry(209, 300, 650, 430)
        self.ui.grpMedia.setLayout(QVBoxLayout())
        self.videoWidget.hide()
        self.ui.lblImage.hide()
        #self.loadGamelists(self.conMan.get('folders','gamelistsFolder'), self.conMan.get('misc','gamelistsMask'))
        self.ui.lblImage.setText('')
        self.ui.grpMedia.setTitle('')

        self.setupForm()

    # this probably won't be needed/desired in the future
    def onTabChanged(self, index):
        if index == 2:  # Tab 3 is at index 2
            self.resize(1100, 900)  # Set larger size for window
            self.ui.tcTabs.setFixedSize(1098, 800)  # Set larger size for tab container
        else:
            self.resize(1070, 900)  # Revert to original size for window
            self.ui.tcTabs.setFixedSize(1070, 780)  # Revert to original size for tab container

###############################################
#################v NEW MODEL v#################
    def setupForm(self):
        # load any folder in the current config.activeRomDirs that actually has roms in it to a ComboBox
        # populate that config entry (imperfectly) if it's empty
        if not self.conMan.get('misc', 'activeRomDirs'):
            self.loadRomsDirectories()

        for dir in self.conMan.get('misc', 'activeRomDirs').split(','):
            self.ui.cmbSystems.addItem(os.path.basename(dir))

    def loadRomsDirectories(self):
        for dir in sorted(Utils.getDirsInDir(self.conMan.get('folders', 'romsFolder'))):
            if not Path(dir).is_symlink():
                size, count = Utils.getDirectorySizeAndFileCount(dir)
                if size > 2000: # horrendous active directory detection, fix the fuck outta me
                    self.conMan.append('misc', 'activeRomDirs', dir)
        self.conMan.save()

    def on_cmbSystems_activated(self, index):
        # load games for the selected system
        self.ui.lwGames.clear()
        self.clearFormMetadata()
        self.currentSystem = self.ui.cmbSystems.currentText()

        try:
            self.xmlRoot = Utils.loadXmlFile(os.path.join(self.conMan.get('folders', 'gamelistsfolder'), self.currentSystem, 'gamelist.xml'))
            folderPath = os.path.join(self.conMan.get('folders','romsfolder'), self.currentSystem)
            romList = Utils.getRoms(folderPath)
        except:
            return

        for romFile in sorted(romList):
            name = Path(romFile).stem
            game = Game(name)
            game.romPath = romFile
            game.system = self.currentSystem
            game.updatePath = self.conMan.get('folders', 'updatefolder')
            game.mediaFolder = os.path.join(self.conMan.get('folders', 'mediafolder'), game.system)
            game.gamelistEntry = Utils.findGameByName(self.xmlRoot, game.name)
            self.loadMedia(game)
            self.loadUpdatesDLC(game)
            self.games['|'.join([name, self.currentSystem])] = game
            self.ui.lwGames.addItem(name)

    def clearFormMetadata(self):
        self.ui.txtName.setText("")
        self.ui.txtPath.setText("")
        self.ui.txtRating.setText("")
        self.ui.txtDeveloper.setText("")
        self.ui.txtPublisher.setText("")
        self.ui.txtGenre.setText("")
        self.ui.txtPlayers.setText("")
        self.ui.txtDesc.setPlainText("")

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

    def on_lwGames_item_clicked(self, item):
        sGame = item.text()
        # game|system is the key for local collection of class Games
        self.currentGame = self.games.get('|'.join([sGame, self.currentSystem]))

        # deal with media
        self.ui.lblImage.hide()
        self.mediaPlayer.stop()
        self.videoWidget.hide()
        self.loadThumbnails(self.currentGame)

        # display the metadata or lack thereof
        if not self.currentGame.gamelistEntry:
            self.clearFormMetadata()
        else:
            nameElement = self.currentGame.gamelistEntry.find('name')
            self.ui.txtName.setText(nameElement.text if nameElement is not None else sGame)

            nameElement = self.currentGame.gamelistEntry.find('path')
            self.ui.txtPath.setText(nameElement.text if nameElement is not None else "")

            nameElement = self.currentGame.gamelistEntry.find('rating')
            self.ui.txtRating.setText(nameElement.text if nameElement is not None else "")

            nameElement = self.currentGame.gamelistEntry.find('developer')
            self.ui.txtDeveloper.setText(nameElement.text if nameElement is not None else "")

            nameElement = self.currentGame.gamelistEntry.find('publisher')
            self.ui.txtPublisher.setText(nameElement.text if nameElement is not None else "")

            nameElement = self.currentGame.gamelistEntry.find('genre')
            self.ui.txtGenre.setText(nameElement.text if nameElement is not None else "")

            nameElement = self.currentGame.gamelistEntry.find('players')
            self.ui.txtPlayers.setText(nameElement.text if nameElement is not None else "")

            nameElement = self.currentGame.gamelistEntry.find('desc')
            self.ui.txtDesc.setPlainText(nameElement.text if nameElement is not None else "")
###############################################
#################^ NEW MODEL ^#################

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
        # update gamelists location in config
        folderPath = QFileDialog.getExistingDirectory(self, "Select Gamelists Folder")
        self.conMan.set('folders', 'gamelistsfolder')
###############^ GAMELISTS TAB ^###############
###############################################

###############################################
#################v ROMS TAB v##################
    def on_btnLoadRomDir_click(self):
        folderPath = QFileDialog.getExistingDirectory(self, 'Select ROMs Folder', self.conMan.get('folders', 'romsFolder'))
        self.romList = Utils.getRoms(folderPath)
        fileNames = [os.path.basename(filePath) for filePath in self.romList]
        fileNames = sorted(fileNames)
        self.ui.lstRoms.clear()
        self.ui.lstRoms.addItems(fileNames)
        uniqueOptions = set()

        # Iterate over all file names to find values in parentheses
        for fileName in fileNames:
            matches = re.findall(r'\((.*?)\)', fileName)
            for match in matches:
                options = match.split(',')
                uniqueOptions.update(option.strip() for option in options)  # Add stripped options to the set

        if self.ui.grpRadioBtns.layout() is None:
            self.ui.grpRadioBtns.setLayout(QVBoxLayout())
        else:
            self.clearGroupBox(self.ui.grpRadioBtns)

        for value in uniqueOptions:
            radioBtn = QRadioButton(value)
            radioBtn.toggled.connect(self.on_RadioButton_Checked)
            self.ui.grpRadioBtns.layout().addWidget(radioBtn)

    def on_RadioButton_Checked(self):
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

################################################
#################v MULTIMEDIA v#################
    def displayImage(self, imagePath):
        self.videoWidget.hide()
        self.mediaPlayer.stop()
        pixmap = QPixmap(imagePath)
        scaledPixmap = pixmap.scaled(self.ui.lblImage.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.lblImage.setPixmap(scaledPixmap)
        self.ui.lblImage.setAlignment(Qt.AlignCenter)
        self.ui.lblImage.show()

    def playVideo(self, videoPath):
        self.ui.lblImage.hide()
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(videoPath)))
        self.videoWidget.show()
        self.mediaPlayer.play()

    # REMOVE ME AND CONTROL
    def on_btnLoadMedia_click(self):
        self.ui.lvMedia.clear()
        folderPath = QFileDialog.getExistingDirectory(self, 'Select Media Folder', self.conMan.get('folders', 'mediafolder'))
        self.mediaDic = Utils.loadMediaDic(folderPath)
        self.mediaDic = dict(sorted(self.mediaDic.items()))
        self.ui.lvMedia.addItems(self.mediaDic.keys())

    def loadThumbnails(self, game):
        self.clearGroupBox(self.ui.grpMedia)

        # load video thumbnail
        thumb = Utils.get_video_thumbnail(game.video)
        pixmap = QPixmap(thumb)
        self.createThumbnail(game.video, pixmap)

        # load image thumbnails
        for file in game.pictures:
            pixmap = QPixmap(file)
            self.createThumbnail(file, pixmap)

    def createThumbnail(self, file, pixmap):
        label = Thumbnail(file)
        label.setFixedSize(64, 48)
        scaledPixmap = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(scaledPixmap)
        label.setAlignment(Qt.AlignCenter)
        label.show()
        label.clicked.connect(self.on_thumbnail_clicked)
        self.ui.grpMedia.layout().addWidget(label)

    def on_thumbnail_clicked(self):
        selectedThumbnail = self.sender()
        if selectedThumbnail:
            if Path(selectedThumbnail.path).suffix in self.videoExtensions:
                self.playVideo(selectedThumbnail.path)
            else:
                self.displayImage(selectedThumbnail.path)
#################^ MULTIMEDIA ^#################
################################################


    def clearGroupBox(self, group):
        layout = group.layout()
        if layout:
            # Iterate over the layout items in reverse order and remove them
            for i in reversed(range(layout.count())):
                widget = layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()  # Safely delete the widget from memory
            layout.invalidate()  # Update the layout

if __name__ == "__main__":
    app = QApplication(sys.argv)  # Create the application
    window = MainWindow()  # Create the main window
    window.show()  # Show the window
    sys.exit(app.exec_())  # Execute the application

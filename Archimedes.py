import os, sys, configparser, cv2
import xml.etree.ElementTree as ET
from ui_form import Ui_MainWindow # generated UI class
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QLabel, QTextEdit, QTreeView, QFileSystemModel
from PyQt5.QtWidgets import QFileDialog, QFileSystemModel, QRadioButton, QGridLayout, QVBoxLayout, QListWidgetItem
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QUrl, pyqtSlot, QThread
import pickle

from Utils import Utils, FileSystemModel, SettingsManager, Thumbnail, Game, QListWidgetGame, DataWarehouse, GameSystem

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Create an instance of the UI class
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # Set up the UI in the main window

        self.setupMode = True
        if self.setupMode:
            try:
                os.remove(os.path.join(Utils.programFolder, 'data.dat'))
                os.remove(os.path.join(Utils.programFolder, 'systems.dat'))
            except:
                pass
            #Utils().showDialog(self, "Initial Setup", "This is gonna take a while", "K")
#        # Initialize the QFileSystemModel
#        self.model = QFileSystemModel()
#        self.model.setRootPath('/home/deck')
#        self.model = None

        # Instance vars
        self.videoWidget = QVideoWidget(self.ui.tabGames)
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.programFolder = os.path.dirname(os.path.abspath(__file__))
        self.configPath = os.path.join(self.programFolder, 'config.ini')
        self.conman = SettingsManager(self.configPath)
        self.imageExtensions = self.conman.get('misc','imageextensions').split(',')
        self.videoExtensions = self.conman.get('misc','videoextensions').split(',')
        self.xmlRoot = None
        self.romList = None
        self.currentGame = Game()
        self.currentSystem = None
        self.currentXmlPath = None
        self.games = {}
        self.dataWarehouse = self.loadDataWarehouse() if self.setupMode else DataWarehouse().load()

        # Connect controls to event handlers
        self.ui.btnGamelists.clicked.connect(self.on_btnGamelists_click)
        self.ui.btnAddGame.clicked.connect(self.on_btnAddGame_click)
        self.ui.btnSaveChanges.clicked.connect(self.on_btnSaveChanges_click)
        self.ui.btnDeleteGamelistEntry.clicked.connect(self.on_btnDeleteGamelistEntry_click)
        self.ui.lwGames.itemClicked.connect(self.on_lwGames_item_clicked)
        self.ui.tcTabs.currentChanged.connect(self.onTabChanged)
        self.ui.cmbSystems.activated.connect(self.on_cmbSystems_activated)
        self.ui.btnRemoveSelectedTag.clicked.connect(self.on_btnRemoveSelectedTag_click)
        self.ui.btnRemoveAllTags.clicked.connect(self.on_btnRemoveAllTags_click)
        self.ui.btnDeleteSelectedRoms.clicked.connect(self.on_btnDeleteSelectedRoms_click)
        self.ui.chkAll.stateChanged.connect(self.on_chkAll_Checked)
        self.ui.btnSerialize.clicked.connect(self.on_btnSerialize_click)
        self.ui.btnDeserialize.clicked.connect(self.on_btnDeserialize_click)

        # Startup operations
        self.ui.tcTabs.setCurrentIndex(0)
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.videoWidget.setGeometry(20, 310, 670, 370)
        self.ui.grpMedia.setLayout(QGridLayout())
        self.videoWidget.hide()
        self.ui.lblImage.hide()
        self.ui.lblImage.setText('')
        self.ui.grpMedia.setTitle('')
        self.ui.lblMedia.setText('')
        self.ui.lblMarquee.setText('')

        for gs in self.dataWarehouse.systems.keys():
            self.ui.cmbSystems.addItem(gs)

        if self.setupMode:
            Utils().showDialog(self, "Ready", "Loading finished", "thx")

    def loadDataWarehouse(self):
        # load all data the program will need
        out = DataWarehouse()
        out.gamelistFiles = Utils.getGameLists(self.conman.get('folders', 'gamelistsfolder'))
        for x in out.gamelistFiles:
            out.gamelists[os.path.basename(os.path.dirname(x))] = Utils.loadXmlFile(x)
        out.mediaFolder = self.conman.get('folders', 'mediafolder')
        out.media = Utils.getFilesInSubDirs(out.mediaFolder)
        out.updateFolder = self.conman.get('folders', 'updatefolder')
        out.romsFolder = self.conman.get('folders', 'romsfolder')

        for root, dirs, files in os.walk(out.updateFolder):
            for filename in files:
                if 'UPDATE' in filename:
                    out.updates.append(filename)
                elif 'DLC' in filename:
                   out.dlc.append(filename)

        out.loadSystems()
        out.save()
        return out

    def on_btnSerialize_click(self):
        Utils.serializeGames(self.games)

    def on_btnDeserialize_click(self):
        self.games = Utils.deserializeGames()

    def onTabChanged(self, index):
        if index == 0:
            self.resize(1565, 785)  # window size
            self.ui.tcTabs.setFixedSize(1190, 761)  # tab container size
        else:
            self.resize(1028, 785)  # window size
            self.ui.tcTabs.setFixedSize(650, 761)  # tab container size

####################################################
###############v METADATA/MEDIA TAB v###############
    def on_cmbSystems_activated(self, index):
        # load games for the selected system into the form-right QListWidget
        self.ui.lwGames.clear()
        self.clearFormMetadata()
        self.clearGroupBox(self.ui.grpMedia)
        self.mediaPlayer.stop()
        self.videoWidget.hide()
        self.currentSystem = self.ui.cmbSystems.currentText()

        for name, g in self.dataWarehouse.systems.get(self.ui.cmbSystems.currentText()).games.items():
            widg = QListWidgetGame(g.name, game = g)
            self.ui.lwGames.addItem(widg)

    def clearFormMetadata(self):
        self.ui.txtName.setText("")
        self.ui.txtPath.setText("")
        self.ui.txtRating.setText("")
        self.ui.txtDeveloper.setText("")
        self.ui.txtPublisher.setText("")
        self.ui.txtGenre.setText("")
        self.ui.txtPlayers.setText("")
        self.ui.txtDesc.setPlainText("")

    def on_lwGames_item_clicked(self, item):
        gameName = item.text()
        game = self.dataWarehouse.systems[self.ui.cmbSystems.currentText()].getGameByProperty('name', gameName)
        self.currentGame = game # delete

        #Utils.printObjectPropertiesToFile(game, os.path.join(Utils.programFolder, f'{gameName}.game'))
        # deal with media
        self.clearGroupBox(self.ui.grpMedia)
        self.ui.lblImage.hide()
        self.ui.lblMarquee.hide()
        self.mediaPlayer.stop()
        self.videoWidget.hide()
        self.loadThumbnails(game)
        self.setRadioButtons()

        # display the metadata or lack thereof
        if not game.gamelistEntry:
            self.clearFormMetadata()
        else:
            nameElement = game.gamelistEntry.find('name')
            self.ui.txtName.setText(nameElement.text if nameElement is not None else sGame)

            nameElement = game.gamelistEntry.find('path')
            self.ui.txtPath.setText(nameElement.text if nameElement is not None else "")

            nameElement = game.gamelistEntry.find('rating')
            self.ui.txtRating.setText(nameElement.text if nameElement is not None else "")

            nameElement = game.gamelistEntry.find('developer')
            self.ui.txtDeveloper.setText(nameElement.text if nameElement is not None else "")

            nameElement = game.gamelistEntry.find('publisher')
            self.ui.txtPublisher.setText(nameElement.text if nameElement is not None else "")

            nameElement = game.gamelistEntry.find('genre')
            self.ui.txtGenre.setText(nameElement.text if nameElement is not None else "")

            nameElement = game.gamelistEntry.find('players')
            self.ui.txtPlayers.setText(nameElement.text if nameElement is not None else "")

            nameElement = game.gamelistEntry.find('desc')
            self.ui.txtDesc.setPlainText(nameElement.text if nameElement is not None else "")

    def on_btnSaveChanges_click(self):
        # this will need to update the game object, I think the GameSystem object should handle xml ops
        updatedValues = self.getGameProperties()
        self.updateGameXML(self.currentGame, updatedValues)
        Utils.saveXMLToFile(self.currentXmlPath, self.xmlRoot)

    def on_btnAddGame_click(self):
        xroot = ET.Element("game")

        for tag, value in self.getGameProperties().items():
            childElement = ET.SubElement(xroot, tag)
            childElement.text = value

        self.xmlRoot.append(xroot)
        self.current.gamelistEntry = xroot
        Utils.saveXMLToFile(self.currentXmlPath, self.xmlRoot)

    def on_btnDeleteGamelistEntry_click(self, xelement=None):
        if xelement is None:
            xelement = self.currentGame
        self.xmlRoot.remove(xelement)
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

    def updateGameXML(game, updatedValues):
        # Updates multiple XML child tags of the Game object
        # Loop through the updated values and update corresponding child tags
        for tag, newText in updatedValues.items():
            childElement = game.gamelistEntry.find(tag)
            if childElement is not None:
                childElement.text = newText
            else:
                newElement = ET.Element(tag)
                newElement.text = newText
                game.gamelistEntry.append(newElement)  # Add the new element to the current <game>

    def on_btnGamelists_click(self):
        # update gamelists location in config
        folderPath = QFileDialog.getExistingDirectory(self, "Select Gamelists Folder")
        self.conman.set('folders', 'gamelistsfolder')
###############^ METADATA/MEDIA TAB ^###############
####################################################
###############################################
#################v ROMS TAB v##################
    def setRadioButtons(self):
        uniqueOptions = set()
        # Iterate over all file names to find values in parentheses
        for index in range(self.ui.lwGames.count()):
            item = self.ui.lwGames.item(index)
            matches = re.findall(r'[\(\[](.*?)[\)\]]', item.text())
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

    def on_RadioButton_Checked(self): #Rework this
        # Get the selected radio button
        selectedButton = self.sender()
        if selectedButton:
            self.ui.lwFilteredRoms.clear()
            text = selectedButton.text()
            for index in range(self.ui.lwGames.count()):
                item = self.ui.lwGames.item(index)
                if text in item.text():
                    # Add a new checkable item to the filtered list
                    newItem = QListWidgetGame(item.text(), game = item.getGame())
                    newItem.setGame
                    newItem.setFlags(newItem.flags() | Qt.ItemIsUserCheckable)
                    newItem.setCheckState(Qt.Unchecked)
                    self.ui.lwFilteredRoms.addItem(newItem)

    def on_chkAll_Checked(self):
        for i in range(self.ui.lwFilteredRoms.count()):
            self.ui.lwFilteredRoms.item(i).setCheckState(self.sender().checkState())
        if self.sender().checkState():
            self.sender().setText('Deselect All')
        else:
            self.sender().setText('Select All')

    def getSelectedRadioBtn(self):
        for radio in groupBox.findChildren(QRadioButton):
            if radio.isChecked():
                return radio

    def getSelectedRoms(self):
        out = []
        for i in range(self.ui.lwFilteredRoms.count()):
            item = self.ui.lwFilteredRoms.item(i)
            if item.checkState() == Qt.Checked:
                out.append(item)
        return out

    def on_btnRemoveSelectedTag_click(self):
        tag = self.getSelectedRadioBtn().text
        for item in self.getSelectedRoms():
            newName = re.sub(r'\s*[\[\(]' + tag + '?[\]\)]', '', item.text()).strip().replace(' .', '.')
            self.renameGame(item.getGame(), newName)

    def on_btnRemoveAllTags_click(self):
        for item in self.getSelectedRoms():
            newName = re.sub(r'\s*[\[\(].*?[\]\)]', '', item.text()).strip().replace(' .', '.')
            self.renameGame(item.getGame(), newName)

    def on_btnDeleteSelectedRoms_click(self):
        for item in self.getSelectedRoms():
            self.deleteGame(item.game)

    def deleteGame(self, game=None):
        if game != None:
            if game.pictures != []:
                for file in game.pictures:
                    os.remove(file)
            if not game.video is None:
                os.remove(game.video)
            if not game.updatePath is None:
                os.remove(game.updatePath)
            if game.dlc != []:
                for file in game.dlc:
                    os.remove(file)
            os.remove(game.romPath)
            self.on_btnDeleteGamelistEntry_click(game.gamelistEntry)

    def renameGame(self, game, newName):
        if game != None:
            game.name = newName
            Utils.renameFile(game.romPath, newName)
            if game.pictures != []:
                for file in game.pictures:
                    Utils.renameFile(file, newName)
            if not game.video is None:
                Utils.renameFile(game.video, newName)
            if not game.updatePath is None:
                Utils.renameFile(game.updatePath, newName)
            if game.dlc != []:
                for file in game.dlc:
                    Utils.renameFile(file, newName)
            # rename on any controls

    def updateXMLRoot(self):
            gameName = self.currentGame.find('name').text
            existingGame = self.xmlRoot.find(f"./game[name='{gameName}']")
            if existingGame is not None:
                self.xmlRoot.remove(existingGame)
                self.xmlRoot.append(self.currentGame)

    def renameGame(self, oldPath, newName):
        game.name = newName
        # gonna need to go through all the media & gamelist entry too
        oldPath = item.getGame().romPath
        newPath = oldPath.replace(item.getGame().name, newName)
        os.rename(oldPath, newPath)
        self.ui.lwFilteredRoms.removeItemWidget(item)




#################^ ROMS TAB ^##################
###############################################
################################################
#################v MULTIMEDIA v#################
    def displayImage(self, imagePath, label=None):
        if label is None:
            label = self.ui.lblImage
        self.videoWidget.hide()
        self.mediaPlayer.stop()
        pixmap = QPixmap(imagePath)
        scaledPixmap = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(scaledPixmap)
        label.setAlignment(Qt.AlignCenter)
        label.show()

    def playVideo(self, videoPath):
        self.ui.lblImage.hide()
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(videoPath)))
        self.videoWidget.show()
        self.mediaPlayer.play()

    def loadThumbnails(self, game):
        self.clearGroupBox(self.ui.grpMedia)
        i = 0

        # load video thumbnail first
        if game.video:
            thumb = self.getVideoThumbnail(game.video)
            pixmap = QPixmap(thumb)
            label = self.createThumbnail(game.video, pixmap)
            row = i // 5  # There will be 2 rows
            col = i % 5   # Each row will have 5 columns
            self.ui.grpMedia.layout().addWidget(label, row, col)
            i += 1

        # load image thumbnails
        for file in game.pictures:
            pixmap = QPixmap(file)
            label = self.createThumbnail(file, pixmap)
            row = i // 5
            col = i % 5
            self.ui.grpMedia.layout().addWidget(label, row, col)
            i += 1
            if 'marquees' in file:
                self.displayImage(file, self.ui.lblMarquee)

    def createThumbnail(self, file, pixmap):
        label = Thumbnail(file)
        label.setFixedSize(128, 96)
        scaledPixmap = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(scaledPixmap)
        label.setAlignment(Qt.AlignCenter)
        label.show()
        label.clicked.connect(self.on_thumbnail_clicked)
        return label

    def getVideoThumbnail(self, videoPath, seconds=5):
        cap = cv2.VideoCapture(videoPath)
        cap.set(cv2.CAP_PROP_POS_MSEC, seconds * 1000)  # Set the time in milliseconds
        success, image = cap.read()
        cap.release()
        if success:
            thumbnailPath = "thumbnail.jpg"
            cv2.imwrite(thumbnailPath, image)  # Save the frame as an image
            return thumbnailPath
        return None

    def on_thumbnail_clicked(self):
        selectedThumbnail = self.sender()
        if selectedThumbnail:
            if Path(selectedThumbnail.path).suffix in self.videoExtensions:
                self.playVideo(selectedThumbnail.path)
                self.ui.lblMedia.setText('Video')
            else:
                self.displayImage(selectedThumbnail.path)
                mediaType = os.path.basename(os.path.dirname(selectedThumbnail.path)).rstrip('s').title()
                if mediaType == '3Dboxe':
                    mediaType = '3D Box'
                self.ui.lblMedia.setText(mediaType)

    def clearGroupBox(self, group):
        layout = group.layout()
        if layout:
            # Iterate over the layout items in reverse order and remove them
            for i in reversed(range(layout.count())):
                widget = layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()  # Safely delete the widget from memory
            layout.invalidate()  # Update the layout
#################^ MULTIMEDIA ^#################
################################################

################################################
################### DESIGN GOALS ###############

# remove all rom tags from selected roms................X
# remove selected tag from selected roms................X
# delete selected roms..................................X
    ## and all associated media & gamelist entries......
# in-folder dupe check (basename, ignore extension).....
# rename files..........................................
## between 3 folders:
    # display differences...............................
    # equalize (move missing files between folders).....
    # mirror............................................
    # copy selected files...............................
    # delete selected roms from one, have it echo out...
# backup media & gamelists (for metadata)...............
# scrape from filestore.................................
# ? scrape from net ?................

################### DESIGN GOALS ###############
################################################

if __name__ == "__main__":
    app = QApplication(sys.argv)  # Create the application
    window = MainWindow()  # Create the main window
    window.show()  # Show the window
    sys.exit(app.exec_())  # Execute the application

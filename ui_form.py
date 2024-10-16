# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'form.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1070, 900)
        self.tcTabs = QtWidgets.QTabWidget(MainWindow)
        self.tcTabs.setGeometry(QtCore.QRect(0, 0, 1070, 780))
        self.tcTabs.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tcTabs.setObjectName("tcTabs")
        self.tabGamelists = QtWidgets.QWidget()
        self.tabGamelists.setObjectName("tabGamelists")
        self.lwGamelists = QtWidgets.QListWidget(self.tabGamelists)
        self.lwGamelists.setGeometry(QtCore.QRect(10, 10, 221, 681))
        self.lwGamelists.setObjectName("lwGamelists")
        self.lwGames = QtWidgets.QListWidget(self.tabGamelists)
        self.lwGames.setGeometry(QtCore.QRect(240, 10, 371, 681))
        self.lwGames.setObjectName("lwGames")
        self.label_9 = QtWidgets.QLabel(self.tabGamelists)
        self.label_9.setGeometry(QtCore.QRect(621, 281, 85, 21))
        self.label_9.setObjectName("label_9")
        self.txtDesc = QtWidgets.QPlainTextEdit(self.tabGamelists)
        self.txtDesc.setGeometry(QtCore.QRect(720, 280, 341, 411))
        self.txtDesc.setAcceptDrops(True)
        self.txtDesc.setReadOnly(False)
        self.txtDesc.setObjectName("txtDesc")
        self.btnGamelists = QtWidgets.QPushButton(self.tabGamelists)
        self.btnGamelists.setGeometry(QtCore.QRect(10, 700, 131, 29))
        self.btnGamelists.setObjectName("btnGamelists")
        self.btnAddGame = QtWidgets.QPushButton(self.tabGamelists)
        self.btnAddGame.setGeometry(QtCore.QRect(840, 700, 111, 29))
        self.btnAddGame.setObjectName("btnAddGame")
        self.btnSaveChanges = QtWidgets.QPushButton(self.tabGamelists)
        self.btnSaveChanges.setGeometry(QtCore.QRect(720, 700, 121, 29))
        self.btnSaveChanges.setObjectName("btnSaveChanges")
        self.layoutWidget = QtWidgets.QWidget(self.tabGamelists)
        self.layoutWidget.setGeometry(QtCore.QRect(619, 11, 441, 268))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_10 = QtWidgets.QLabel(self.layoutWidget)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 0, 0, 1, 1)
        self.txtName = QtWidgets.QLineEdit(self.layoutWidget)
        self.txtName.setObjectName("txtName")
        self.gridLayout.addWidget(self.txtName, 0, 1, 1, 2)
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.txtPath = QtWidgets.QLineEdit(self.layoutWidget)
        self.txtPath.setObjectName("txtPath")
        self.gridLayout.addWidget(self.txtPath, 1, 2, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.layoutWidget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.txtRating = QtWidgets.QLineEdit(self.layoutWidget)
        self.txtRating.setObjectName("txtRating")
        self.gridLayout.addWidget(self.txtRating, 2, 2, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.layoutWidget)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 2)
        self.txtReleaseDate = QtWidgets.QLineEdit(self.layoutWidget)
        self.txtReleaseDate.setObjectName("txtReleaseDate")
        self.gridLayout.addWidget(self.txtReleaseDate, 3, 2, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.layoutWidget)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 2)
        self.txtDeveloper = QtWidgets.QLineEdit(self.layoutWidget)
        self.txtDeveloper.setObjectName("txtDeveloper")
        self.gridLayout.addWidget(self.txtDeveloper, 4, 2, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.layoutWidget)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 5, 0, 1, 2)
        self.txtPublisher = QtWidgets.QLineEdit(self.layoutWidget)
        self.txtPublisher.setObjectName("txtPublisher")
        self.gridLayout.addWidget(self.txtPublisher, 5, 2, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.layoutWidget)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 6, 0, 1, 1)
        self.txtGenre = QtWidgets.QLineEdit(self.layoutWidget)
        self.txtGenre.setObjectName("txtGenre")
        self.gridLayout.addWidget(self.txtGenre, 6, 2, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.layoutWidget)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 7, 0, 1, 2)
        self.txtPlayers = QtWidgets.QLineEdit(self.layoutWidget)
        self.txtPlayers.setObjectName("txtPlayers")
        self.gridLayout.addWidget(self.txtPlayers, 7, 2, 1, 1)
        self.btnDeleteGamelistEntry = QtWidgets.QPushButton(self.tabGamelists)
        self.btnDeleteGamelistEntry.setGeometry(QtCore.QRect(950, 700, 111, 29))
        self.btnDeleteGamelistEntry.setObjectName("btnDeleteGamelistEntry")
        self.tcTabs.addTab(self.tabGamelists, "")
        self.tabRoms = QtWidgets.QWidget()
        self.tabRoms.setObjectName("tabRoms")
        self.btnLoadRomDir = QtWidgets.QPushButton(self.tabRoms)
        self.btnLoadRomDir.setGeometry(QtCore.QRect(10, 10, 131, 29))
        self.btnLoadRomDir.setObjectName("btnLoadRomDir")
        self.lstRoms = QtWidgets.QListWidget(self.tabRoms)
        self.lstRoms.setGeometry(QtCore.QRect(10, 50, 361, 691))
        self.lstRoms.setObjectName("lstRoms")
        self.grpRadioBtns = QtWidgets.QGroupBox(self.tabRoms)
        self.grpRadioBtns.setGeometry(QtCore.QRect(380, 10, 121, 731))
        self.grpRadioBtns.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.grpRadioBtns.setObjectName("grpRadioBtns")
        self.lstFilteredRoms = QtWidgets.QListWidget(self.tabRoms)
        self.lstFilteredRoms.setGeometry(QtCore.QRect(680, 50, 381, 691))
        self.lstFilteredRoms.setObjectName("lstFilteredRoms")
        self.tcTabs.addTab(self.tabRoms, "")
        self.tabMedia = QtWidgets.QWidget()
        self.tabMedia.setObjectName("tabMedia")
        self.lblImage = QtWidgets.QLabel(self.tabMedia)
        self.lblImage.setGeometry(QtCore.QRect(420, 10, 640, 480))
        self.lblImage.setObjectName("lblImage")
        self.btnLoadMedia = QtWidgets.QPushButton(self.tabMedia)
        self.btnLoadMedia.setGeometry(QtCore.QRect(10, 10, 151, 61))
        self.btnLoadMedia.setObjectName("btnLoadMedia")
        self.mediaContainer = QtWidgets.QWidget(self.tabMedia)
        self.mediaContainer.setGeometry(QtCore.QRect(70, 450, 261, 221))
        self.mediaContainer.setObjectName("mediaContainer")
        self.lvMedia = QtWidgets.QListWidget(self.tabMedia)
        self.lvMedia.setGeometry(QtCore.QRect(10, 80, 256, 501))
        self.lvMedia.setObjectName("lvMedia")
        self.tcTabs.addTab(self.tabMedia, "")
        self.btnTemp = QtWidgets.QPushButton(MainWindow)
        self.btnTemp.setGeometry(QtCore.QRect(20, 810, 91, 29))
        self.btnTemp.setObjectName("btnTemp")

        self.retranslateUi(MainWindow)
        self.tcTabs.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Archimedes ROM Management"))
        self.label_9.setText(_translate("MainWindow", "Description:"))
        self.btnGamelists.setText(_translate("MainWindow", "Load Gamelists"))
        self.btnAddGame.setText(_translate("MainWindow", "Add Game"))
        self.btnSaveChanges.setText(_translate("MainWindow", "Save Changes"))
        self.label_10.setText(_translate("MainWindow", "Name:"))
        self.label_2.setText(_translate("MainWindow", "Path:"))
        self.label_3.setText(_translate("MainWindow", "Rating:"))
        self.label_4.setText(_translate("MainWindow", "Release Date:"))
        self.label_5.setText(_translate("MainWindow", "Developer:"))
        self.label_6.setText(_translate("MainWindow", "Publisher:"))
        self.label_7.setText(_translate("MainWindow", "Genre:"))
        self.label_8.setText(_translate("MainWindow", "Players:"))
        self.btnDeleteGamelistEntry.setText(_translate("MainWindow", "Delete Entry"))
        self.tcTabs.setTabText(self.tcTabs.indexOf(self.tabGamelists), _translate("MainWindow", "Gamelists"))
        self.btnLoadRomDir.setText(_translate("MainWindow", "&Load Directory"))
        self.grpRadioBtns.setTitle(_translate("MainWindow", "Filters:"))
        self.tcTabs.setTabText(self.tcTabs.indexOf(self.tabRoms), _translate("MainWindow", "Rom Manager"))
        self.lblImage.setText(_translate("MainWindow", "lblImage"))
        self.btnLoadMedia.setText(_translate("MainWindow", "Load Game System\n"
" Media Folder"))
        self.tcTabs.setTabText(self.tcTabs.indexOf(self.tabMedia), _translate("MainWindow", "Media"))
        self.btnTemp.setText(_translate("MainWindow", "PushButton"))

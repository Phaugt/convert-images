from PyQt5 import uic
from easysettings import EasySettings
from PyQt5.QtWidgets import (QApplication, qApp, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog, QMainWindow,
                            QMessageBox, QStatusBar, QWidget, QMenuBar, QStatusBar, QAction, QRadioButton)
from PyQt5.QtCore import QFile , Qt
from PyQt5.QtGui import QImage, QIcon, QPixmap
import sys, os, PIL, glob
from os.path import expanduser
from pathlib import Path
from PIL import Image

try:
    from PyQt5.QtWinExtras import QtWin
    myappid = 'convert.images.python.program'
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)    
except ImportError:
    pass

def resource_path(relative_path):
    """used by pyinstaller to see the relative path"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

guifile = resource_path("./gui/main.ui")
logo = resource_path("./gui/logo.png")
userfold = expanduser("~")
config = EasySettings(userfold+"./imageconf.conf")
configGui = resource_path("./gui/config.ui")

try:
    saveLocation = config.get("saveLocation")
    saveAs = config.get("saveFormat")
    if saveLocation or saveAs == "":
        saveLocation = userfold+'\\pictures\\'
        config.set("saveLocation", str(saveLocation))
        config.set("saveFormat", 'webp')
        config.save()
except FileNotFoundError:
    pass

class GUI(QMainWindow):
    """main window used by the application"""
    def __init__(self):
        super(GUI, self).__init__()
        UIFile = QFile(guifile)
        UIFile.open(QFile.ReadOnly)
        uic.loadUi(UIFile, self)
        UIFile.close()
        self.c = Config()
        self.c.reloadSettings()

        self.setAcceptDrops(True)

        self.image.setAlignment(Qt.AlignCenter)
        self.image.setText('\n\n Drop Image Here \n\n')
        self.image.setStyleSheet('''
            QLabel{
                border: 4px dashed #aaa
            }
            ''')
        self.btnconvertImage.clicked.connect(self.convertImage)
        self.btnconvertImage.setStatusTip("Convert the image to specified format")
        self.btnselectImage.setStatusTip("Select image to convert")
        self.btnselectImage.clicked.connect(self.selectImageFile)
        self.btnopenFolder.setStatusTip("Open the output folder for the new images")
        self.btnopenFolder.clicked.connect(self.openSavedFolder)

        
        self.actSetting.setStatusTip('Edit application settings')
        self.actSetting.triggered.connect(self.showSettings)
        
        self.actExit.setStatusTip('Exit application')
        self.actExit.triggered.connect(qApp.quit)

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

    def informationMessage(self,message):
        """send message to messagebox"""
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setWindowTitle("Information")
        msgBox.setText(message)
        msgBox.exec()
        
    def showSettings(self):
        """call the settings widget"""
        self.c.show()

    def dragEnterEvent(self, event):
        """accept the drag to window if it contains an image"""
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()
 
    def dragMoveEvent(self, event):
        """accept the drag to window if it contains an image"""
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()
 
    def dropEvent(self, event):
        """accept image when dropped into window"""
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.set_image(file_path)
            self.folderLocation.setText(file_path)
 
            event.accept()
        else:
            event.ignore()
 
    def set_image(self, file_path):
        """set the image as pixmap in the label and scale it """
        pixmap = QPixmap(file_path)
        scaled = pixmap.scaled(631,420,Qt.KeepAspectRatio)
        self.image.setPixmap(scaled)

    def convertImage(self):
        """convert the image to specified format and location """
        saveAs = config.get("saveFormat")
        saveLocation = config.get("saveLocation")
        image = Image.open(self.folderLocation.text())
        fileName = Path(image.filename).stem
        if saveAs == 'ico':
            size = 256, 256
            destPath = saveLocation+fileName+"."+saveAs
            im = Image.open(self.folderLocation.text())
            im.thumbnail(size)
            im.save(destPath, 'jpeg')
        else:
            image.save(saveLocation+fileName+"."+saveAs, saveAs)
        
    def selectImageFile(self):
        """if user does not want to drag and drop file"""
        fileName = QFileDialog.getOpenFileName()
        if fileName:
            self.set_image(fileName[0])

    
    def openSavedFolder(self):
        """open the folder where the output is saved"""
        sfl = config.get("saveLocation")
        os.startfile(sfl)

class Config(QWidget):
    """Config window - called from menubar"""
    def __init__(self):
        super().__init__()
        UIFile = QFile(configGui)
        UIFile.open(QFile.ReadOnly)
        uic.loadUi(UIFile, self)
        UIFile.close()

        self.newFolderPath.setText(config.get("saveLocation"))
        self.saveExit.clicked.connect(self.saveExitConfig)
        self.saveExit.setStatusTip("Save and Exit")
        self.save.clicked.connect(self.saveConfig)
        self.save.setStatusTip("Save")
        self.changeOutputFolder.clicked.connect(self.changeSavedFolder)
        self.changeOutputFolder.setStatusTip("Change the save folder for the newly converted images")

        self.formatWebp.toggled.connect(self.pickSaveFormat)
        self.formatWebp.setStatusTip("Select .webp (saves alot of space)")
        self.formatIco.toggled.connect(self.pickSaveFormat)
        self.formatIco.setStatusTip("Convert the image to an .ico file with 256x256 px size!")
        self.formatJpeg.toggled.connect(self.pickSaveFormat)
        self.formatJpeg.setStatusTip("Select .jpeg")
        self.formatPng.toggled.connect(self.pickSaveFormat)
        self.formatPng.setStatusTip("Select .png")
    
    def reloadSettings(self):
        """reload settings"""
        try:
            saveLocation = config.get("saveLocation")
            saveAs = config.get("saveFormat")
            if saveAs == 'webp':
                self.formatWebp.setChecked(True)
            elif saveAs == 'jpeg':
                self.formatJpeg.setChecked(True)
            elif saveAs == 'png':
                self.formatPng.setChecked(True)
            elif saveAs == 'ico':
                self.formatIco.setChecked(True)
            else:
                pass
        except FileNotFoundError:
            pass

    def saveConfig(self):
        """save the current settings to config"""
        newPath = self.newFolderPath.text()
        config.set("saveLocation", str(newPath))
        config.save()
        self.reloadSettings()

    def pickSaveFormat(self):
        """save choice from radio button into config"""
        try:
            if self.formatWebp.isChecked():
                config.set("saveFormat",'webp')
                config.save()
            elif self.formatPng.isChecked():
                config.set("saveFormat",'png')
                config.save()
            elif self.formatJpeg.isChecked():
                config.set("saveFormat",'jpeg')
                config.save()
            elif self.formatIco.isChecked():
                config.set("saveFormat",'ico')
                config.save()
            else:
                pass
        except Exception:
            pass


    def saveExitConfig(self):
        """save the current settings to config and exit"""
        newPath = self.newFolderPath.text()
        config.set("saveLocation", str(newPath))
        config.save()
        self.reloadSettings()
        self.close()

    def changeSavedFolder(self):
        """change the folder for the output"""
        sfl = QFileDialog()
        sfl.setFileMode(QFileDialog.Directory)
        foldName = sfl.getExistingDirectory()
        fixfoldName = foldName + "/"
        if fixfoldName:
            self.newFolderPath.setText(fixfoldName)

app = QApplication(sys.argv)
app.setWindowIcon(QIcon(logo))
window = GUI()
window.show()
app.exec_()

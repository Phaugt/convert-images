from PyQt5 import uic
from easysettings import EasySettings
from PyQt5.QtWidgets import (QApplication, qApp, QPushButton, QLabel, QVBoxLayout,QHBoxLayout, QFileDialog, QMainWindow,
                            QMessageBox, QStatusBar)
from PyQt5.QtCore import QFile , Qt
from PyQt5.QtGui import QImage, QIcon, QPixmap
import sys, os, PIL, glob
from os.path import expanduser
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

class GUI(QMainWindow):
    def __init__(self):
        super(GUI, self).__init__()
        UIFile = QFile(guifile)
        UIFile.open(QFile.ReadOnly)
        uic.loadUi(UIFile, self)
        UIFile.close()
        
        self.setAcceptDrops(True)

        self.image.setAlignment(Qt.AlignCenter)
        self.image.setText('\n\n Drop Image Here \n\n')
        self.image.setStyleSheet('''
            QLabel{
                border: 4px dashed #aaa
            }
            ''')
        self.btnconvertImage.clicked.connect(self.convertImage)

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()
 
    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()
 
    def dropEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.set_image(file_path)
            self.folderLocation.setText(file_path)
 
            event.accept()
        else:
            event.ignore()
 
    def set_image(self, file_path):
        pixmap = QPixmap(file_path)
        scaled = pixmap.scaled(631,420,Qt.KeepAspectRatio)
        self.image.setPixmap(scaled)

    def convertImage(self):
        try:
            saveLocation = config.get("saveLocation")
            if saveLocation == "":
                saveLocation = userfold+'/pictures/'
                config.set("saveLocation", str(saveLocation))
                config.save()
            else:
                saveLocation = config.get("saveLocation")
        except FileNotFoundError:
            pass
        image = Image.open(self.folderLocation.text())
        #image = image.convert('RBG')
        image.save(saveLocation+'.webp', 'webp')





app = QApplication(sys.argv)
app.setWindowIcon(QIcon(logo))
window = GUI()
window.show()
app.exec_()

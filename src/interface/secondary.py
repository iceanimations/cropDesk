'''
Created on Aug 31, 2013
@author: qurban.ali
'''
import site
site.addsitedir(r"R:\Python_Scripts")
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic
import os
import os.path as osp
import logic.cdLogic as logic
import sys
import time
modulePath = sys.modules[__name__].__file__
root = osp.dirname(osp.dirname(osp.dirname(modulePath)))
home = osp.expanduser('~')
cdDirectory = osp.join(home, '.cropDesk')
settingsFile = osp.join(cdDirectory, 'settings.txt')

class Label(QLabel):
    def __init__(self, parent = None, pixmap = None, data = {}):
        super(Label, self).__init__(parent)
        self.rect = QRect()
        self.parentWin = parent
        self.pix = pixmap
        self.darkenBackground = False
        if data:
            if data.has_key('darkenBackground'):
                if data['darkenBackground'] == 'True':
                    self.darkenBackground = True
        self.mouseDown = False
        cursor = QCursor()
        cursor.setShape(Qt.CrossCursor)
        self.setCursor(cursor)
        if self.darkenBackground:
            self.resultImage = QPixmap(pixmap.size())
            self.resultImage.fill(QColor(255, 255, 255, alpha = 100))
            self.sourceImage = QPixmap(pixmap.size())
            self.sourceImage.fill(QColor(255, 255, 255, alpha = 100))
            self.setPixmap(self.sourceImage)
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.rubberBand.paintEvent = self.rbPaintEvent
            
    def rbPaintEvent(self, event):
        painter = QPainter(self.rubberBand)
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        #painter.setBrush(QBrush(Qt.NoBrush))
        rect = self.rubberBand.rect()
        rect.setTopLeft(QPoint(rect.x() + 1, rect.y() + 1))
        rect.setBottomRight(QPoint(rect.width() - 1, rect.height() - 1))
        painter.drawRect(QRect(rect.normalized()))
    
    def mousePressEvent(self, event):
        self.rect.setTopLeft(event.pos())
        self.rect.setBottomRight(event.pos())
        if event.button() == Qt.LeftButton:
            self.mouseDown = True
            self.rect.setTopLeft(event.pos())
        if self.darkenBackground:
            self.setPixmap(self.sourceImage)
        self.rubberBand.setGeometry(self.rect)
        self.rubberBand.show()

    def mouseReleaseEvent(self, event):
        self.parentWin.showContextMenu(event)
        if event.button() == Qt.LeftButton:
            self.mouseDown = False
            self.rect.setBottomRight(event.pos())
            width = self.rect.width()
            height = self.rect.height()
            if width > 5 and height > 5:
                self.parentWin.showDoneMenu(self.rect)
        
    def mouseMoveEvent(self, event):
        if self.mouseDown:
            self.rect.setBottomRight(event.pos())
            if self.darkenBackground:
                self.drawImages()
                self.repaint()
            self.rubberBand.setGeometry(self.rect)
            
    def drawImages(self):
        painter = QPainter(self.resultImage)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(self.resultImage.rect(), Qt.transparent)
        self.destinationImage = QPixmap(self.rect.size())
        self.destinationImage.fill(QColor(255, 255, 255, alpha = 255))
        painter.drawPixmap(self.rect.topLeft() ,self.destinationImage)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOut)
        painter.drawPixmap(0, 0, self.sourceImage)
        self.setPixmap(self.resultImage)
        
        
            
class Menu(QMenu):
    def __init__(self, parentWin = None, tray = False):
        super(Menu, self).__init__(parentWin)
        self.parentWin = parentWin
        acts = []
        if tray:
            acts.append('Capture')
        acts.append('Help')
        acts.append('Preferences')
        self.setObjectName('contextMenu')
        self.createActions(acts)
        self.addSeparator()
        if not tray:
            self.createActions(['Cancel'])
        if tray:
            self.createActions(['Exit'])
        map(lambda action: action.triggered.connect
            (lambda: self.handleActions(action)), self.actions())
        
    def createActions(self, names):
        for name in names:
            action = QAction(name, self)
            self.addAction(action)
    
    def handleActions(self, action):
        text = str(action.text())
        if text == 'Capture':
            self.parentWin.label.hide()
            self.parentWin.label.deleteLater()
            self.parentWin.captureDesk()
            self.parentWin.showMaximized()
        if text == 'Preferences':
            self.parentWin.preferencesWindow.exec_()
        if text == 'Cancel':
            self.parentWin.hide()
        if text == 'Exit':
            self.parentWin.close()
            self.close()
        if text == 'Help':
            flag = False
            if self.parentWin.isHidden():
                self.parentWin.showMaximized()
                flag = True
            msgBox(self.parentWin, msg= helpMsg,
                   icon = QMessageBox.Information, title = 'Help')
            if flag:
                self.parentWin.hide()

Form, Base = uic.loadUiType(r"%s\ui\settings.ui"%root)
class Preferences(Form, Base):
    def __init__(self, parent = None):
        super(Preferences, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('Preferences')
        self.parentWin = parent
        self.saveButton.clicked.connect(self.save)
        self.cancelButton.clicked.connect(self.hide)
        self.browseButton.clicked.connect(lambda: folderDialog(self))
        
    def showEvent(self, event):
        self.loadPreferences()
    
    def closeEvent(self, event):
        self.hide()
        event.ignore()     
    
    def loadPreferences(self):
        settings = {}
        fd = open(osp.join(settingsFile))
        value = fd.read()
        if value:
            settings.update(eval(value))
            if settings.has_key('prefix'):
                self.prefixBox.setText(settings['prefix'])
            if settings.has_key('path'):
                self.pathBox.setText(settings['path'])
            if settings.has_key('closeWhenCropped'):
                if settings['closeWhenCropped'] == 'True':
                    self.closeWhenCroppedButton.setChecked(True)
            if settings.has_key('darkenBackground'):
                if settings['darkenBackground'] == 'True':
                    self.darkenButton.setChecked(True)
            if settings.has_key('imageQuality'):
                self.imageQualityBox.setValue(settings['imageQuality'])
        fd.close()
        
    def save(self):
        path = str(self.pathBox.text())
        prefix = str(self.prefixBox.text())
        if not path:
            msgBox(self, msg = 'Path not specified', icon = QMessageBox.Warning)
            return
        if not prefix:
            msgBox(self, msg = 'Prefix not specified',
                   icon = QMessageBox.Warning)
            return
        if not osp.exists(path):
            msgBox(self, 'The system can not find the path specified',
                   icon = QMessageBox.Warning)
            return
        #save the settings
        closeWhenCropped = 'False'
        darken = 'False'
        if self.closeWhenCroppedButton.isChecked():
            closeWhenCropped = 'True'
        if self.darkenButton.isChecked():
            darken = 'True'
        fd = open(settingsFile, 'w')
        settings = {'prefix': prefix, 'path': path,
                    'closeWhenCropped': closeWhenCropped,
                    'darkenBackground': darken,
                    'imageQuality': self.imageQualityBox.value()}
        fd.write(str(settings))
        fd.close()
        self.hide()
        self.parentWin.setData()
        self.parentWin.switchView()
        
def msgBoxCloseEvent(*args):
    print 'hello'
    
            
def msgBox(parent, msg = None, btns = QMessageBox.Ok,
           icon = None, ques = None, details = None, title = 'cropDesk'):
    '''
    dispalys the warnings
    @params:
            args: a dictionary containing the following sequence of variables
            {'msg': 'msg to be displayed'[, 'ques': 'question to be asked'],
            'btns': QMessageBox.btn1 | QMessageBox.btn2 | ....}
    '''
    if msg:
        mBox = QMessageBox(parent)
        mBox.closeEvent = msgBoxCloseEvent
        mBox.setWindowModality(Qt.ApplicationModal)
        mBox.setWindowTitle(title)
        mBox.setText(msg)
        if ques:
            mBox.setInformativeText(ques)
        if icon:
            mBox.setIcon(icon)
        if details:
            mBox.setDetailedText(details)
        mBox.setStandardButtons(btns)
        buttonPressed = mBox.exec_()
        return buttonPressed
        
def folderDialog(parent):
    '''shows the file dialog listing directories only'''
    path = QFileDialog.getExistingDirectory(parent, 'Directory', '',
                                            QFileDialog.ShowDirsOnly)
    parent.pathBox.setText(path)
    
class Thread(QThread):
    def __init__(self, parent = None):
        super(Thread, self).__init__(parent)
        self.parent = parent
        self.testButton = QPushButton(self.parent)
        self.testButton.hide()
        self.testButton.released.connect(self.parent.monitorFile)
    
    def run(self):
        while(True):
            self.testButton.released.emit()
            time.sleep(2)
    
helpMsg = ('- Cropping: Press left mouse button and drag it '+
            'through the area which you want to crop.\n\n'+
            '- Cancel cropping: Press Esc key on your keyboard.\n\n'+
            '- Preferences: Preferences window lets you manage:\na) Where to'+ 
            ' save the cropped images.\nb) What name should be given to the '+ 
            'cropped image (cropDesk will append 1,2,3... at the end of each '+
            'image name if you save multiple images in the same directory with'+
            ' same name.)\nc) "Close window when cropped" option closes the the'
            +' cropping window when you are done with the first crop.\n'+
            'd) Whiten background: this option makes the background transparent'+
            ' white, so the cropped area looks separate from the area other'+
            ' than cropped area.\ne) Image Quality: This option lets you handle'+
             ' the quality of cropped image between 1 to 100'+
            '\n\n- The path to the latest cropped image is always copied to the'+ 
            ' clipboard, you can paste it whereever you want after cropping the'
             +' image.')
    
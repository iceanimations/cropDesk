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
modulePath = sys.modules[__name__].__file__
root = osp.dirname(osp.dirname(osp.dirname(modulePath)))
home = osp.expanduser('~')
cdDirectory = osp.join(home, '.cropDesk')
settingsFile = osp.join(cdDirectory, 'settings.txt')

class Label(QLabel):
    def __init__(self, parent = None, pixmap = None):
        super(Label, self).__init__(parent)
        self.rect = QRect()
        self.parentWin = parent
        self.mouseDown = False
        cursor = QCursor()
        cursor.setShape(Qt.CrossCursor)
        self.setCursor(cursor)
        self.resultImage = QPixmap(pixmap.size())
        self.resultImage.fill(QColor(0, 0, 0, alpha = 130))
        self.sourceImage = QPixmap(pixmap.size())
        self.sourceImage.fill(QColor(0, 0, 0, alpha = 130))
        self.setPixmap(self.resultImage)
        
    
    def mousePressEvent(self, event):
        self.rect.setSize(QSize(0,0))
        if event.button() == Qt.LeftButton:
            self.mouseDown = True
            self.rect.setTopLeft(event.pos())
        self.setPixmap(self.sourceImage)

    def mouseReleaseEvent(self, event):
        self.parentWin.showContextMenu(event)
        if event.button() == Qt.LeftButton:
            self.mouseDown = False
            width = self.rect.width()
            height = self.rect.height()
            if width > 5 and height > 5:
                self.parentWin.showDoneMenu(self.rect)
        
    def mouseMoveEvent(self, event):
        if self.mouseDown:
            self.rect.setBottomRight(event.pos())
            self.drawImages()
            self.repaint()
            
    def drawImages(self):
        painter = QPainter(self.resultImage)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(self.resultImage.rect(), Qt.transparent)
        self.destinationImage = QPixmap(self.rect.size())
        self.destinationImage.fill(QColor(0, 0, 0, alpha = 130))
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.drawPixmap(self.rect.topLeft() ,self.destinationImage)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOut)
        painter.drawPixmap(0, 0, self.sourceImage)
        painter.end()
        self.setPixmap(self.resultImage)
        
        
            
class Menu(QMenu):
    def __init__(self, parentWin = None):
        super(Menu, self).__init__(parentWin)
        self.parentWin = parentWin
        acts = ['Help', 'Preferences']
        self.setObjectName('contextMenu')
        self.createActions(acts)
        self.addSeparator()
        self.createActions(['Cancel'])
        map(lambda action: action.triggered.connect
            (lambda: self.handleActions(action)), self.actions())
        shortcut = QShortcut(QKeySequence(self.tr('Ctrl+Alt+c',
                                                  'contextMenu|Capture')), self)
        
    def createActions(self, names):
        for name in names:
            action = QAction(name, self)
            self.addAction(action)
    
    def handleActions(self, action):
        text = str(action.text())
        if text == 'Capture':
            self.parentWin.captureDesk()
            self.parentWin.showMaximized()
        if text == 'Preferences':
            self.parentWin.showPreferences()
        if text == 'Cancel':
            self.parentWin.close()
        if text == 'Help':
            msgBox(self.parentWin, msg= helpMsg,
                   icon = QMessageBox.Information, title = 'Help')
            

Form, Base = uic.loadUiType(r"%s\ui\settings.ui"%root)
class Preferences(Form, Base):
    def __init__(self, parent = None):
        super(Preferences, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('Preferences')
        self.parentWin = parent
        self.saveButton.clicked.connect(self.save)
        self.cancelButton.clicked.connect(self.close)
        self.browseButton.clicked.connect(lambda: folderDialog(self))
        self.setStyle(QStyleFactory.create('plastique'))
        
    def showEvent(self, event):
        self.loadPreferences()       
    
    def loadPreferences(self):
        settings = {}
        fd = open(osp.join(cdDirectory, 'settings.txt'))
        value = fd.read()
        if value:
            settings.update(eval(value))
            self.prefixBox.setText(settings['prefix'])
            self.pathBox.setText(settings['path'])
            if settings['closeWhenCropped'] == 'True':
                self.closeWhenCroppedButton.setChecked(True)
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
        if self.closeWhenCroppedButton.isChecked():
            closeWhenCropped = 'True'
        fd = open(settingsFile, 'w')
        settings = {'prefix': prefix, 'path': path,
                    'closeWhenCropped': closeWhenCropped}
        fd.write(str(settings))
        fd.close()
        self.close()
            
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
    
helpMsg = ('- Cropping: Press left mouse button and drag it '+
            'through the area which you want to crop.\n'+
            '- Cancel cropping: Press Esc key on your keyboard.\n'+
            '- Preferences: Preferences window lets you manage:\na) Where to'+ 
            ' save the cropped images.\nb) What name should be given to the '+ 
            'cropped image (cropDesk will append 1,2,3... at the end of each '+
            'image name if you save multiple images in the same directory with'+
            ' same name.)\nc) "Close window when cropped" option closes the the'
            +' cropping window when you are done with the first crop.'+
            '\n- The path to the latest cropped image is always copied to the'+ 
            ' clipboard, you can paste it whereever you want after cropping the'
             +' image.')
    
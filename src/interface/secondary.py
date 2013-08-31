'''
Created on Aug 31, 2013

@author: qurban.ali
'''
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
cdDirectory = osp.join(home, 'cropDesk')
os.mkdir(cdDirectory)
settingsFile = osp.join(cdDirectory, 'settings.txt')
fd = open(settingsFile, 'w')
fd.close()

class Label(QLabel):
    def __init__(self, parentWin = None):
        super(Label, self).__init__(parentWin)
        self.mousePos = QPoint()
        self.mouseDown = False
        self.rect = QRect()
        self.pix = QPixmap.grabWindow(QApplication.desktop().winId())
        image = osp.join(cdDirectory, 'image.png')
        self.pix.save(image, None, 100)
        self.setStyleSheet("background-image: url("+ image +")")
        cursor = QCursor()
        cursor.setShape(Qt.CrossCursor)
        self.setCursor(cursor)
        
    def mousePressEvent(self, event):
        self.mouseDown = True
        self.mousePos = event.pos()
        self.rect.setTopLeft(self.mousePos)
    
    def mouseReleaseEvent(self, event):
        self.rect.setBottomRight(event.pos())
        self.repaint()
        self.saveCropped()
        
    def saveCropped(self, path):
        self.pix.copy(self.rect).save(path, None, 100)
        
    def mouseMoveEvent(self, event):
        if self.mouseDown:
            self.rect.setBottomRight(event.pos())
            self.repaint()
        
    def paintEvent(self, event):
        if self.rect.x() > 0:
            painter = QPainter(self)    
            painter.setPen(QPen(Qt.black, 1, Qt.DashLine));
            painter.drawRect(self.rect);
            
class Menu(QMenu):
    def __init__(self, parentWin = None):
        super(Menu, self).__init__(parentWin)
        self.parentWin = parentWin
        acts = ['Capture', 'Settings']
        self.createActions()
        self.addSeparator()
        self.createActions(['Exit'])
        map(lambda action: action.triggered.connect
            (lambda: self.handleActions(action)), self.actions())
        
    def createActions(self, names):
        for name in names:
            action = QAction(name)
    
    def handleActions(self, action):
        text = str(action.text())
        if text == 'Capture':
            self.parentWin.showMaximized()
        if text == 'Settings':
            win = Settings(self.parentWin)
            win.showMaximized()
            

Form, Base = uic.loadUiType(r"%s\ui\settings.ui"%root)
class Settings(Form, Base):
    def __init__(self, parent = None):
        super(Settings, self).__init__(parent)
        self.setupUi(self)
        self.parentWin = parent
        self.saveButton.clicked.connect(self.save)
        self.cancelButton.clicked.connect(self.close)
        self.loadSettings()
            
    def loadSettings(self):
        settings = {}
        fd = open(osp.join(cdDirectory, 'settings.txt'))
        value = fd.read()
        if value:
            settings.update(eval(value))
            self.prefixBox.setText(settings['prefix'])
            self.pathBox.setText(settings['path'])
        fd.close()
        
    def save(self):
        path = str(self.pathBox.text())
        prefix = str(self.prefixBox.text())
        if not path:
            msgBox(self, msg = 'Path not specified')
            return
        if not prefix:
            msgBox(self, msg = 'Prefix not specified')
            return
        if not osp.exists(path):
            msgBox(self, 'The system can not find the path specified')
            return
        #save the settings
        fd.open(settingsFile, 'w')
        settings = {'prefix': prefix, 'path': path}
        fd.write(str(settings))
        fd.close()
        
            
def msgBox(parent, msg = None, btns = QMessageBox.Ok,
           icon = None, ques = None, details = None):
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
        mBox.setWindowTitle('Shader Transfer')
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
        
            
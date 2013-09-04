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
    def __init__(self, parent = None):
        super(Label, self).__init__(parent)
        self.rect = QRect()
        self.parentWin = parent
        self.mousePos = QPoint()
        self.mouseDown = False
        cursor = QCursor()
        cursor.setShape(Qt.CrossCursor)
        self.setCursor(cursor)
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        
    def mousePressEvent(self, event):
        self.rubberBand.setGeometry(QRect(0,0,0,0))
        if event.button() == Qt.LeftButton:
            self.mouseDown = True
            self.rect.setTopLeft(event.pos())
            self.rubberBand.show()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouseDown = False
            width = self.rubberBand.size().width()
            height = self.rubberBand.size().height()
            if width > 5 and height > 5:
                self.parentWin.showDoneMenu(QRect(self.rubberBand.pos(),
                                                        self.rubberBand.size()))
        
    def mouseMoveEvent(self, event):
        if self.mouseDown:
            self.rect.setBottomRight(event.pos())
            self.rubberBand.setGeometry(self.rect.normalized())
            
class Menu(QMenu):
    def __init__(self, parentWin = None):
        super(Menu, self).__init__(parentWin)
        self.parentWin = parentWin
        acts = ['Capture', 'Preferences']
        self.setObjectName('contextMenu')
        self.createActions(acts)
        self.addSeparator()
        self.createActions(['Exit'])
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
            self.parentWin.preferencesWindow.exec_()
        if text == 'Exit':
            self.parentWin.close()
            

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
        
    def showEvent(self, event):
        self.loadPreferences()
            
#    def keyPressEvent(self, event):
#        if event.key() == Qt.Key_Escape:
#            self.hide()
#            
#    def closeEvent(self, event):
#        self.hide()
#        event.ignore()
#        
#    def changeEvent(self, event):
#        if self.isMinimized():
#            self.show()
#            self.hide()        
    
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
        
def folderDialog(parent):
    '''shows the file dialog listing directories only'''
    path = QFileDialog.getExistingDirectory(parent, 'Directory', '',
                                            QFileDialog.ShowDirsOnly)
    parent.pathBox.setText(path)
    
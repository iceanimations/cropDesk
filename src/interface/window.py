'''
Created on Aug 31, 2013

@author: qurban.ali
'''
import site
site.addsitedir(r"R:\Python_Scripts")
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt
import secondary as secui
import sys
import os
import os.path as osp
modulePath = sys.modules[__name__].__file__
root = osp.dirname(osp.dirname(osp.dirname(modulePath)))
home = osp.expanduser('~')
cdDirectory = osp.join(home, '.cropDesk')
try:
    os.mkdir(cdDirectory)
except WindowsError:
    pass
settingsFile = osp.join(cdDirectory, 'settings.txt')
try:
    if not osp.exists(settingsFile):
        fd = open(settingsFile, 'w+')
        fd.close()
except WindowsError:
    pass

class Window(QWidget):
    def __init__(self, parent = None):
        super(Window, self).__init__(parent)
        self.icon = QIcon(r"%s\icons\cd.png"%root)
        self.setWindowTitle('cropDesk')
        self.setWindowIcon(self.icon)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.setTrayIcon()
        self.doneMenu = None
        self.captureDesk()
        self.setWindowModality(Qt.WindowModal)
        # make the window full sized
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def captureDesk(self):
        self.pixmap = QPixmap.grabWindow(QApplication.desktop().winId())
        self.label = secui.Label(self, self.pixmap)
        self.layout.addWidget(self.label)
        self.pixmap.save('D:/tempImage.png', None, 100)
        self.label.setStyleSheet("background-image: url(D:/tempImage.png)")
        #self.label.setPixmap(self.pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            
    def showContextMenu(self, event):
        if event.button() == Qt.RightButton:
            menu = secui.Menu(self)
            menu.popup(QCursor.pos())

    def setTrayIcon(self):
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setToolTip("cropDesk")
        self.trayIcon.setIcon(self.icon)
        self.trayIcon.show()
        self.trayIcon.setContextMenu(secui.Menu(self))

    def showDoneMenu(self, rect):
        self.rect = rect
        self.doneMenu = QMenu(self)
        self.doneMenu.addAction('Crop')
        self.doneMenu.actions()[0].triggered.connect(self.saveCropped)
        self.doneMenu.popup(QCursor.pos())

    def saveCropped(self):
        fd = open(settingsFile)
        data = fd.read()
        if not data:
            self.showPreferences()
            fd.seek(0)
            data = fd.read()
            if not data: return
        data = eval(data)
        path = data['path']
        prefix = data['prefix']
        if not osp.exists(path) or not prefix:
            btn = secui.msgBox(self,
                         msg = 'No valid Settings found in preferences\n'+path,
                         btns = QMessageBox.Yes | QMessageBox.No,
                         ques = 'Do you want to change the Preferences?',
                         icon = QMessageBox.Information)
            if btn == QMessageBox.Yes:
                self.showPreferences()
                fd.seek(0)
                data = fd.read()
                fd.close()
                if not data:
                    return
                data = eval(data)
            else: return
        path = data['path']
        prefix = data['prefix']
        fname = self.fileName(path, prefix)
        path = osp.join(path, fname)
        if self.pixmap.height() > self.height(): # due to some display bug
            self.rect.setY(self.rect.y() + 28)
            self.rect.setHeight(self.rect.height() + 28)
        path = osp.normpath(path)
        path = osp.splitext(path)[0] + '.png'
        self.pixmap.copy(self.rect).save(path, None, 100)
        path2 = osp.splitext(path)[0] +'.jpeg'
        os.rename(path, path2)
        if data['closeWhenCropped'] == 'True':
            self.close()
        clipBoard = QApplication.clipboard()
        clipBoard.setText(path2)
        try: os.remove('D:/tempImage.png')
        except: pass

    def fileName(self, path, name):
        count = 1
        name += str(count) + '.jpeg'
        while(True):
            if osp.exists(osp.join(path, name)):
                count += 1
                name = name.replace(str(count - 1), str(count))
            else:
                return name

    def showPreferences(self):
        self.preferencesWindow = secui.Preferences(self)
        self.preferencesWindow.exec_()
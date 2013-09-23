'''
Created on Aug 31, 2013

@author: qurban.ali
'''
import site
site.addsitedir(r"R:\Python_Scripts")
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt
site.addsitedir(r"R:\Pipe_Repo\Users\Hussain\packages")
from pgmagick.api import Image
import secondary as secui
import sys
import os
import time
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
runningFile = osp.join(cdDirectory, 'running.txt')

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
        self.data = None # data from settings file
        self.preferencesWindow = secui.Preferences(self)
        self.setData()
        self.captureDesk()
        self.setWindowModality(Qt.ApplicationModal)
        self.runningFileCreated = False
        self.thread = secui.Thread(self)
        self.thread.start()
        # make the window full sized
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
    def switchView(self):
        try:
            self.label.deleteLater()
            self.captureDesk(self.pixmap)
        except: pass
        
    def monitorFile(self):
        if self.runningFileCreated:
            if not osp.exists(runningFile):
                self.close()
        
    def setData(self):
        '''
        reads the settings file and fetches the data from it
        '''
        fd = open(settingsFile)
        self.data = fd.read()
        if not self.data:
            self.preferencesWindow.exec_()
            time.sleep(1)
            fd.seek(0)
            self.data = fd.read()
            if not self.data: return
        self.data = eval(self.data)
        path = self.data['path']
        prefix = self.data['prefix']
        if not osp.exists(path) or not prefix:
            btn = secui.msgBox(self,
                         msg = 'No valid Settings found in preferences\n'+path,
                         btns = QMessageBox.Yes | QMessageBox.No,
                         ques = 'Do you want to change the Preferences?',
                         icon = QMessageBox.Information)
            if btn == QMessageBox.Yes:
                self.preferencesWindow.exec_()
                time.sleep(1)
                fd.seek(0)
                self.data = fd.read()
                fd.close()
                if not self.data:
                    return
                self.data = eval(self.data)
            else: return
        

    def captureDesk(self, pix = None):
        if not pix:
            self.pixmap = QPixmap.grabWindow(QApplication.desktop().winId())
        else: self.pixmap = pix
        self.label = secui.Label(self, self.pixmap, self.data)
        self.layout.addWidget(self.label)
        self.pixmap.save('D:/tempImage.png', None, 100)
        self.label.setStyleSheet("background-image: url(D:/tempImage.png)")
        
        # update the database, how many times this app is used
        site.addsitedir(r'r:/pipe_repo/users/qurban')
        import appUsageApp
        appUsageApp.updateDatabase('cropDesk')
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()
            
    def hideEvent(self, event):
        fd = open(osp.join(runningFile), 'w')
        fd.close()
        self.runningFileCreated = True
        
    def closeEvent(self, event):
        try: os.remove(runningFile)
        except: pass
            
    def showContextMenu(self, event):
        if event.button() == Qt.RightButton:
            menu = secui.Menu(self)
            menu.popup(QCursor.pos())

    def setTrayIcon(self):
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setToolTip("cropDesk")
        self.trayIcon.setIcon(self.icon)
        self.trayIcon.show()
        self.trayIcon.setContextMenu(secui.Menu(self, tray = True))

    def showDoneMenu(self, rect):
        self.rect = rect
        self.doneMenu = QMenu(self)
        self.doneMenu.addAction('Crop')
        self.doneMenu.actions()[0].triggered.connect(self.saveCropped)
        self.doneMenu.popup(QCursor.pos())

    def saveCropped(self):
        if not self.data:
            self.setData()
            if not self.data:
                return
        path = self.data['path']
        prefix = self.data['prefix']
        imageQuality = self.data['imageQuality']
        fname = self.fileName(path, prefix)
        path = osp.join(path, fname)
        if self.pixmap.height() > self.height(): # due to some display bug
            self.rect.setY(self.rect.y() + 28)
            self.rect.setHeight(self.rect.height() + 28)
        path = osp.normpath(path)
        path2 = osp.splitext(path)[0] + '.jpg'
        self.pixmap.copy(self.rect).save(path, None, imageQuality)
        im = Image(path)
        im.write(path2)
        os.remove(path)
        if self.data['closeWhenCropped'] == 'True':
            self.hide()
        clipBoard = QApplication.clipboard()
        clipBoard.setText(path2)
        try: os.remove('D:/tempImage.png')
        except: pass

    def fileName(self, path, name):
        count = 1
        name += str(count) + '.jpg'
        while(True):
            print osp.join(path, name)
            if osp.exists(osp.join(path, name)):
                count += 1
                name = name.replace(str(count - 1), str(count))
            else:
                return osp.splitext(name)[0] +'.png'
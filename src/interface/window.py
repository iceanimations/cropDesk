'''
Created on Aug 31, 2013

@author: qurban.ali
'''
import site
site.addsitedir(r"R:\Python_Scripts")
from PyQt4.QtGui import *
import secondary as secui
import sys
import os.path as osp
modulePath = sys.modules[__name__].__file__
root = osp.dirname(osp.dirname(osp.dirname(modulePath)))

class Window(QWidget):
    def __init__(self, parent = None):
        super(Window, self).__init__(parent)
        self.icon = QIcon(r"%s\icons\cd.png"%root)
        self.setWindowIcon(self.icon)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.label = secui.Label(self)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setTrayIcon()
        
    def setTrayIcon(self):
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setToolTip("cropDesk")
        self.trayIcon.setIcon(self.icon)
        self.trayIcon.show()
        self.trayIcon.setContextMenu(secui.Menu(self))
        
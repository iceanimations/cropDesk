'''
Created on Aug 31, 2013

@author: qurban.ali
'''
import site
site.addsitedir(r'R:\Python_Scripts')
from PyQt4.QtGui import QApplication, QStyleFactory
import sys
import interface.window as win
import os.path as osp
import os
home = osp.expanduser('~')
cdDirectory = osp.join(home, '.cropDesk')
runningFile = osp.join(cdDirectory, 'running.txt')


if __name__ == '__main__':
    if osp.exists(runningFile):
        os.remove(runningFile)
    app = QApplication(sys.argv)
    #app.setStyle(QStyleFactory.create('plastique'))
    w = win.Window()
    w.showMaximized()
    sys.exit(app.exec_())
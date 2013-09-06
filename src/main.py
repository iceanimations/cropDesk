'''
Created on Aug 31, 2013

@author: qurban.ali
'''
import site
site.addsitedir(r'R:\Python_Scripts')
from PyQt4.QtGui import QApplication, QStyleFactory
import sys
import interface.window as win


if __name__ == '__main__':
    app = QApplication(sys.argv)
    #app.setStyle(QStyleFactory.create('plastique'))
    w = win.Window()
    w.showMaximized()
    sys.exit(app.exec_())
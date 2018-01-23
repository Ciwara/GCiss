#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fadiga

import os
import sys

sys.path.append(os.path.abspath('../'))

from PyQt4.QtGui import QApplication

from Common.ui.window import FWindow
from Common.cmain import cmain
from Common.ui.qss import theme

from ui.mainwindow import MainWindow

app = QApplication(sys.argv)


def main():

    window = MainWindow()
    window.setStyleSheet(theme)
    setattr(FWindow, 'window', window)
    # window.show()
    window.showMaximized()
    sys.exit(app.exec_())

if __name__ == '__main__':
    if cmain():
        # from migrations import init
        # init()
        main()

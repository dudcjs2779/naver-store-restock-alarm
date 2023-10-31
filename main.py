from scripts import soldout_ui, database

from PyQt5.QtWidgets import QApplication
from PyQt5 import uic
import sys
import os


if __name__ == "__main__":
    database.create_table()
    app = QApplication(sys.argv)
    mainWindow = soldout_ui.MainClass()
    mainWindow.show()
    app.exec_()
    
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import sys
import time
import random
import json
import os
from . import crawling, database, bot

main_form = uic.loadUiType(r'ui\soldout_check.ui')[0]
insert_url_form = uic.loadUiType(r'ui\input_url.ui')[0]
alarm_setting_form = uic.loadUiType(r'ui\alarm_setting.ui')[0]
crawling_class = crawling.CrawlingClass()
config = "dict()"

class MainClass(QMainWindow, main_form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        print(config)
        

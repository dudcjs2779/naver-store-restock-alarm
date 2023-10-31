from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import time
import random
import json
import os
import schedule
from . import crawling, database, bot


def get_config() -> dict:
    if os.path.exists("config.json"):
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
    else:
        config = {
            "is_background": False,
            "slack_url": "",
            "alarm_count": 2,
            "start_times": ["09:00", "15:00"],
        }
    
        with open("config.json", "w") as config_file:
            json.dump(config, config_file)
            
    return config

config = get_config()


main_form = uic.loadUiType(r'ui\soldout_check.ui')[0]
insert_url_form = uic.loadUiType(r'ui\input_url.ui')[0]
alarm_setting_form = uic.loadUiType(r'ui\alarm_setting.ui')[0]
crawling_class = crawling.CrawlingClass()

class MainClass(QMainWindow, main_form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.btn_insert.clicked.connect(self.show_insert_url)
        self.btn_remove.clicked.connect(self.delete_product)
        self.btn_get_alarm.clicked.connect(self.get_alarm)
        self.btn_alarm_setting.clicked.connect(self.show_alarm_setting)
        self.btn_auto_play.clicked.connect(self.auto_play)
        
        self.table_product:QTableWidget
        self.table_product.setColumnCount(7)
        # self.table_product.hideColumn(0)
        
        column_names = ["id", "제품", "가격", "옵션", "옵션 값", "품절", "링크"]
        self.table_product.setHorizontalHeaderLabels(column_names)
        
        self.table_product.setColumnWidth(0, 100)  
        self.table_product.setColumnWidth(1, 200)  
        self.table_product.setColumnWidth(2, 100)  
        self.table_product.setColumnWidth(3, 100)  
        self.table_product.setColumnWidth(4, 200)  
        self.table_product.setColumnWidth(5, 100)  
        self.table_product.setColumnWidth(6, 500) 
        
        # database.update_product_by_id(1, new_option_val= "오션,XS (품절)",new_is_soldout=True)
        # database.update_product_by_id(3, new_is_soldout=True)
        # database.update_product_by_id(2, new_option_val= "오션,M",new_is_soldout=False)
        
        self.load_products()
        
    
    def load_products(self):
        print("Load data")
        # 데이터베이스로부터 모든 제품을 가져오기
        products = database.load_all_product()
        
        # 테이블 초기화
        self.table_product.clearContents()  # 모든 셀 내용을 지움
        self.table_product.setRowCount(0)  # 모든 행을 삭제

        # 가져온 데이터를 출력
        for product in products:
            num_rows = self.table_product.rowCount()
            self.table_product.insertRow(num_rows)
            
            if product['is_soldout']:
                soldout = "품절"
            else:
                soldout = "입고"
            
            self.table_product.setItem(num_rows, 0, QTableWidgetItem(str(product['id'])))
            self.table_product.setItem(num_rows, 1, QTableWidgetItem(product['title']))
            self.table_product.setItem(num_rows, 2, QTableWidgetItem(product['price']))
            self.table_product.setItem(num_rows, 3, QTableWidgetItem(product['option_type']))
            self.table_product.setItem(num_rows, 4, QTableWidgetItem(product['option_val']))
            self.table_product.setItem(num_rows, 5, QTableWidgetItem(soldout))
            self.table_product.setItem(num_rows, 6, QTableWidgetItem(product['link']))
        
    
    def add_product(self, product):
        print("add_product", product)
        
        product_id = database.add_product(
            product['제품'],
            product['가격'],
            product['옵션'],
            product['옵션 값'],
            product['품절'] == "품절",
            product['링크']
        )
        
        db_product = database.load_product_by_id(product_id)
        db_product = dict(db_product)
        
        num_rows = self.table_product.rowCount()
        self.table_product.insertRow(num_rows)
        
        if db_product['is_soldout']:
            soldout = "품절"
        else:
            soldout = "입고"
            
        self.table_product.setItem(num_rows, 0, QTableWidgetItem(str(db_product['id'])))
        self.table_product.setItem(num_rows, 1, QTableWidgetItem(db_product['title']))
        self.table_product.setItem(num_rows, 2, QTableWidgetItem(db_product['price']))
        self.table_product.setItem(num_rows, 3, QTableWidgetItem(db_product['option_type']))
        self.table_product.setItem(num_rows, 4, QTableWidgetItem(db_product['option_val']))
        self.table_product.setItem(num_rows, 5, QTableWidgetItem(soldout))
        self.table_product.setItem(num_rows, 6, QTableWidgetItem(db_product['link']))
    
    
    def delete_product(self):
        if self.table_product.rowCount() > 0:
            index = self.table_product.currentRow()
            if index == -1: index =self.table_product.rowCount()-1
            
            print("delete_product, Index: ", index)
            selected_id = self.table_product.item(index, 0).text()
            
            self.table_product.removeRow(index)
            database.delete_product_by_id(selected_id)
        
        
    def show_insert_url(self):
        self.insert_url_window = InsertUrlClass(self)
        self.insert_url_window.show()
        
    def get_alarm(self):
        if not crawling_class.is_broswer_open:
            crawling_class.open_browser(config['is_background'])
        else:
            print("already opened browser")
            
        products = database.load_all_product()
        
        restock_list =[]
        soldout_list =[]
        
        for product in products:
            print(f"search {product['option_val']}")
            url = product['link']
            
            prev_is_soldout = product['is_soldout']
            # print(prev_is_soldout, type(prev_is_soldout))
            
            crawling_class.set_url(url)
            now_is_soldout:bool = crawling_class.check_option_soldout(product['option_val'])
            
            if not now_is_soldout and prev_is_soldout:
                restock_list.append(product)
                print(f"{product['title']} {product['option_val']} is restocked")
                
            elif now_is_soldout and not prev_is_soldout:
                soldout_list.append(product)
                print(f"{product['title']} {product['option_val']} is sold out")
                
            time.sleep(random.uniform(0.5, 1))
            
        for restock_item in restock_list:
            # print(dict(restock_item))
            # print(database.load_product_by_id(item)['option_val'])
            new_option_value:str = restock_item['option_val']
            
            if new_option_value != "":
                msg_op = new_option_value.replace(',', ',   ')
                print(msg_op)
                
                # 품절 때기
                print("restock_item['option_val']: ", restock_item['option_val'])
                new_option_value:str = restock_item['option_val']
                
                temp_list = new_option_value.split(',')
                
                if "(품절)" in temp_list[-1]:
                    new_option_value = new_option_value[:len(new_option_value)-5]
                
                database.update_product_by_id(restock_item['id'], new_option_val=new_option_value, new_is_soldout=False)
                msg = f"*{restock_item['title']}*\n {msg_op}    옵션의 상품이 재입고 되었습니다!\n {restock_item['link']}"
                
            else:
                database.update_product_by_id(restock_item['id'], new_is_soldout=False)
                msg = f"*{restock_item['title']}*   상품이 재입고 되었습니다!\n {restock_item['link']}"
            
            bot.send_msg_to_slack(msg, config["slack_url"])
   
            
        for soldout_item in soldout_list:
            # 품절 붙이기
            new_option_value:str = soldout_item['option_val']
            
            if new_option_value != "":
                temp_list = new_option_value.split(',')
                
                if "(품절)" not in temp_list[-1]:
                    new_option_value += " (품절)"
                
                database.update_product_by_id(soldout_item['id'], new_option_val=new_option_value, new_is_soldout=True)
            else:
                database.update_product_by_id(soldout_item['id'], new_is_soldout=True)
                
        
        self.load_products()
            
            
    def show_alarm_setting(self):
        self.alarm_setting_window = AlarmSettingClass(self)
        self.alarm_setting_window.show()
    
    def auto_play(self):
        self.close()
        auto_play(config['start_times'])
        
    def closeEvent(self, event):
        QCoreApplication.quit()
        
        
class InsertUrlClass(QDialog, insert_url_form):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setupUi(self)
        
        self.btn_confirm.clicked.connect(self.clicked_confirm)
        self.btn_cancle.clicked.connect(self.clicked_cancle)
        
        
    def clicked_confirm(self):
        if not crawling_class.is_broswer_open:
            crawling_class.open_browser(config['is_background'])
        else:
            print("already opened browser")
            
        crawling_class.set_url(self.text_input_url.toPlainText())
        
        self.product = crawling_class.crawling_product()
        print(self.product)
        
        if crawling_class.check_option_page():
            self.hide()
            self.insert_option_window = InsertOptionClass(self)
            self.insert_option_window.show()
        else:
            self.parent.add_product(self.product)
        
        self.close()
        
    def clicked_cancle(self):
        self.close()
        
        
class InsertOptionClass(QDialog):
    def __init__(self, parent):
        super().__init__()
        
        if not crawling_class.is_broswer_open:
            crawling_class.open_browser(config['is_background'])
        else:
            print("already opened browser")
        
        self.parent = parent
        self.setWindowTitle('Option Select')
        self.setGeometry(100, 100, 400, 400)
        self.enable_combo_changed = True
        
        btn_confirm = QPushButton('등록', self)
        btn_cancle = QPushButton('취소', self)
        
        btn_confirm.setGeometry(0, 0, 100, 30)
        btn_cancle.setGeometry(100, 0, 100, 30)
        
        btn_confirm.clicked.connect(self.clicK_btn_confirm)
        btn_cancle.clicked.connect(self.click_btn_cancle)
        
        op_titles, ops = crawling_class.setting_options()
        self.create_options(op_titles, ops)

    def create_options(self, option_titles, options):
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(20)
        
        print(option_titles)
        print(options)
        
        font = QFont()
        font.setFamily('맑은 고딕')
        font.setPointSize(12)
        
        self.combo_boxes = []
        self.combo_labels = []
        for i in range(len(option_titles)):
            label = QLabel(f'{option_titles[i]}:')
            label.font = font
            combo_box = QComboBox()
            combo_box.font = font
            
            # for j in range(len(options)):  # 원하는 수만큼 레이블과 콤보 박스를 생성할 수 있습니다.
            #     combo_box.addItem(options[j])
                
            self.combo_boxes.append(combo_box)
            self.combo_labels.append(label)
            form_layout.addRow(label, combo_box)
            
            combo_box.currentIndexChanged.connect(self.on_combobox_changed)
        
        for i in range(len(options)):
            self.combo_boxes[0].addItem(options[i])
        

        form_layout.setFormAlignment(Qt.AlignCenter)
        self.setLayout(form_layout)
        
    def on_combobox_changed(self, index):
        
        if self.enable_combo_changed:
            self.enable_combo_changed = False
            
            current_combo_box = self.sender()
            selected_text = current_combo_box.currentText()
            current_option_index = self.combo_boxes.index(current_combo_box)
            
            print("selected item is ", index, selected_text)
            print("current combobox is ", current_option_index, self.combo_labels[current_option_index].text())
            next_options = crawling_class.setting_next_option(index, current_option_index)
            if current_option_index + 1 < len(self.combo_boxes):
                
                for i in range(current_option_index + 1, len(self.combo_boxes)):
                    self.combo_boxes[i].clear()
                
                for i in range(len(next_options)):
                    self.combo_boxes[current_option_index + 1].addItem(next_options[i])
            
            self.enable_combo_changed = True
        
        
        
    def clicK_btn_confirm(self):
        temp_list = []
        for combo_box in self.combo_boxes:
            temp_list.append(combo_box.currentText())
        
        last_option = temp_list[-1]
        
        soldout_text = last_option.split()[-1]
        if soldout_text == "(품절)":
            self.parent.product['품절'] = "품절"
        else:
            self.parent.product['품절'] = "입고"
        
        temp_str = ",".join(temp_list)
        
        self.parent.product['옵션 값'] = temp_str
        self.parent.parent.add_product(self.parent.product)
    
    def click_btn_cancle(self):
        self.close()


class AlarmSettingClass(QWidget, alarm_setting_form):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setupUi(self)
        
        self.checkBox_background:QCheckBox
        self.btn_apply.clicked.connect(self.clicked_apply)
        self.btn_cancle.clicked.connect(self.clicked_cancle)
        self.btn_alarm_count_confirm.clicked.connect(self.clicked_alarm_count_confirm)
        
        self.lineEdit_alarm_count:QLineEdit
        self.lineEdit_slack_url:QLineEdit
        self.lineEdit_alarm_count.setValidator(QIntValidator(1, 24, self))
        
        self.checkBox_background.setCheckState(config["is_background"])
        self.lineEdit_slack_url.setText(config["slack_url"])
        
        self.create_alarm_form(config["alarm_count"], config["start_times"])
        
    def create_alarm_form(self, count, time_list):
        self.alarm_formLayout:QFormLayout
        self.lineEdit_alarm_count.setText(str(count))
        
        form_row_count = self.alarm_formLayout.rowCount()
        print("form_row_count: ",form_row_count)
        
        for i in range(form_row_count):
            self.alarm_formLayout.removeRow(0)
        
        self.alarm_formLayout.setVerticalSpacing(15)
        
        font = QFont()
        font.setFamily('맑은 고딕')
        font.setPointSize(12)
        
        self.line_edit_list = []
        for i in range(count):
            label = QLabel(f'알람 받을 시간:')
            label.font = font
            line_edit = QLineEdit()
            
            if len(time_list) <= i:
                line_edit.setText("15:00")
            else:
                line_edit.setText(time_list[i])
                
            line_edit.font = font
            
            self.line_edit_list.append(line_edit)
            self.alarm_formLayout.addRow(label, line_edit)

        self.setLayout(self.alarm_formLayout)
    
    def clicked_alarm_count_confirm(self):
        print(self.lineEdit_alarm_count.text()) 
        
        count = int(self.lineEdit_alarm_count.text())
        
        self.create_alarm_form(count, config["start_times"])
        pass
    
    def clicked_apply(self):
        
        self.lineEdit_time:QLineEdit
        self.lineEdit_hours:QLineEdit
        
        time_list = []
        
        for line_edit in self.line_edit_list:
            time_list.append(line_edit.text())
        
        config["is_background"] = self.checkBox_background.checkState()
        config["slack_url"] = self.lineEdit_slack_url.text()
        config["alarm_count"] = int(self.lineEdit_alarm_count.text())
        config["start_times"] = time_list
        
        with open("config.json", "w") as config_file:
            json.dump(config, config_file)
            
        self.close()

        
    def clicked_cancle(self):
        self.close()


# 자동 알람
def get_alarm():
    if not crawling_class.is_broswer_open:
        crawling_class.open_browser(config['is_background'])
    else:
        print("already opened browser")
    
    products = database.load_all_product()
    
    restock_list =[]
    soldout_list =[]
    
    for product in products:
        print(f"search {product['option_val']}")
        url = product['link']
        
        prev_is_soldout = product['is_soldout']
        # print(prev_is_soldout, type(prev_is_soldout))
        
        crawling_class.set_url(url)
        now_is_soldout:bool = crawling_class.check_option_soldout(product['option_val'])
        
        if not now_is_soldout and prev_is_soldout:
            restock_list.append(product)
        elif now_is_soldout and not prev_is_soldout:
            soldout_list.append(product)
            
        time.sleep(random.uniform(0.5, 1))
        
    for restock_item in restock_list:
        print(dict(restock_item))
        # print(database.load_product_by_id(item)['option_val'])
        new_option_value:str = restock_item['option_val']
        
        if new_option_value != "":
            msg_op = new_option_value.replace(',', ',   ')
            print(msg_op)
            
            # 품절 때기
            print("restock_item['option_val']: ", restock_item['option_val'])
            new_option_value:str = restock_item['option_val']
            
            temp_list = new_option_value.split(',')
            
            if "(품절)" in temp_list[-1]:
                new_option_value = new_option_value[:len(new_option_value)-5]
            
            database.update_product_by_id(restock_item['id'], new_option_val=new_option_value, new_is_soldout=False)
            msg = f"*{restock_item['title']}*\n {msg_op}    옵션의 상품이 재입고 되었습니다!\n {restock_item['link']}"
            
        else:
            database.update_product_by_id(restock_item['id'], new_is_soldout=False)
            msg = f"*{restock_item['title']}*   상품이 재입고 되었습니다!\n {restock_item['link']}"
        
        bot.send_msg_to_slack(msg, config["slack_url"])

        
    for soldout_item in soldout_list:
        # 품절 붙이기
        new_option_value:str = soldout_item['option_val']
        
        if new_option_value != "":
            temp_list = new_option_value.split(',')
            
            if "(품절)" not in temp_list[-1]:
                new_option_value += " (품절)"
            
            database.update_product_by_id(soldout_item['id'], new_option_val=new_option_value, new_is_soldout=True)
        else:
            database.update_product_by_id(soldout_item['id'], new_is_soldout=True)
            
    crawling_class.quit_browser()
    
def auto_play(start_times:list):
    schedule.clear()
    
    for start_time in start_times:
        schedule.every().day.at(start_time).do(get_alarm)
    
    print(f"time schedule: {start_times} is running")

    while True:
        schedule.run_pending()
        time.sleep(1)
        
            



from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import os
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font
import random
import time

class CrawlingClass():
    def open_browser(self):
        chrome_options = webdriver.ChromeOptions()

        chrome_options.add_argument(r"--user-data-dir=C:\Users\dudcj\AppData\Local\Google\Chrome")
        chrome_options.add_argument("--profile-directory=Profile_1")

        ChromeDriverManager().install()
        self.driver = webdriver.Chrome(options=chrome_options)
        
        
    def set_url(self, url:str):
        self.url = url
        self.driver.get(self.url)
        
    def crawling_product(self) -> dict:
        print("crawling_product")
        link = self.driver.current_url

        try:
            self.driver.find_element(By.CLASS_NAME, "_2BQ-WF2QUb")
            sold_out = "품절"
        except:
            sold_out = "입고"
            
        print(sold_out)
        option_div = self.driver.find_element(By.CLASS_NAME, "bd_2dy3Y")
        options = option_div.find_elements(By.CLASS_NAME, "bd_1fhc9")
        options_text_list = []

        for i in range(len(options)):
            options_text_list.append(options[i].text)
            
        options_text = ','.join(options_text_list)

        title_text = self.driver.find_element(By.CLASS_NAME, '_22kNQuEXmb').text
        price_text = self.driver.find_elements(By.CLASS_NAME, '_1LY7DqCnwR')[-1].text

        print(title_text)
        print(price_text)

        product_data = {
            "제품": title_text,
            "가격": price_text,
            "옵션": options_text,
            "옵션 값": "",
            "품절": sold_out,
            "링크":  link
        }

        return product_data
    
    def setting_options(self) -> list:
        print("setting_options")
        
        # 상세페이지가 불러와질떄까지 대기
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "_2QCa6wHHPy"))
            )
            print("page is loaded")
        except:
            print("page loading is failed")
            
        # 옵션 div
        option_div = self.driver.find_element(By.CLASS_NAME, "bd_2dy3Y")
        option_btns =  option_div.find_elements(By.CLASS_NAME, "bd_1fhc9")
        
        option_titles =[]
        for btn in option_btns:
            option_titles.append(btn.text)

        options= []
        
        # 옵션 리스트 열고 크롤링하고 대기
        option_btns[0].click()
        elems = option_div.find_elements(By.CLASS_NAME, "bd_3iRne")
            
        for elem in elems:
            options.append(elem.text)
        
        # 옵션 리스트 닫기
        option_btns[0].click()
        
        print(option_titles)
        print(options)
        
        return option_titles, options
    
    
    def setting_next_option(self, option_index:int, btn_index:int) -> list:
        print("setting_next_option")
        
        option_div = self.driver.find_element(By.CLASS_NAME, "bd_2dy3Y")
        option_btns =  option_div.find_elements(By.CLASS_NAME, "bd_1fhc9")
        options= []
        
        # 해당 옵션 리스트를 열기
        if btn_index < len(option_btns)-1:
            option_btns[btn_index].click()
            
            # 옵션 리스트 가져오기
            elems = option_div.find_elements(By.CLASS_NAME, "bd_3iRne")
            print(f"selected {elems[option_index].text}")       
            elems[option_index].click()
        
        # 다음 옵션 리스트를 열고 리스트 크롤링
        if btn_index < len(option_btns)-1:
            option_btns[btn_index + 1].click()
            print(f"clicked {option_btns[btn_index].text}")
            elems = option_div.find_elements(By.CLASS_NAME, "bd_3iRne")
                
            for elem in elems:
                options.append(elem.text)
                
            option_btns[btn_index + 1].click()
        
        print(options)
        
        return options
    
    def check_option_page(self):
        try:
            no_option = self.driver.find_element(By.CLASS_NAME, "bd_2cuha")
            print("This page has no options")
            return False
        except:
            print("This page has option")
            return True
    
    def check_soldout(self):
        try:
            soldout = self.driver.find_element(By.CLASS_NAME, "_2BQ-WF2QUb")
            print("All sold out")
        except:
            pass
        
    def check_option_soldout(self, options:str) -> bool:
        print("check_option_soldout")
        
        # 상세페이지가 불러와질떄까지 대기
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "_2QCa6wHHPy"))
            )
            print("page is loaded")
        except:
            print("page loading is failed")
            
        # 옵션 div
        option_div = self.driver.find_element(By.CLASS_NAME, "bd_2dy3Y")
        option_types =  option_div.find_elements(By.CLASS_NAME, "bd_1fhc9")
        
        split_options = options.split(',')
        
        last_option = split_options[-1]
        
        # 옵션에서 품절 text 제거
        if "(품절)" in last_option:
            last_length = len(last_option)
            last_option = last_option[:last_length-5]
            print(last_option)
            split_options[-1] = last_option
        
        is_soldout:bool = False
        
        for i in range(len(option_types)):
            option_types[i].click()
            option_type_elems = option_div.find_elements(By.CLASS_NAME, "bd_3iRne")
            
            for elem in option_type_elems:
                # print(f"{option_types[i].text}, {elem.text}, {split_options[i]}")
                
                if elem.text == split_options[i] and i < len(option_types)-1:
                    print(f"selected {elem.text}")
                    elem.click()
                    break
                elif elem.text == split_options[i] and i == len(option_types)-1:
                    is_soldout = False
                    print("this product is not sold out")
                    break
                elif elem.text == split_options[i] + " (품절)" and i == len(option_types)-1:
                    is_soldout = True
                    print("this product is sold out")
                    break
                    
        print(options, " sold out is ", is_soldout)
        return is_soldout
    
            
                    
            
        
        
        
                

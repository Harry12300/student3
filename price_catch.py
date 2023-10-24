from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import time

# 設定下載目錄
options = webdriver.ChromeOptions()
download_directory = "D:\專題\student"  # 將目錄路徑替換為您想要的下載目錄
options.add_experimental_option("prefs", {
    "download.default_directory": download_directory,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

# 初始化瀏覽器
driver = webdriver.Chrome(options=options)

# 載入目標網站
url = "https://amis.afa.gov.tw/veg/VegProdTransInfoCP.aspx"
driver.get(url)

# 等待3秒
time.sleep(1)

# 找到日期輸入框並輸入日期
date_input = driver.find_element(By.CSS_SELECTOR, "#ctl00_contentPlaceHolder_txtPrevSTransDate")
date_input.click()

time.sleep(1)

date_input = driver.find_element(By.CSS_SELECTOR, "tr:nth-child(2) td:nth-child(6) font:nth-child(1)")
date_input.click()

time.sleep(1)

#市場
handles = driver.window_handles
driver.find_element(By.XPATH,"/html/body/form/table/tbody/tr[3]/td[2]/table/tbody/tr[2]/td/table/tbody/tr[2]/td[4]/textarea",).click()

element3 = driver.find_element(By.XPATH, ('//*[@id="divDialog"]/iframe'))
driver.switch_to.frame(element3)

time.sleep(1)

handles1 = driver.window_handles
driver.find_element(By.XPATH,"/html/body/form/div[3]/table/tbody/tr[2]/td/select/option[2]",).click()

time.sleep(1)

driver.find_element(By.XPATH,"/html/body/form/div[3]/table/tbody/tr[3]/td/input",).click()
driver.switch_to.window(handles[0])

time.sleep(1)
##############3 產品點選
handles = driver.window_handles
driver.find_element(By.XPATH,"/html/body/form/table/tbody/tr[3]/td[2]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[4]/textarea",).click()

time.sleep(1)

element3 = driver.find_element(By.XPATH, ('//*[@id="divDialog"]/iframe'))
driver.switch_to.frame(element3)

handles1 = driver.window_handles
driver.find_element(By.XPATH,"/html/body/form/div[4]/div/table/tbody/tr[1]/td/table/tbody/tr[2]/td[1]/input",).click()

time.sleep(1)

# 找到多選框元素，通常是一個<select>元素
select_element = driver.find_element(By.XPATH, '/html/body/form/div[4]/div/table/tbody/tr[3]/td/select')

# 使用Select物件包裝多選框元素
from selenium.webdriver.support.ui import Select
select = Select(select_element)

# 開始迭代選項，從option[2]到option[128]
for i in range(2, 129):
    option_xpath = f'/html/body/form/div[4]/div/table/tbody/tr[3]/td/select/option[{i}]'
    option_element = driver.find_element(By.XPATH, option_xpath)
    select.select_by_value(option_element.get_attribute("value"))

driver.find_element(By.XPATH,"/html/body/form/div[4]/div/table/tbody/tr[4]/td/input",).click()
driver.switch_to.window(handles[0])

handles1 = driver.window_handles
driver.find_element(By.XPATH,"/html/body/form/table/tbody/tr[3]/td[2]/table/tbody/tr[2]/td/table/tbody/tr[7]/td/input[1]",).click()

time.sleep(2)

handles1 = driver.window_handles
driver.find_element(By.XPATH,"/html/body/form/table/tbody/tr[3]/td[2]/table/tbody/tr[2]/td/table/tbody/tr[7]/td/input[2]",).click()

time.sleep(2)


# 最後，關閉瀏覽器
driver.quit()

import xlrd
import openpyxl

# 打開原始Excel檔案（使用xlrd來讀取舊的.xls格式）
input_file = "蔬菜產品行情比較.xls"
workbook = xlrd.open_workbook(input_file)
sheet = workbook.sheet_by_index(0)

# 要提取的欄位範圍
columns_to_extract = [0, 2, 3]
start_row = 6  # 注意：xlrd的索引從0開始，所以這裡使用7表示第8行
end_row = sheet.nrows

# 創建一個新的Excel檔案
output_file = "output.xlsx"
output_workbook = openpyxl.Workbook()
output_sheet = output_workbook.active

# 提取資料並寫入新的Excel檔案
for row in range(start_row, end_row):
    output_row = []
    for column_index in columns_to_extract:
        cell_value = sheet.cell_value(row, column_index)
        output_row.append(cell_value)

    output_sheet.append(output_row)

# 保存新的Excel文件
output_workbook.save(output_file)

##############

# 打开Excel文件
input_file = "output.xlsx"
output_file = "output.xlsx"  # 输出文件与输入文件相同

# 打开工作簿
workbook = openpyxl.load_workbook(input_file)
sheet = workbook.active

# 从B列和C列获取数据并四舍五入
for row in sheet.iter_rows(min_row=1, min_col=2, max_col=3):
    for cell in row:
        if cell.value is not None:
            cell.value = round(cell.value)  # 四舍五入为整数

# 保存修改后的工作簿
workbook.save(output_file)
print("数据已四舍五入并保存回 output.xlsx")

##################

import openpyxl

# 打开Excel文件
input_file = "output.xlsx"
output_file = "output.xlsx"  # 输出文件与输入文件相同

# 打开工作簿
workbook = openpyxl.load_workbook(input_file)
sheet = workbook.active

# 插入一列在A列之后
sheet.insert_cols(2)  # 在A列之后插入一列

# 复制A列的数据到新插入的列
for row in sheet.iter_rows(min_row=1, max_row=sheet.max_row, min_col=1, max_col=1):
    for cell in row:
        if cell.value is not None:
            new_cell = sheet.cell(row=cell.row, column=2, value=cell.value)

# 保存修改后的工作簿
workbook.save(output_file)
print("已在A列之后插入一列，并复制A列的数据到新列")

####################

import openpyxl
import re

# 打开Excel文件
input_file = "output.xlsx"
output_file = "output.xlsx"  # 输出文件与输入文件相同

# 打开工作簿
workbook = openpyxl.load_workbook(input_file)
sheet = workbook.active

# 处理A列：保留英文和数字，删除中文
for row in sheet.iter_rows(min_row=1, max_row=sheet.max_row, min_col=1, max_col=1):
    for cell in row:
        if cell.value is not None:
            # 使用正则表达式匹配中文字符并删除
            cell.value = re.sub(r'[\u4e00-\u9fff]', '', cell.value)

# 处理B列：保留中文，删除英文和数字
for row in sheet.iter_rows(min_row=1, max_row=sheet.max_row, min_col=2, max_col=2):
    for cell in row:
        if cell.value is not None:
            # 使用正则表达式匹配英文和数字并删除
            cell.value = re.sub(r'[a-zA-Z0-9]', '', cell.value)

# 保存修改后的工作簿
workbook.save(output_file)
print("已处理A列和B列的数据")

###

import csv
import openpyxl

# 打开output.xlsx
input_file = "output.xlsx"
workbook = openpyxl.load_workbook(input_file)
sheet = workbook.active

# 创建一个CSV文件并打开以写入
output_csv = "price.csv"
with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)

    # 遍历工作表中的行
    for row in sheet.iter_rows(values_only=True):
        # 使用列表推导式去除每个字段中的空格
        cleaned_row = [str(cell).strip() for cell in row]
        csv_writer.writerow(cleaned_row)

print(f"数据已保存为 {output_csv}")

import os

file_to_delete1 = "蔬菜產品行情比較.xls"
file_to_delete2 = "output.xlsx"

os.remove(file_to_delete1)
os.remove(file_to_delete2)



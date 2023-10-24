from flask import Flask, render_template, request, redirect, jsonify
import base64
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import csv
import subprocess
import pandas as pd
from datetime import datetime
from flask import Flask, redirect, render_template
from flask_socketio import SocketIO
from flask import Flask, render_template, request  # flask裡要抓前端用的
from keras.models import load_model  # 跟keras有關的都是模型要用的
from keras.utils import load_img, img_to_array
import keras.utils as image
import numpy as np  # 模型機率要用的

app = Flask(__name__)
socketio = SocketIO(app)

HOSTNAME = '127.0.0.1'
PORT = '3306'
USERNAME = 'root'
PASSWORD = '123456'
DATABASE = 'demo'
app.config[
    'SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8"
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    chines = db.Column(db.Integer)
    math = db.Column(db.Integer)
    english = db.Column(db.Integer)


class Price(db.Model):
    id = db.Column(db.String(80), nullable=False, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price_up = db.Column(db.Integer)
    price_down = db.Column(db.Integer)


# 資料庫初始化
with app.app_context():
    db.create_all()


@app.route('/')
def aaa():
    return render_template('admin.html')


@app.route('/search')
def search():
    price = Price.query.all()
    return render_template('search.html', price=price)


#############價格抓取###############
@app.route('/price_catch')
def price_catch():
    try:
        # 使用subprocess执行price_catch.py脚本
        subprocess.run(["python", "price_catch.py"], check=True)
        return redirect('/price_import')
    except subprocess.CalledProcessError as e:
        return f"price_catch.py 腳本執行失敗，錯誤訊息：{e}"


##############價格導入覆蓋################
@app.route('/price_import')
def price_import():
    file_path = 'D:/專題/student/price.csv'
    # 读取CSV文件
    df = pd.read_csv(file_path, encoding='utf-8')
    for index, row in df.iterrows():
        id, name, price_up, price_down = row

        if not pd.isnull(id):  # 檢查id是否有效
            existing_price = Price.query.filter_by(id=id).first()  # 只有在id有效時才進行查詢

            if existing_price:
                # 如果记录已存在，覆盖现有数据
                existing_price.name = name
                existing_price.price_up = price_up
                existing_price.price_down = price_down
            else:
                # 如果记录不存在，创建新记录
                new_price_entry = Price(id=id, name=name, price_up=price_up, price_down=price_down)
                db.session.add(new_price_entry)

    db.session.commit()

    return "價格導入成功"



@app.route('/identify')
def identify():
    return render_template('identify.html')


######################蔬菜辨識##############################
'''
category={
    0: 'FA1黃秋葵', 1: 'FB花椰菜', 2: 'FC胡瓜', 3: 'FD花胡瓜', 4: 'FE冬瓜',
    5: 'FF絲瓜', 6: 'FG苦瓜', 7: 'FH扁蒲', 8: 'FI茄子', 9: 'FJ番茄',
    10: 'FK甜椒', 11: 'FL豌豆', 12: 'FM菜豆', 13: 'FN敏豆', 14: 'FP萊豆',
    15: 'FQ毛豆', 16: 'FR青花苔', 17: 'FS越瓜', 18: 'FT南瓜', 19: 'FU3石蓮花',
    20: 'FU隼人瓜', 21: 'FV辣椒', 22: 'FW2洛神花', 23: 'FY玉米', 24: 'FZ落花生',
    25: 'LA甘藍', 26: 'LB小白菜', 27: 'LC包心白', 28: 'LD青江白菜', 29: 'LE皇宮菜',
    30: 'LF蕹菜', 31: 'LG芹菜', 32: 'LH菠菜', 33: 'LI萵苣菜', 34: 'LJ芥菜',
    35: 'LK芥藍菜', 36: 'LM莧菜', 37: 'LN油菜', 38: 'LO甘薯葉', 39: 'LP2九層塔',
    40: 'LP3羅勒', 41: 'LP芫荽', 42: 'LQ紅鳳菜', 43: 'LS茴香', 44: 'LV巴西利',
    45: 'LX蕨菜', 46: 'LY1西洋菜', 47: 'LY2黑甜仔菜', 48: 'LY3豬母菜', 49: 'LZ2藤川七',
    50: 'MA洋菇', 51: 'MB草菇', 52: 'MC濕木耳', 53: 'MD濕香菇', 54: 'ME金絲菇',
    55: 'MF蠔菇', 56: 'MG巴西蘑菇', 57: 'MI秀珍菇', 58: 'MJ杏鮑菇', 59: 'MK鴻禧菇',
    60: 'ML珊瑚菇', 61: 'MN柳松菇', 62: 'SA蘿蔔', 63: 'SB胡蘿蔔', 64: 'SC馬鈴薯',
    65: 'SD洋蔥', 66: 'SE青蔥', 67: 'SF韭菜', 68: 'SG大蒜', 69: 'SH竹筍',
    70: 'SJ芋', 71: 'SK荸薺', 72: 'SL1豆薯', 73: 'SM牛蒡', 74: 'SN蓮藕',
    75: 'SO甘薯', 76: 'SP薑', 77: 'SQ茭白筍', 78: 'SR菱角', 79: 'SU薯蕷',
    80: 'SV蘆筍', 81: 'SW球莖甘藍', 82: 'SX芽菜類', 83: 'SZ4百合', 84: 'SZ7晚香玉筍'
}
'''
category = {
    0: 'FA1', 1: 'FB', 2: 'FC', 3: 'FD', 4: 'FE',
    5: 'FF', 6: 'FG', 7: 'FH', 8: 'FI', 9: 'FJ',
    10: 'FK', 11: 'FL', 12: 'FM', 13: 'FN', 14: 'FP',
    15: 'FQ', 16: 'FR', 17: 'FS', 18: 'FT', 19: 'FU3',
    20: 'FU', 21: 'FV', 22: 'FW2', 23: 'FY', 24: 'FZ',
    25: 'LA', 26: 'LB', 27: 'LC', 28: 'LD', 29: 'LE',
    30: 'LF', 31: 'LG', 32: 'LH', 33: 'LI', 34: 'LJ',
    35: 'LK', 36: 'LM', 37: 'LN', 38: 'LO', 39: 'LP2',
    40: 'LP3', 41: 'LP', 42: 'LQ', 43: 'LS', 44: 'LV',
    45: 'LX', 46: 'LY1', 47: 'LY2', 48: 'LY3', 49: 'LZ2',
    50: 'MA', 51: 'MB', 52: 'MC', 53: 'MD', 54: 'ME',
    55: 'MF', 56: 'MG', 57: 'MI', 58: 'MJ', 59: 'MK',
    60: 'ML', 61: 'MN', 62: 'SA', 63: 'SB', 64: 'SC',
    65: 'SD', 66: 'SE', 67: 'SF', 68: 'SG', 69: 'SH',
    70: 'SJ', 71: 'SK', 72: 'SL1', 73: 'SM', 74: 'SN',
    75: 'SO', 76: 'SP', 77: 'SQ', 78: 'SR', 79: 'SU',
    80: 'SV', 81: 'SW', 82: 'SX', 83: 'SZ4', 84: 'SZ7'
}

# 這是訓練好的模型架構你沒有要進行辨識 所以你可以複製就好
model = load_model('D:/專題/student/model_senior_project_best_clear.h5')


def predict_label(img_path):  # 預測函數
    try:
        # 實現圖像預處理，例如調整大小、正規化等
        i = image.load_img(img_path, target_size=(128, 128))
        i = image.img_to_array(i) / 255.0  # 正規化
        i = np.expand_dims(i, axis=0)  # 一維陣列轉換成一個二維陣列

        predictions = model.predict(i)
        predicted_class = np.argmax(predictions, axis=1)[0]
        confidence = predictions[0][predicted_class]  # 獲取預測類別的置信度

        if confidence > 0.6:  # 調整閾值
            return category[predicted_class]
        else:
            return f"識別置信度低於閾值。 請使用不同的圖像.{confidence}"
    except Exception as e:
        print(f"辨識失敗或錯誤，請重新上傳其他照片: {e}")
        return "無法辨識圖像。 請嘗試使用不同的圖像."


# routes設定
@app.route("/", methods=['GET', 'POST'])
def main():
    # 將 "index.html" 模板呈現給用戶，顯示在用戶的瀏覽器中
    return render_template("identify.html")


# 按了傳送後的route位子
@app.route("/submit", methods=['GET', 'POST'])
def get_output():
    if request.method == 'POST':
        img = request.files['my_image']
        img_path = "static/" + img.filename
        img.save(img_path)
        p = predict_label(img_path)

        price_record = Price.query.filter_by(id=p).first()

        if price_record:
            price_name = price_record.name
            price_up = price_record.price_up
            price_down = price_record.price_down
        else:
            price_name = "N/A"
            price_up = "N/A"
            price_down = "N/A"

        return render_template("identify.html", prediction=p, img_path=img_path, price_name=price_name,
                               price_up=price_up, price_down=price_down)


####################################################

#########################時時辨識########################
@app.route("/canmera", methods=['GET', 'POST'])
def canmera():

    return render_template("canmera.html")




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)

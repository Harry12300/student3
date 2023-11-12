from flask_sqlalchemy import SQLAlchemy
import subprocess
import pandas as pd
from flask import Flask, redirect, render_template, request
from flask_socketio import SocketIO
from keras.models import load_model
import keras.utils as image
import numpy as np

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

class Price(db.Model):
    id = db.Column(db.String(80), nullable=False, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price_up = db.Column(db.Integer)
    price_down = db.Column(db.Integer)

class Price2(db.Model):
    id = db.Column(db.String(80), nullable=False, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price_L1 = db.Column(db.Integer)
    price_L2 = db.Column(db.Integer)
    price_L3 = db.Column(db.Integer)
    price_L4 = db.Column(db.Integer)
    price_L5 = db.Column(db.Integer)
    price_L6 = db.Column(db.Integer)
    price_L7 = db.Column(db.Integer)


# 資料庫初始
with app.app_context():
    db.create_all()

@app.route('/')
def aaa():
    return render_template('admin.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['searchInput']
        results = Price2.query.filter_by(name=search_term).all()
        return render_template('search.html', price=results)
    else:
        price = Price2.query.all()
        return render_template('search.html', price=price)


#############價格抓取###############
@app.route('/price_catch')
def price_catch():
    try:
        # 使用subprocess执行price_catch.py脚本
        subprocess.run(["python", "price_catch2.py"], check=True)
        return redirect('/price_import')
    except subprocess.CalledProcessError as e:
        return f"price_catch.py 腳本執行失敗，錯誤訊息：{e}"

##############價格導入覆蓋################
@app.route('/price_import')
def price_import():
    file_path = 'D:/專題/student/price.csv'
    df = pd.read_csv(file_path, encoding='utf-8')

    for index, row in df.iterrows():
        id, name, price_L1 = row

        if not pd.isnull(id):
            existing_price = Price2.query.filter_by(id=id).first()

            if existing_price:
                # 移動數據
                existing_price.price_L7 = existing_price.price_L6
                existing_price.price_L6 = existing_price.price_L5
                existing_price.price_L5 = existing_price.price_L4
                existing_price.price_L4 = existing_price.price_L3
                existing_price.price_L3 = existing_price.price_L2
                existing_price.price_L2 = existing_price.price_L1

                # 更新紀錄
                existing_price.name = name
                existing_price.price_L1 = price_L1
            else:
                # 如果沒有紀錄，創新
                new_price_entry = Price2(
                    id=id,
                    name=name,
                    price_L1=price_L1,
                    price_L2=None,
                    price_L3=None,
                    price_L4=None,
                    price_L5=None,
                    price_L6=None,
                    price_L7=None,
                )
                db.session.add(new_price_entry)

    db.session.commit()
    print("價格導入資料庫成功")
    return ("價格導入資料庫成功")

######################蔬菜辨識##############################
@app.route('/identify')
def identify():
    price = Price2.query.filter_by().all
    return render_template('identify.html',price=price)

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


def predict_label(img_path):
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

@app.route("/submit", methods=['GET', 'POST'])
def get_output():
    if request.method == 'POST':
        img = request.files['my_image']
        img_path = "static/" + img.filename
        img.save(img_path)
        p = predict_label(img_path)

        price = Price2.query.filter_by(id=p).first()

        return render_template("identify.html", prediction=p, img_path=img_path, price=price)
####################################################

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)

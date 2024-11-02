import os
import telebot
import pandas as pd
from flask import Flask, request
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

# Настройки для Telegram и Flask
TOKEN = "7687451703:AAHcWRT7jSbTEBUUjeJW4gM-P9ps42g9tNA"
WEBHOOK_URL = f"https://dashboard.render.com/web/srv-csiueeu8ii6s73cro12g/{TOKEN}" 
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

data = pd.read_excel('Homes_enc.xlsx')
X = data.drop(['Цена'], axis=1)
y = data['Цена']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model2 = RandomForestRegressor(max_depth=14, random_state=42)
model2.fit(X_train, y_train)

@bot.message_handler(commands=['start'])
def handle_text(message): 
    q_kk = bot.send_message(message.chat.id, 'Введите количество комнат') 
    bot.register_next_step_handler(q_kk, get_kk)

def get_kk(message):
    global kk
    try:
        kk = int(message.text)
        q_et = bot.send_message(message.chat.id, 'Введите номер этажа')
        bot.register_next_step_handler(q_et, get_et)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите число.")

def get_et(message):
    global et
    try:
        et = int(message.text)
        q_sq = bot.send_message(message.chat.id, 'Введите площадь')
        bot.register_next_step_handler(q_sq, get_sq)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите число.")

def get_sq(message):
    global sq
    try:
        sq = float(message.text)
        q_cr = bot.send_message(message.chat.id, 'Находится ли квартира в городе Рудаки? (да/нет)')
        bot.register_next_step_handler(q_cr, get_cr)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите число.")

def get_cr(message):
    global cr
    cr = 1 if message.text.strip().lower() == "да" else 0
    q_ckh = bot.send_message(message.chat.id, 'Находится ли квартира в городе Худжанд? (да/нет)')
    bot.register_next_step_handler(q_ckh, get_ckh)

def get_ckh(message):
    global ckh
    ckh = 1 if message.text.strip().lower() == "да" else 0
    q_nw = bot.send_message(message.chat.id, 'Является ли квартира новостройкой? (да/нет)')
    bot.register_next_step_handler(q_nw, get_nw)

def get_nw(message):
    global nw
    nw = 1 if message.text.strip().lower() == "да" else 0
    q_blt = bot.send_message(message.chat.id, 'Построен ли дом? (да/нет)')
    bot.register_next_step_handler(q_blt, get_blt)

def get_blt(message):
    global blt
    blt = 1 if message.text.strip().lower() == "да" else 0
    q_rem = bot.send_message(message.chat.id, 'Есть ли ремонт в квартире? (да/нет)')
    bot.register_next_step_handler(q_rem, get_rem)

def get_rem(message):
    global rem
    rem = 1 if message.text.strip().lower() == "да" else 0
    q_nw_rem = bot.send_message(message.chat.id, 'Новый ли ремонт в квартире? (да/нет)')
    bot.register_next_step_handler(q_nw_rem, get_nw_rem)

def get_nw_rem(message):
    global nw_rem
    nw_rem = 1 if message.text.strip().lower() == "да" else 0
    
    df1 = pd.DataFrame({
        'Комнаты': [kk], 
        'Этаж': [et], 
        'Площадь': [sq], 
        'Город_Рудаки': [cr], 
        'Город_Худжанд': [ckh], 
        'Тип_Новостройка': [nw], 
        'Состояние_Построено': [blt], 
        'Ремонт_Новый_ремонт': [nw_rem], 
        'Ремонт_С_ремонтом': [rem]
    })
    
    reslt = model2.predict(df1).round(1)[0]
    bot.send_message(message.chat.id, f'Примерная цена: {reslt} сомон')

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

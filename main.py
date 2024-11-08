import os
import telebot
import pandas as pd
from flask import Flask, request
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

# Настройки для Telegram и Flask
TOKEN = "7687451703:AAHcWRT7jSbTEBUUjeJW4gM-P9ps42g9tNA"
WEBHOOK_URL = f"https://tgbot.onrender.com/{TOKEN}"  # Замените на актуальный URL Render
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Загрузка и подготовка данных, обучение модели
data = pd.read_excel('Homes_enc.xlsx')
X = data.drop(['Цена'], axis=1)
y = data['Цена']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestRegressor(max_depth=14, random_state=42)
model.fit(X_train, y_train)

# Словарь для хранения данных пользователя между шагами
user_data = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_data[message.chat.id] = {}
    bot.send_message(message.chat.id, 'Введите количество комнат')
    bot.register_next_step_handler(message, get_kk)

# Последовательные функции для сбора данных от пользователя
def get_kk(message):
    try:
        user_data[message.chat.id]['Комнаты'] = int(message.text)
        bot.send_message(message.chat.id, 'Введите номер этажа')
        bot.register_next_step_handler(message, get_et)
    except ValueError:
        bot.send_message(message.chat.id, "Введите число.")

def get_et(message):
    try:
        user_data[message.chat.id]['Этаж'] = int(message.text)
        bot.send_message(message.chat.id, 'Введите площадь')
        bot.register_next_step_handler(message, get_sq)
    except ValueError:
        bot.send_message(message.chat.id, "Введите число.")

def get_sq(message):
    try:
        user_data[message.chat.id]['Площадь'] = float(message.text)
        bot.send_message(message.chat.id, 'Находится ли квартира в городе Рудаки? (да/нет)')
        bot.register_next_step_handler(message, get_cr)
    except ValueError:
        bot.send_message(message.chat.id, "Введите число.")

def get_cr(message):
    user_data[message.chat.id]['Город_Рудаки'] = 1 if message.text.strip().lower() == "да" else 0
    bot.send_message(message.chat.id, 'Находится ли квартира в городе Худжанд? (да/нет)')
    bot.register_next_step_handler(message, get_ckh)

def get_ckh(message):
    user_data[message.chat.id]['Город_Худжанд'] = 1 if message.text.strip().lower() == "да" else 0
    bot.send_message(message.chat.id, 'Является квартира новостройкой? (да/нет)')
    bot.register_next_step_handler(message, get_nw)

def get_nw(message):
    user_data[message.chat.id]['Тип_Новостройка'] = 1 if message.text.strip().lower() == "да" else 0
    bot.send_message(message.chat.id, 'Построен ли дом? (да/нет)')
    bot.register_next_step_handler(message, get_blt)

def get_blt(message):
    user_data[message.chat.id]['Состояние_Построено'] = 1 if message.text.strip().lower() == "да" else 0
    bot.send_message(message.chat.id, 'Есть ли ремонт в квартире? (да/нет)')
    bot.register_next_step_handler(message, get_rem)

def get_rem(message):
    user_data[message.chat.id]['Ремонт_С_ремонтом'] = 1 if message.text.strip().lower() == "да" else 0
    bot.send_message(message.chat.id, 'Новый ли ремонт в квартире? (да/нет)')
    bot.register_next_step_handler(message, calculate_price)

def calculate_price(message):
    user_data[message.chat.id]['Ремонт_Новый_ремонт'] = 1 if message.text.strip().lower() == "да" else 0
    
    # Создание DataFrame с введёнными данными
    user_input = pd.DataFrame([user_data[message.chat.id]])
    # Получение прогноза и отправка результата
    price_prediction = model.predict(user_input)[0].round(1)
    bot.send_message(message.chat.id, f'Примерная цена: {price_prediction} сомон')

# Настройка Webhook
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

# Запуск приложения
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

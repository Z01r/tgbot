import telebot
import pandas as pd
from flask import Flask, request
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from telebot import types
from catboost import CatBoostRegressor
from sklearn.preprocessing import LabelEncoder
import math

token = "7687451703:AAHcWRT7jSbTEBUUjeJW4gM-P9ps42g9tNA"
bot = telebot.TeleBot(token)
server = Flask(__name__)

# Загрузка и подготовка данных
data = pd.read_excel('Homes_dush.xlsx')
label_encoder = LabelEncoder()
for column in ["Тип", "Состояние", "Ремонт"]:
    data[column] = label_encoder.fit_transform(data[column])

X = data.drop(['Цена'], axis=1)
y = data['Цена']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestRegressor(max_depth=14, random_state=42)
model.fit(X_train, y_train)

# Убираем выбросы
data1 = {
    'actual': y,
    'predicted': model.predict(X)
}
df_data = pd.DataFrame(data1)
df_data['residuals'] = df_data['actual'] - df_data['predicted']
threshold = 200000
large_residuals_indices = df_data[abs(df_data['residuals']) > threshold].index.tolist()
df2 = data.copy()
df2 = df2.drop(index=large_residuals_indices)
X = df2.drop(['Цена'], axis=1)
y = df2['Цена']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
model2 = CatBoostRegressor(verbose=0)
model2.fit(X_train, y_train)

# Словарь для хранения данных пользователя
user_input = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Здравствуйте! Я помогу вам рассчитать цену квартиры.")
    ask_room_count(message)

def ask_room_count(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add("1", "2", "3", "4", "5", "6")
    bot.send_message(message.chat.id, "Введите количество комнат:", reply_markup=markup)
    bot.register_next_step_handler(message, get_room_count)

def get_room_count(message):
    user_input['kk'] = int(message.text)
    ask_floor(message)

def ask_floor(message):
    markup = types.ReplyKeyboardMarkup(row_width=5, one_time_keyboard=True)
    buttons = [str(i) for i in range(1, 26)]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "Введите номер этажа (от 1 до 25):", reply_markup=markup)
    bot.register_next_step_handler(message, get_floor)

def get_floor(message):
    user_input['et'] = int(message.text)
    ask_area(message)

def ask_area(message):
    bot.send_message(message.chat.id, "Введите площадь:")
    bot.register_next_step_handler(message, get_area)

def get_area(message):
    try:
        user_input['sq'] = float(message.text)
        ask_type_building(message)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите число.")
        ask_area(message)

def ask_type_building(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add("Новостройка", "Вторичный рынок")
    bot.send_message(message.chat.id, "Введите тип квартиры:", reply_markup=markup)
    bot.register_next_step_handler(message, get_type_building)

def get_type_building(message):
    user_input['tpb'] = 1 if message.text.strip().lower() == "новостройка" else 0
    ask_is_built(message)

def ask_is_built(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add("Построено", "На стадии строительства")
    bot.send_message(message.chat.id, "Построен ли дом?", reply_markup=markup)
    bot.register_next_step_handler(message, get_is_built)

def get_is_built(message):
    user_input['blt'] = 1 if message.text.strip().lower() == "построено" else 0
    ask_repair(message)

def ask_repair(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add("Без ремонта(коробка)", "С ремонтом", "Новый ремонт")
    bot.send_message(message.chat.id, "Введите состояние ремонта:", reply_markup=markup)
    bot.register_next_step_handler(message, get_repair)

def get_repair(message):
    if message.text.strip().lower() == "без ремонта(коробка)":
        user_input['rem'] = 0
    elif message.text.strip().lower() == "с ремонтом":
        user_input['rem'] = 2
    elif message.text.strip().lower() == "новый ремонт":
        user_input['rem'] = 1
    calculate_price(message)

def calculate_price(message):
    try:
        df1 = pd.DataFrame({
            'Комнаты': [user_input['kk']], 
            'Этаж': [user_input['et']], 
            'Площадь': [user_input['sq']], 
            'Тип': [user_input['tpb']], 
            'Состояние': [user_input['blt']], 
            'Ремонт': [user_input['rem']]
        })
        
        predicted_price = model2.predict(df1).round(1)[0]
        bot.send_message(message.chat.id, f"Цена находится в диапозоне от {math.ceil(round(model.predict(df1)[0]*0.85,0)/10000)*10000} до {math.floor(round(model.predict(df1)[0]*1.15,0)/10000)*10000}")
        bot.send_message(message.chat.id, 'Если хотите узнать цену другой квартиры, напишите /start для начала.')
    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка при получении прогноза. Попробуйте снова.")
        print(f"Ошибка при прогнозировании: {e}")

@server.route(f"/{token}", methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://tgbot-2vks.onrender.com/{token}") 
    server.run(host="0.0.0.0", port=5000)

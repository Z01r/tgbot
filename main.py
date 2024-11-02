import telebot
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression 
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score,mean_absolute_percentage_error
from telebot import types

token = "7687451703:AAHcWRT7jSbTEBUUjeJW4gM-P9ps42g9tNA"
bot = telebot.TeleBot(token)
@bot.message_handler(commands=['start'])
def handle_text(message): 
    q_kk = bot.send_message(message.chat.id, 'Введите количество комнат') 
    bot.register_next_step_handler(q_kk ,get_kk)

def get_kk(message):
   global kk;
   kk = message.text
   q_et = bot.send_message(message.chat.id, 'Введите номер этажа')
   bot.register_next_step_handler(q_et ,get_et)
   
def get_et(message):
    global et;
    et = message.text      
    q_sq = bot.send_message(message.chat.id, 'Введите площадь')
    bot.register_next_step_handler(q_sq ,get_sq)
def get_sq(message):
    global sq;
    sq = message.text      
    q_cr = bot.send_message(message.chat.id, 'Находится ли квартира в городе Рудаки? Если квартира находится в Душанбе введите :"нет"')
    bot.register_next_step_handler(q_cr ,get_cr)
def get_cr(message):
    global cr;
    cr = message.text  
    cr = cr.strip()
    if cr.lower() == "да":
        cr = 1
    else:
        cr = 0     
    q_ckh = bot.send_message(message.chat.id, 'Находится ли квартира в городе Худжанд? Если квартира находится в Душанбе введите :"нет"')
    bot.register_next_step_handler(q_ckh ,get_ckh)
def get_ckh(message):
    global ckh;
    ckh = message.text  
    ckh = ckh.strip()
    if ckh.lower() == "да":
        ckh = 1
    else:
        ckh = 0     
    q_nw = bot.send_message(message.chat.id, 'Является квартира ли новостройкой?')
    bot.register_next_step_handler(q_nw ,get_nw)
def get_nw(message):
    global nw;
    nw = message.text  
    nw = nw.strip()
    if nw.lower() == "да":
        nw = 1
    else:
        nw = 0     
    q_blt = bot.send_message(message.chat.id, 'Построен ли дом?')
    bot.register_next_step_handler(q_blt ,get_blt)
def get_blt(message):
    global blt;
    blt = message.text  
    blt = blt.strip()
    if blt.lower() == "да":
        blt = 1
    else:
        blt = 0
    q_rem = bot.send_message(message.chat.id, 'Есть ли ремонт в квартире?')
    bot.register_next_step_handler(q_rem ,get_rem)
def get_rem(message):
    global rem;
    rem = message.text  
    rem = rem.strip()
    if rem.lower() == "да":
        rem = 1
    else:
        rem = 0     
    q_nw = bot.send_message(message.chat.id, 'Новый ли ремонт в квартире? Если его нет то введите: "нет"')
    bot.register_next_step_handler(q_nw ,get_nw_rem)

def get_nw_rem(message):
    global nw_rem;
    nw_rem = message.text
    nw_rem = nw_rem.strip()
    if nw_rem.lower() == "да":
        nw_rem = 1
    else:
        nw_rem = 0
    data = pd.read_excel('Homes_enc.xlsx')
    X = data.drop(['Цена'],axis=1)
    y = data['Цена']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model2 = RandomForestRegressor(max_depth=14, random_state=42)
    model2.fit(X_train, y_train)
    y_pred2 = model2.predict(X_test)
    df1 =pd.DataFrame({ 
    'Комнаты':[kk], 
    'Этаж':[et], 
    'Площадь':[sq], 
    'Город_Рудаки':[cr], 
    'Город_Худжанд':[ckh], 
    'Тип_Новостройка':[nw], 
    'Состояние_Построено':[blt], 
    'Ремонт_Новый_ремонт':[nw_rem], 
    'Ремонт_С_ремонтом':[rem]})
    reslt = model2.predict(df1).round(1)
    reslt1 = reslt[0]
    bot.send_message(message.chat.id,f'Примерная ценна : {(reslt1).round(1)} сомон')
bot.polling(none_stop=True) 

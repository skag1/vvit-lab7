import telebot
from telebot import types
import psycopg2


conn = psycopg2.connect(database="mtuci_schedule",
                        user="postgres",
                        password="123",
                        host="localhost",
                        port="5432")
cursor = conn.cursor()

token = '6259917091:AAG0oizBo0Z6o1-4lOIYQIWxdCLf5FOefmo'
bot = telebot.TeleBot(token)

message_monday = 'Понедельник'
message_tuesday = 'Вторник'
message_wednesday = 'Среда'
message_thursday = 'Четверг'
message_friday = 'Пятница'
message_saturday = 'Суббота'
message_sunday = 'Воскресенье'
message_week = 'Неделя'
message_current_week = 'Расписание на текущую неделю'
message_next_week = 'Расписание на следующую неделю'
message_back = 'Назад в меню'
this_week = 'четная'


def get_schedule_day(day, week):
    cursor.execute("SELECT timetable.subject_name, timetable.room_numb, timetable.start_time, teacher.full_name "
                   "FROM timetable "
                   "JOIN teacher ON teacher.subject_name = timetable.subject_name "
                   "WHERE w_day =%s  AND week =%s ORDER BY start_time", (str(day), str(week)))
    schedule = cursor.fetchall()
    text = '\n'
    text += '<' + day + '>\n'
    text += '----------------------------------\n'
    for row in schedule:
        text += str('<' + row[0]) + '>  <' + str(row[1]) + '>  <' + str(row[2]) + '>  <' + str(row[3]) + '>\n'
    if schedule == []:
        text += '<Нет пар>\n'
    text += '----------------------------------\n'
    return text

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row("Хочу", "/help")
    keyboard.row("Узнать расписание")
    bot.send_message(message.chat.id, 'Привет! Хочешь узнать свежую информацию о МТУСИ?', reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id,
                     'Я могу:\n'
                     'Показывать расписание\n'
                     '/help - получить список доступных команд\n'
                     '/mtuci - получить ссылку на сайт МТУСИ\n'
                     '/week - узнать какая сейчас идет неделя')


@bot.message_handler(commands=['mtuci'])
def start_message(message):
    bot.send_message(message.chat.id, 'Официальный сайт МТУСИ доступен по ссылке: https://mtuci.ru/')


@bot.message_handler(commands=['week'])
def start_message(message):
    cursor.execute("SELECT numb FROM current_week")
    current_week = cursor.fetchone()
    if (current_week[0] % 2 == 0):
        this_week = 'четная'
    else:
        this_week = 'нечетная'
    bot.send_message(message.chat.id,
                     'Сейчас идет ' + this_week + ' неделя\n')


@bot.message_handler(content_types=['text'])
def answer(message):
    global this_week
    text = message.text
    if text == "Хочу":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in ['Узнать расписание', '/help']])
        bot.send_message(message.chat.id, 'Тогда тебе сюда - https://mtuci.ru/', reply_markup=keyboard)
    elif text == "Узнать расписание":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in [message_current_week, message_next_week, message_back,'/help']])
        bot.send_message(message.chat.id, 'Выберите кнопку', reply_markup=keyboard)
    elif text == message_current_week:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in
                              [message_monday, message_tuesday, message_wednesday, message_thursday, message_friday,
                               message_week, message_back, '/help']])
        cursor.execute("SELECT numb FROM current_week")
        current_week = cursor.fetchone()
        if (current_week[0] % 2 == 0):
            this_week = 'четная'
        else:
            this_week = 'нечетная'
        bot.send_message(message.chat.id,
                         'Сейчас идет ' + this_week + ' неделя\n')
        bot.send_message(message.chat.id, 'Выберите день недели', reply_markup=keyboard)
    elif text == message_next_week:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in
                              [message_monday, message_tuesday, message_wednesday, message_thursday, message_friday,
                               message_week, message_back, '/help']])
        cursor.execute("SELECT numb FROM current_week")
        current_week = cursor.fetchone()
        if (current_week[0] % 2 == 0):
            this_week = 'нечетная'
        else:
            this_week = 'четная'
        bot.send_message(message.chat.id,
                         'Следующая неделя ' + this_week + '\n')
        bot.send_message(message.chat.id, 'Выберите день недели', reply_markup=keyboard)
    elif text in [message_monday, message_tuesday, message_wednesday, message_thursday, message_friday, message_saturday, message_sunday]:
        bot.send_message(message.chat.id, get_schedule_day(text, this_week))
    elif text == message_week:
        week = get_schedule_day(message_monday, this_week)
        week += get_schedule_day(message_tuesday, this_week)
        week += get_schedule_day(message_wednesday, this_week)
        week += get_schedule_day(message_thursday, this_week)
        week += get_schedule_day(message_friday, this_week)
        bot.send_message(message.chat.id, week)
    elif text == message_back:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in ['Узнать расписание', '/help']])
        bot.send_message(message.chat.id, 'Меню', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Извините, я Вас не понял')

bot.polling(none_stop=True)
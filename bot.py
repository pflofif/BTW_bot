import telebot
from telebot import types
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

BOT_TOKEN = '6565093408:AAGIcEAhweOQO5mEWS8QWujfxbYhawdIqKo'
MONGO_URL = "mongodb+srv://CinemaPflofif:LzsOTdMmsFBiaovB@cluster0.oadkx5w.mongodb.net/?retryWrites=true&w=majority"
bot = telebot.TeleBot(BOT_TOKEN)

client = MongoClient(MONGO_URL, server_api=ServerApi('1'))
db = client["BTW_XII"]
collection = db["users"]


class User:
    def __init__(self, name=None, department=None, course=None, phone=None, isVisitBefore=None, chat_id=None):
        self.name = name
        self.department = department
        self.course = course
        self.phone = phone
        self.isVisitBefore = isVisitBefore
        self.chat_id = chat_id


user = User()


@bot.message_handler(commands=['start'])
def ask_name(message):
    user.chat_id = message.chat.id
    about_btw = "Що ж таке це BTW?\n\nBEST Training Week — це тиждень тренінгів для всіх, хто прагне розвиватися та вдосконалювати свої навички. Наші спікери поговорять про різні теми, такі як особистий бренд IT, психологію, подорожі та багато іншого. Це унікальна нагода вивчити нове і знайти спільноту однодумців. Реєстрація проста, а доступ до знань — безплатний."
    bot.send_message(message.chat.id, about_btw)

    text = 'Хочемо дізнатись тепер трохи більше про тебе. Почнімо реєстрацію!\n Як тебе звати?'
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, ask_department)


@bot.message_handler(func=lambda message: message.text.lower() == 'розклад')
def send_schedule(message):
    with open('schedule_text.txt', 'r', encoding='utf-8') as file:
        text = file.read()

    schedule_text = text.split('\n\n\n')

    for paragraph in schedule_text:
        bot.send_message(message.chat.id, paragraph)

    with open("schedule.png", "rb") as img:
        bot.send_photo(message.chat.id, img)


@bot.message_handler(func=lambda message: message.text.lower() == 'чат btw xii')
def send_chat_link(message):
    text = "https://t.me/+3S1qZOXANY03MWYy"
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda message: message.text.lower() == 'спікери')
def send_speakers(message):
    bot.send_message(message.chat.id, "Зустрічайте, спікери BTW XII!")
    speakers = [
        {
            "image_path": "images/second.png",
            "caption": "Юлія Ющук\nОсобистий бренд в ІТ"
        },
        {
            "image_path": "images/three.png",
            "caption": "Шудра Дмитро\nЯк розробляють ігри та ким можна працювати у геймдеві"
        },
        {
            "image_path": "images/first.png",
            "caption": "Ден Бєліцький\nТуризм в межах України"
        },
        {
            "image_path": "images/four.png",
            "caption": "Aнжела Матусовська\nЯк попасти в Рек"
        },
        {
            "image_path": "images/five.png",
            "caption": "Михайло Пацан\nChatGPT та Web3 - як інструменти для ефективного розвитку"
        }
    ]

    for speaker in speakers:
        with open(speaker["image_path"], "rb") as img:
            bot.send_photo(message.chat.id, img, caption=speaker["caption"])


def ask_department(message):
    user.name = message.text

    text = "На якому факультеті ти навчаєшся?"

    sent_msg = bot.send_message(
        message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, ask_course)


def ask_course(message):
    user.department = message.text

    text = 'Який ти курс?'
    keyboard = ["Бакалавр 1",
                "Бакалавр 2",
                "Бакалавр 3",
                "Бакалавр 4",
                "Магістр 1",
                "Магістр 2"]

    sent_msg = send_message_with_reply_keyboard(
        message.chat.id, text, keyboard)
    bot.register_next_step_handler(sent_msg, ask_phone)


def ask_phone(message):
    user.course = message.text
    text = 'Поділись, будь ласка, контактним номером телефону'

    sent_msg = bot.send_message(
        message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, ask_visiting_of_prev_btw)


def ask_visiting_of_prev_btw(message):
    user.phone = message.text

    text = 'Розкажи, чи відвідував/ла ти BTW раніше?'

    keyboard = ["Так, BTW IX або раніше",
                "Так, BTW X",
                "Так, BTW XI",
                "Буде вперше",]

    sent_msg = send_message_with_reply_keyboard(
        message.chat.id, text, keyboard)
    bot.register_next_step_handler(sent_msg, ask_is_confirm)


def ask_is_confirm(message):
    user.isVisitBefore = message.text

    text = 'Дякую! І останнє, дуже важливе. Цією кнопкою підтверджую, що надана інформація є достовірною, даю згоду на обробку та зберігання персональних даних, вказаних у боті, даю дозвіл на фото- та відеозйомку під час проєкту і зобов’язуюсь дотримуватись всіх протоколів безпеки.'

    keyboard = ["Підтверджую!"]

    sent_msg = send_message_with_reply_keyboard(
        message.chat.id, text, keyboard)
    bot.register_next_step_handler(sent_msg, confirm_handler)


def confirm_handler(message):
    text = "Супер! Реєстрація завершена. Чекаємо тебе на BTW з 18-22 вересня!🥰"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Розклад")
    markup.add("Спікери")
    markup.add("Чат BTW XII")
    bot.send_message(
        message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

    try:
        collection.insert_one(user.__dict__)
    except Exception as e:
        print(str(e))


def send_message_with_reply_keyboard(chat_id, text, keyboard):
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True)
    markup.add(*keyboard)
    sent_msg = bot.send_message(
        chat_id, text, parse_mode="Markdown", reply_markup=markup)
    return sent_msg


bot.infinity_polling()

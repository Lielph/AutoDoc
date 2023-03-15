import telebot
import sqlite3
import datetime

bot = telebot.TeleBot('6113944950:AAEZLCzU0dHrMJlbEKa5W3OGUcsw8ng7uuE')


@bot.message_handler(commands = ['start'])
def start(message):
    mess: str = f'Привет, <b>{message.from_user.first_name}</b>'
    bot.send_message(message.chat.id,mess, parse_mode="html")

@bot.message_handler(content_types=['photo'])
def get_user_photo(message):
    idphoto = str(message.photo[0].file_id)
    user_id = str(message.chat.username)
    Upload_to_dataBase(idphoto,user_id)
    bot.send_message(message.chat.id, "Фото загружено в базу")

def Show_Last_Uploaded():
    connect = sqlite3.connect("Data_base.db",detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = connect.cursor()
    rows = cursor.execute("SELECT Photo_id FROM User_Photos ORDER BY date DESC LIMIT 1")
    for row in rows:
        return row[0]
    connect.close()


def Upload_to_dataBase(Photo_Link, user_id):
    now = datetime.datetime.now()
    connect = sqlite3.connect("Data_base.db",detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = connect.cursor()
    cursor.execute("INSERT INTO User_Photos VALUES(?,?,?)", (user_id,str(now.strftime("%d-%m-%Y %H:%M")), Photo_Link))
    connect.commit()
    connect.close()



@bot.message_handler(commands = ['last'])
def show(message):
    idphoto = Show_Last_Uploaded()
    bot.send_message(message.chat.id, "Последнее загруженное фото")
    bot.send_photo(message.chat.id, idphoto)

bot.polling(none_stop=True)
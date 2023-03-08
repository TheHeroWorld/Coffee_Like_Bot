import os
import telebot
from PIL import Image
import logging
import random

logging.basicConfig(level=logging.INFO,
                    filename="bot.log",
                    format='%(asctime)s %(levelname)s: %(message)s')

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

mom = ['Маме 1.png', "Маме 2.png"]
grandmom = [
    'Бабушка 1.png',
    'Бабушке 2.png',
]
collega = [
    'Коллеге 1.png',
    'Коллеге 2.png',
]
love = [
    'Любимой 1.png',
    'Любимой 2.png',
]
sister = [
    "Сестре 1.png",
    'Сестре 2.png',
]
daughter = [
    "Дочке 1.png",
    'Дочке 2.png',
]
Friend = [
    "Подруге 1.png",
    'Подруге 2.png',
]
me = [
    "Себе 1.png",
    'Себе 2.png',
]

button_text = {
    'mom': 'Маме 💝',
    'grandmom': 'Бабушке 👵🏼',
    'colleague': 'Коллеге 👩‍💼',
    "love": "Любимой 👩‍❤‍👨",
    "sister": "Сестре 👯‍♀",
    "daughter": "Дочке 👧🏼",
    "Friend": "Подруге💃",
    "me": "Себе 🧚‍♀",
}


@bot.message_handler(commands=['start'])
def start_handler(message):
    """Ловим /start"""
    chat_id = message.chat.id
    bot.send_message(
        chat_id,
        'Привет! Это фотобот COFFEE LIKE, и он поможет тебе сделать очень душевные и приятные поздравления для твоих близких. 💚 Нужно только прислать фото, из которого получится милая открыточка.'
    )
    logging.info(f"Пользавотель {chat_id} запустил бота")
    start(message)


def start(message, retry=False):
    """Создаем кнопки для выбора"""
    chat_id = message.chat.id
    username = message.from_user.username
    markup = telebot.types.InlineKeyboardMarkup()
    btn1 = telebot.types.InlineKeyboardButton(text='Маме 💝',
                                              callback_data='mom')
    btn2 = telebot.types.InlineKeyboardButton(text='Бабушке 👵🏼',
                                              callback_data='grandmom')
    btn3 = telebot.types.InlineKeyboardButton(text='Коллеге 👩‍💼',
                                              callback_data='colleague')
    btn4 = telebot.types.InlineKeyboardButton(text='Любимой 👩‍❤‍👨',
                                              callback_data='love')
    btn5 = telebot.types.InlineKeyboardButton(text='Сестре 👯‍♀',
                                              callback_data='sister')
    btn6 = telebot.types.InlineKeyboardButton(text='Дочке 👧🏼',
                                              callback_data='daughter')
    btn7 = telebot.types.InlineKeyboardButton(text='Подруге💃',
                                              callback_data='Friend')
    btn8 = telebot.types.InlineKeyboardButton(text='Себе 🧚‍♀',
                                              callback_data='me')
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8)
    if retry == False:
        bot.send_message(
            chat_id,
            'Укажи, для кого будем делать открытку:',
            reply_markup=markup,
        )
    else:
        bot.send_message(chat_id, 'Еще разок?', reply_markup=markup)
    logging.info(
        f"Пользавотель:{username} ID: {chat_id} выбирает кому сделать открытку"
    )


@bot.callback_query_handler(func=lambda call: True)
def Frames(call):
    """Функция которая ждет пока пользавотель загрузит свою фотку"""
    original_text = call.message.text
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id,
                              text="Выбрано: " + button_text[call.data])
    if call.data == "me":
        bot.send_message(
            chat_id,
            f'Вы выбрали {button_text[call.data]}. Загрузите своё фото.')
    else:
        bot.send_message(
            chat_id,
            f'Вы выбрали {button_text[call.data]}. Загрузите её фото (лучше портрет)'
        )
    bot.edit_message_text(chat_id=chat_id,
                          message_id=call.message.message_id,
                          text=original_text,
                          reply_markup=None)
    bot.register_next_step_handler(
        call.message, lambda message: choice_user(message, call.data))
    logging.info(f"Ловим кнопку {chat_id}")


def choice_user(message, call):
    """Проверяет что выбрал пользавотель"""
    chat_id = message.chat.id
    username = message.from_user.username
    choices = {
        'mom': mom,
        'grandmom': grandmom,
        'colleague': collega,
        'love': love,
        'sister': sister,
        'daughter': daughter,
        'Friend': Friend,
        'me': me
    }
    if call in choices:
        choice = random.choice(choices[call])
        frame = Image.open(choice).convert('RGBA')
        logging.info(f"Пользователь:{username} ID: {chat_id} выбрал {call} ")
        save_and_combine_photo(message, frame)


def save_and_combine_photo(message, frame):
    """Комбинация фото и рамки"""
    chat_id = message.chat.id
    username = message.from_user.username
    try:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path
        file_name = f"{chat_id}_{file_id}.jpg"
        if not os.path.exists('photos'):
            os.makedirs('photos')
        file = bot.download_file(file_path)
        with open(f"photos/{file_name}", 'wb') as f:
            f.write(file)
        bot.send_message(chat_id, "Вжух вжух, обработка фото 🪄 ")
        # загрузка рамки и фото
        photo = Image.open(f"photos/{file_name}").convert('RGBA')
        # Проверяем соотношение сторон фото и рамки
        # определение соотношения сторон рамки и фото
        frame_ratio = frame.width / frame.height
        photo_ratio = photo.width / photo.height
        # обрезка фото, если соотношение сторон не совпадает с рамкой
        if frame_ratio != photo_ratio:
            if frame_ratio > photo_ratio:
                new_height = int(photo.width / frame_ratio)
                diff = (photo.height - new_height) // 2
                photo = photo.crop((0, diff, photo.width, diff + new_height))
            else:
                new_width = int(photo.height * frame_ratio)
                diff = (photo.width - new_width) // 2
                photo = photo.crop((diff, 0, diff + new_width, photo.height))
        # Изменяем размер рамки до размеров фото
        frame = frame.resize(photo.size)
        logging.info(f"Делаем resize для :{username} ID: {chat_id}")
        # изменение размера фото
        photo = Image.alpha_composite(photo, frame)
        logging.info(f"Обьединяем фото для :{username} ID: {chat_id}")
        # сохранение объединенного изображения
        combined_path = f"Final/{file_name}"
        photo.save(combined_path, format='PNG')
        logging.info(f"Сохроняем фото для :{username} ID: {chat_id}")
        with open(combined_path, "rb") as f:
            bot.send_photo(chat_id, f)
        os.remove(f"photos/{file_name}")
        os.remove(combined_path)
        logging.info(f"Удаляем фото :{username} ID: {chat_id}")
        start(message, retry=True)
        bot.send_message(chat_id,
                         'Готово! Открытку можно отправлять адресату 👍')
        bot.send_message(
            chat_id,
            'Будет еще круче, если ты поделишься этой открыткой в сториз Instagram или ВКонтакте и отметишь нас @coffeelike_com 😻'
        )
        logging.info(f"Обработка фото и отправка пользавотелю  {chat_id}")
    except Exception as e:
        bot.reply_to(message, "Ошибка: загрузи фото еще раз ")
        logging.critical('Критическая ошибка: %s', e)
        start(message)
        return


def check_tokens():
    """Проверяем доступность переменных окружения."""
    token = ("TELEGRAM_TOKEN")
    logging.info("Check Token")
    for token_name in token:
        if globals()[token_name] is None:
            return None
        return all([token_name])


bot.polling(none_stop=True, interval=0)


def main():
    """Основная функция"""

    if not check_tokens():
        logging.critical('Empty token')
        raise KeyError('Empty token')
    telebot.TeleBot(TELEGRAM_TOKEN)


if __name__ == '__main__':
    main()

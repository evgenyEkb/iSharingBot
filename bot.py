import sqlite3
import telebot
from telebot import types
import datetime
import pytz
import user_state_def
import users_def
import item_type_def
import item_for_rent_def
import config
import find_request_def

# release 1


conn = sqlite3.connect(config.db_path, check_same_thread=False)
cursor = conn.cursor()


bot = telebot.TeleBot(config.bot_token)


# TODO подумать над формулировкой диалогов + добавить обращение по имени
#  пользователя

# TODO сделать логгироавние действий пользователя


@bot.message_handler(commands=['start', 'share', 'find'])
def start_message(message):
    user_id = message.chat.id
    if users_def.check_user_registration(cursor, user_id):
        if message.text == '/start':
            user_state_def.set_current_user_state(conn, cursor, user_id,
                                                  user_state_def.States.S_CHOICE_OPERATING_MODE.value)
            start_sharing_procedure(message)
        elif message.text == '/share':
            user_state_def.set_current_user_state(conn, cursor, user_id,
                                                  user_state_def.States.S_SELECT_SHARING_OPERATING_MODE.value)
            share_item(message)
        elif message.text == '/find':
            user_state_def.set_current_user_state(conn, cursor, user_id,
                                                  user_state_def.States.S_SELECT_FIND_OPERATING_MODE.value)
            find_item(message)
    else:
        # TODO разобраться с часовыми поясами
        # TODO упростить этот блок
        user_date_registration = datetime.datetime.now(pytz.utc)
        user = users_def.check_user_data(user_id,
                                         message.from_user.first_name,
                                         message.from_user.last_name,
                                         "new_user",
                                         user_date_registration)
        users_def.registration_user_in_db(conn, cursor, user[0], user[1],
                                          user[2], user[3], user[4], 1,
                                          'Без адреса')
        user_state_def.set_current_user_state(conn, cursor, user_id,
                                              user_state_def.States.S_CHOICE_OPERATING_MODE.value)
        start_sharing_procedure(message)


@bot.message_handler(func=lambda message: user_state_def.get_current_user_state(cursor, message.chat.id) ==
                                          user_state_def.States.S_CHOICE_OPERATING_MODE.value)
def start_sharing_procedure(message):
    keyboard = types.InlineKeyboardMarkup()
    key_share = types.InlineKeyboardButton(text='Предложить вещь в '
                                                'пользование.',
                                           callback_data='share')
    keyboard.add(key_share)
    key_find = types.InlineKeyboardButton(text='Найти вещь в пользование.',
                                          callback_data='find')
    keyboard.add(key_find)
    bot.send_message(message.chat.id, "Что вы хотите сделать?",
                     reply_markup=keyboard)


@bot.message_handler(func=lambda message: user_state_def.get_current_user_state(cursor, message.chat.id) ==
                                          user_state_def.States.S_SELECT_SHARING_OPERATING_MODE.value)
def share_item(message):
    # TODO сделать выгрузку из БД имени пользователя по message.chat.id
    user_id = message.chat.id
    bot.send_message(user_id, "Введи название вещи, которую хочешь сдавать в "
                              "аренду (в именительном падеже, в ед. числе):")
    user_state_def.set_current_user_state(conn, cursor, user_id,
                                          user_state_def.States.S_SHARING_ENTER_ITEM_TYPE_FOR_ADD_DB.value)


@bot.message_handler(func=lambda message: user_state_def.get_current_user_state(cursor, message.chat.id) ==
                                          user_state_def.States.S_SHARING_ENTER_ITEM_TYPE_FOR_ADD_DB.value)
def get_item_type(message):
    user_id = message.chat.id
    item_type_name = message.text
    item_type_id = item_type_def.check_item_type(conn, cursor, item_type_name)
    item_for_rent_def.tmp_save_item_type_id_and_owner_id(conn, cursor,
                                                         user_id, item_type_id)
    bot.send_message(user_id, "Напиши характеристики/параметры вещи, которые "
                              "позволят другим людям понять, подходит ли она "
                              "им или нет:")
    user_state_def.set_current_user_state(conn, cursor, user_id,
                                           user_state_def.States.S_SHARING_ENTER_ITEM_DESC_FOR_ADD_DB.value)


@bot.message_handler(func=lambda message: user_state_def.get_current_user_state(cursor, message.chat.id) ==
                                          user_state_def.States.S_SHARING_ENTER_ITEM_DESC_FOR_ADD_DB.value)
def get_item_desc(message):
    user_id = message.chat.id
    item_desc = message.text
    item_for_rent_def.tmp_save_item_desc(conn, cursor, user_id, item_desc)
    bot.send_message(user_id, "Пришли фото вещи (можно прислать только 1 "
                              "фото):")
    bot.register_next_step_handler(message, get_item_photo)
    user_state_def.set_current_user_state(conn, cursor, user_id,
                                           user_state_def.States.S_SHARING_ENTER_ITEM_PHOTO_FOR_ADD_DB.value)


# @bot.message_handler(content_types=["photo"], func=lambda message:
# user_state_def.get_current_user_state(cursor, message.chat.id) ==
@bot.message_handler(func=lambda message: user_state_def.get_current_user_state(cursor, message.chat.id) ==
                                          user_state_def.States.S_SHARING_ENTER_ITEM_PHOTO_FOR_ADD_DB.value)
# TODO разобраться почему не вызывается хендлер если остановили скрипт на
#  этапе получения фото (не обрабатывает контент photo)
def get_item_photo(message):
    user_id = message.chat.id
    if message.content_type == 'photo':
        f_id = message.photo[-1].file_id
        file_info = bot.get_file(f_id)
        item_photo = bot.download_file(file_info.file_path)
        item_type_id = item_for_rent_def.tmp_get_item_for_rent(cursor,
                                                               user_id)[0]
        item_desc = item_for_rent_def.tmp_get_item_for_rent(cursor,
                                                               user_id)[1]
        item_for_rent_def.add_item_for_rent_db(conn, cursor, item_type_id,
                                               item_desc, user_id, item_photo)
        item_for_rent_def.tmp_del_item_for_rent(conn, cursor, user_id)
        bot.send_message(user_id, "Спасибо! Информация добавлена в базу данных")
        start_sharing_procedure(message)
    else:
        bot.send_message(user_id, "Присланное сообщение не является "
                                  "изображением. Нужно прислать файл с "
                                  "фотографией")
        bot.register_next_step_handler(message, get_item_photo)


# Ниже все про поиск вещей в аренду
@bot.message_handler(func=lambda message: user_state_def.get_current_user_state(cursor, message.chat.id) ==
                                          user_state_def.States.S_SELECT_FIND_OPERATING_MODE.value)
def find_item(message):
    # TODO сделать выгрузку из БД имени пользователя по message.chat.id
    user_id = message.chat.id
    bot.send_message(user_id, "Введи название вещи (в именительном "
                              "падеже, в ед. числе), которую хочешь найти "
                              "в пользование:")
    user_state_def.set_current_user_state(conn, cursor, user_id,
                                           user_state_def.States.S_FIND_ENTER_ITEM_TYPE.value)


@bot.message_handler(func=lambda message: user_state_def.get_current_user_state(cursor, message.chat.id) ==
                                          user_state_def.States.S_FIND_ENTER_ITEM_TYPE.value)
def print_item_for_rent_list(message):
    user_id = message.chat.id
    request_author_id = user_id
    find_request_def.del_tmp_find_request_for_author(conn, cursor,
                                                     request_author_id)
    item_type_name = message.text
    # TODO item_type_id находить по type_name внутри
    #  item_for_rent_def.search_item_for_rent
    item_type_id = item_type_def.check_item_type(conn, cursor, item_type_name)
    records = item_for_rent_def.search_item_for_rent(cursor, item_type_id)
    if records:
        request_result_id = 0
        for row in records:
            item_id = row[0]
            item_desc = row[2]
            owner_id = row[3]
            find_request_def.add_tmp_find_request(conn, cursor,
                                                  request_author_id,
                                                  owner_id,
                                                  request_result_id,
                                                  item_type_name, item_desc,
                                                  item_id)
            keyboard = types.InlineKeyboardMarkup()
            key_view_profile = types.InlineKeyboardButton(
                text='Посмотреть профиль владельца. Написать ему '
                     'сообщение.', url='tg://user?id='+str(owner_id))
            keyboard.add(key_view_profile)
            request_result_id = request_result_id + 1
            bot.send_photo(user_id, photo=row[4],
                           caption='Название: '+item_type_name+'. \
                                   Характеристики: '+item_desc+'.',
                           reply_markup=keyboard)
    else:
        bot.send_message(user_id, 'Такой вещи ('+item_type_name+') не найдено.')
    bot.send_message(user_id, 'Поиск завершен. Вы можете повторить поиск '
                              'нужной вещи, введя ее название или перейти в '
                              'главное меню, выбрав команду /start')


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "share":
        share_item(call.message)
    elif call.data == "find":
        find_item(call.message)


bot.infinity_polling()
# bot.polling()

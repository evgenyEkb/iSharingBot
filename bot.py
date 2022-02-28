# TODO сделать логгирование действий пользователя

import psycopg2
import telebot
from telebot import types
import datetime
import pytz
from PIL import Image
import user_state_def
import users_def
import item_type_def
import item_for_rent_def
import config
import find_request_def
import io
import queue_messages_def
# import asyncio
import time


conn = psycopg2.connect(user="postgres", password="/k0jrWg8M45(pPga", host="127.0.0.1",
                        port="5432", database="iSharingBot")
cursor = conn.cursor()


bot = telebot.TeleBot(config.bot_token)


def del_not_actual_notification(user_id):
    message_item_list = queue_messages_def.get_queue_message_by_owner_id(cursor, user_id, -2)
    for row in message_item_list:
        try:
            time.sleep(0.5)
            queue_messages_def.del_queue_message_by_id(conn, cursor, row[0])
            bot.delete_message(user_id, row[0])
        except:
            print('Ошибка при удалении неактуальных уведомлений')


def del_not_actual_messages(user_id, item_id):
    message_item_list = queue_messages_def.get_queue_message_by_owner_id(cursor, user_id, item_id)
    for row in message_item_list:
        try:
            queue_messages_def.del_queue_message_by_id(conn, cursor, row[0])
            bot.delete_message(user_id, row[0])
        except:
            print('Ошибка при удалении неактуальных сообщений')


def add_to_queue_messages(user_id, message_id, item_id):
    if not queue_messages_def.check_message_in_queue(cursor, message_id):
        queue_messages_def.add_item_in_queue_message(conn, cursor, user_id, message_id, item_id)


@bot.message_handler(commands=['start', 'share', 'find', 'view_all_category', 'admin_self', 'admin_item_list'])
def start_message(message):
    user_id = message.chat.id
    del_not_actual_messages(user_id, 0)
    add_to_queue_messages(user_id, message.message_id, -1)
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
        elif message.text == '/view_all_category':
            user_state_def.set_current_user_state(conn, cursor, user_id,
                                                  user_state_def.States.S_CHOICE_OPERATING_MODE.value)
            view_all_category(message)
        elif message.text == '/admin_self':
            user_state_def.set_current_user_state(conn, cursor, user_id,
                                                  user_state_def.States.S_ADMIN_SELF.value)
            admin_self(message)
        elif message.text == '/admin_item_list':
            admin_item_list(message)
    else:
        # TODO разобраться с часовыми поясами
        # TODO упростить этот блок
        # TODO 2. подумать и возможно вернуть блок с вводом адреса?????
        user_date_registration = datetime.datetime.now(pytz.utc)
        user = users_def.check_user_data(user_id, message.from_user.first_name, message.from_user.last_name,
                                         "new_user", user_date_registration)
        users_def.registration_user_in_db(conn, cursor, user[0], user[1], user[2], user[3], user[4], 1,
                                          'Без адреса')
        user_state_def.set_current_user_state(conn, cursor, user_id,
                                              user_state_def.States.S_CHOICE_OPERATING_MODE.value)
        start_sharing_procedure(message)


@bot.message_handler(func=lambda message: user_state_def.get_current_user_state(cursor, message.chat.id) ==
                                          user_state_def.States.S_ADMIN_SELF.value)
def admin_self(message):
    user_id = message.chat.id
    # TODO сделать отработку если функция вернула False
    user_address_old = users_def.get_user_address(cursor, user_id)
    message_id = bot.send_message(message.chat.id,
                                  "Введите новый адрес. Прежний адрес: " + user_address_old).message_id
    add_to_queue_messages(user_id, message_id, -1)
    user_state_def.set_current_user_state(conn, cursor, user_id,
                                          user_state_def.States.S_ADMIN_SELF_UPDATE_ADDRESS.value)


@bot.message_handler(func=lambda message: user_state_def.get_current_user_state(cursor, message.chat.id) ==
                     user_state_def.States.S_ADMIN_SELF_UPDATE_ADDRESS.value)
def admin_self_update_address(message):
    user_id = message.chat.id
    add_to_queue_messages(user_id, message.message_id, -1)
    user_address_new = message.text
    # TODO сделать отработку если функция вернула False
    # TODO Сделать подтверждение изменение адреса yes/no
    users_def.set_user_address(conn, cursor, user_id, user_address_new)
    del_not_actual_messages(user_id, 0)
    message_id = bot.send_message(user_id, "Спасибо! Адрес изменен.").message_id
    add_to_queue_messages(user_id, message_id, -2)
    del_not_actual_notification(user_id)
    user_state_def.set_current_user_state(conn, cursor, user_id,
                                          user_state_def.States.S_CHOICE_OPERATING_MODE.value)
    start_sharing_procedure(message)


def admin_item_list(message):
    user_id = message.chat.id
    queue_messages_def.clear_queue_message(conn, cursor, user_id)
    records = item_for_rent_def.get_user_item_list(cursor, user_id)
    if records:
        for row in records:
            item_id = row[0]
            item_type_id = row[1]
            item_desc = row[2]
            item_type_name = item_type_def.get_item_type_name(cursor, item_type_id)
            keyboard = types.InlineKeyboardMarkup()
            key_edit = types.InlineKeyboardButton(text='Редактировать', callback_data='edit_item_' + str(item_id))
            key_del = types.InlineKeyboardButton(text='Удалить', callback_data='del_item_' + str(item_id))
            keyboard.add(key_edit, key_del)
            # TODO сделать функцию по изменению размеров изображения
            fp = io.BytesIO(row[4])
            img = Image.open(fp)
            img.thumbnail(size=(300, 300))
            message_id = bot.send_photo(user_id, photo=img,
                                        caption='Название: '+item_type_name+'. \n' +
                                                'Характеристики: '+item_desc+'.',
                                        reply_markup=keyboard).message_id
            add_to_queue_messages(user_id, message_id, item_id)
    # TODO 3. правильно ли тут перенаправлять на главное меню или все таки
    #  устанавливать статус для редактирования вещей и перенаправлять именно
    #  сюда????


def view_all_category(message):
    user_id = message.chat.id
    del_not_actual_messages(user_id, 0)
    add_to_queue_messages(user_id, message.message_id, -1)
    record = item_type_def.get_all_type_category(cursor)
    keyboard = types.InlineKeyboardMarkup()
    for row in record:
        item_type_id = row[0]
        item_type_name = row[1]
        item_type_count = item_for_rent_def.get_count_item_for_rent_by_type(cursor, item_type_id)
        if item_type_count > 0:
            key_text = item_type_name + ' - ' + str(item_type_count)
            key_category_view = types.InlineKeyboardButton(text=key_text,
                                                           callback_data='category_view_' + str(item_type_id))
            keyboard.add(key_category_view)
    message_id = bot.send_message(message.chat.id,
                                  "Список всех существующих категорий:",
                                  reply_markup=keyboard).message_id
    add_to_queue_messages(user_id, message_id, -1)
    message_id = bot.send_message(user_id, 'Перейти в главное меню, /start').message_id
    add_to_queue_messages(user_id, message_id, -1)
    user_state_def.set_current_user_state(conn, cursor, user_id,
                                          user_state_def.States.S_CHOICE_OPERATING_MODE.value)


@bot.message_handler(func=lambda message: user_state_def.get_current_user_state(cursor, message.chat.id) ==
                     user_state_def.States.S_CHOICE_OPERATING_MODE.value)
def start_sharing_procedure(message):
    user_id = message.chat.id
    add_to_queue_messages(user_id, message.message_id, -1)
    del_not_actual_messages(user_id, 0)
    keyboard = types.InlineKeyboardMarkup()
    key_share = types.InlineKeyboardButton(text='Предложить вещь в пользование.', callback_data='share')
    keyboard.add(key_share)
    key_find = types.InlineKeyboardButton(text='Найти вещь в пользование.', callback_data='find')
    keyboard.add(key_find)
    key_view_all_category = types.InlineKeyboardButton(text='Посмотреть все категории',
                                                       callback_data='view_all_category')
    keyboard.add(key_view_all_category)
    key_admin_self = types.InlineKeyboardButton(text='Редактировать личные данные',
                                                callback_data='admin_self')
    keyboard.add(key_admin_self)
    key_admin_item_list = types.InlineKeyboardButton(text='Редактировать список своих вещей',
                                                     callback_data='admin_item_list')
    keyboard.add(key_admin_item_list)
    message_id = bot.send_message(message.chat.id, "Что вы хотите сделать?", reply_markup=keyboard).message_id
    add_to_queue_messages(user_id, message_id, -1)


@bot.message_handler(func=lambda message: user_state_def.get_current_user_state(cursor, message.chat.id) ==
                     user_state_def.States.S_SELECT_SHARING_OPERATING_MODE.value)
def share_item(message):
    user_id = message.chat.id
    message_id = bot.send_message(user_id, "Введи название вещи, которую хочешь сдавать в аренду "
                                           "(в именительном падеже, в ед. числе):").message_id
    add_to_queue_messages(user_id, message_id, -1)
    user_state_def.set_current_user_state(conn, cursor, user_id,
                                          user_state_def.States.S_SHARING_ENTER_ITEM_TYPE_FOR_ADD_DB.value)


@bot.message_handler(func=lambda message: user_state_def.get_current_user_state(cursor, message.chat.id) ==
                     user_state_def.States.S_SHARING_ENTER_ITEM_TYPE_FOR_ADD_DB.value)
def get_item_type(message):
    user_id = message.chat.id
    add_to_queue_messages(user_id, message.message_id, -1)
    item_type_name = message.text
    item_type_id = item_type_def.check_item_type(conn, cursor, item_type_name)
    item_for_rent_def.tmp_save_item_type_id_and_owner_id(conn, cursor, user_id, item_type_id)
    message_id = bot.send_message(user_id, "Напиши характеристики/параметры вещи, которые позволят другим "
                                           "людям понять, подходит ли она им или нет:").message_id
    add_to_queue_messages(user_id, message_id, -1)
    user_state_def.set_current_user_state(conn, cursor, user_id,
                                          user_state_def.States.S_SHARING_ENTER_ITEM_DESC_FOR_ADD_DB.value)


@bot.message_handler(func=lambda message: user_state_def.get_current_user_state(cursor, message.chat.id) ==
                     user_state_def.States.S_SHARING_ENTER_ITEM_DESC_FOR_ADD_DB.value)
def get_item_desc(message):
    user_id = message.chat.id
    add_to_queue_messages(user_id, message.message_id, -1)
    item_desc = message.text
    item_for_rent_def.tmp_save_item_desc(conn, cursor, user_id, item_desc)
    message_id = bot.send_message(user_id, "Пришли фото вещи (можно прислать только 1 фото):").message_id
    add_to_queue_messages(user_id, message_id, -1)
    bot.register_next_step_handler(message, get_item_photo)
    user_state_def.set_current_user_state(conn, cursor, user_id,
                                          user_state_def.States.S_SHARING_ENTER_ITEM_PHOTO_FOR_ADD_DB.value)


@bot.message_handler(func=lambda message: user_state_def.get_current_user_state(cursor, message.chat.id) ==
                     user_state_def.States.S_SHARING_ENTER_ITEM_PHOTO_FOR_ADD_DB.value)
def get_item_photo(message):
    user_id = message.chat.id
    add_to_queue_messages(user_id, message.message_id, -1)
    if message.content_type == 'photo':
        f_id = message.photo[-1].file_id
        file_info = bot.get_file(f_id)
        item_photo = bot.download_file(file_info.file_path)
        item_type_id = item_for_rent_def.tmp_get_item_for_rent(cursor, user_id)[0]
        item_desc = item_for_rent_def.tmp_get_item_for_rent(cursor, user_id)[1]
        item_for_rent_def.add_item_for_rent_db(conn, cursor, item_type_id, item_desc, user_id, item_photo)
        item_for_rent_def.tmp_del_item_for_rent(conn, cursor, user_id)
        message_id = bot.send_message(user_id, "Спасибо! Информация добавлена в базу данных").message_id
        add_to_queue_messages(user_id, message_id, -2)
        del_not_actual_notification(user_id)
        user_state_def.set_current_user_state(conn, cursor, user_id,
                                              user_state_def.States.S_CHOICE_OPERATING_MODE.value)
        start_sharing_procedure(message)
    else:
        message_id = bot.send_message(user_id, "Присланное сообщение не является изображением. "
                                               "Нужно прислать файл с фотографией").message_id
        add_to_queue_messages(user_id, message_id, -1)
        bot.register_next_step_handler(message, get_item_photo)


# Ниже все про поиск вещей в аренду
@bot.message_handler(func=lambda message: user_state_def.get_current_user_state(cursor, message.chat.id) ==
                     user_state_def.States.S_SELECT_FIND_OPERATING_MODE.value)
def find_item(message):
    user_id = message.chat.id
    add_to_queue_messages(user_id, message.message_id, -1)
    message_id = bot.send_message(user_id, "Введи название вещи (в именительном падеже, в ед. числе), "
                                           "которую хочешь найти:").message_id
    add_to_queue_messages(user_id, message_id, -1)
    user_state_def.set_current_user_state(conn, cursor, user_id,
                                          user_state_def.States.S_FIND_ENTER_ITEM_TYPE.value)


def get_small_picture(picture):
    fp = io.BytesIO(picture)
    img = Image.open(fp)
    img.thumbnail(size=(300, 300))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()


def view_item_for_rent_list(user_id, item_type_id):
    request_author_id = user_id
    item_type_name = item_type_def.get_item_type_name(cursor, item_type_id)
    records = item_for_rent_def.search_item_for_rent(cursor, item_type_id)
    if records:
        request_result_id = 0
        for row in records:
            item_id = row[0]
            item_desc = row[2]
            owner_id = row[3]
            find_request_def.add_tmp_find_request(conn, cursor, request_author_id, owner_id, request_result_id,
                                                  item_type_name, item_desc, item_id)
            keyboard = types.InlineKeyboardMarkup()
            key_text = 'Профиль владельца. Написать сообщение.'
            key_view_profile = types.InlineKeyboardButton(text=key_text, url='tg://user?id=' + str(owner_id))
            keyboard.add(key_view_profile)
            request_result_id = request_result_id + 1
            message_id = bot.send_photo(user_id, photo=get_small_picture(row[4]),
                                        caption='Название: ' + item_type_name + '. \n' +
                                                'Характеристики: ' + item_desc + '.',
                                        reply_markup=keyboard).message_id
            add_to_queue_messages(user_id, message_id, -1)
    else:
        message_id = bot.send_message(user_id, 'Такой вещи ('+item_type_name+') не найдено.').message_id
        add_to_queue_messages(user_id, message_id, -1)


@bot.message_handler(func=lambda message: user_state_def.get_current_user_state(cursor, message.chat.id) ==
                                          user_state_def.States.S_FIND_ENTER_ITEM_TYPE.value)
def print_item_for_rent_list(message):
    user_id = message.chat.id
    add_to_queue_messages(user_id, message.message_id, -1)
    request_author_id = user_id
    find_request_def.del_tmp_find_request_for_author(conn, cursor, request_author_id)
    item_type_name = message.text
    # TODO item_type_id находить по type_name внутри
    #  item_for_rent_def.search_item_for_rent
    item_type_id = item_type_def.get_item_type_id(cursor, item_type_name)
    view_item_for_rent_list(user_id, item_type_id)
    message_id = bot.send_message(user_id, 'Поиск завершен. Вы можете повторить поиск,введя название вещи.'
                                           'Для перехода в главное меню, выберите команду /start').message_id
    add_to_queue_messages(user_id, message_id, -1)


def edit_item(message, item_id):
    keyboard = types.InlineKeyboardMarkup()
    key_edit_item_type = types.InlineKeyboardButton(text='Категорию вещи',
                                                    callback_data='edit_item_type_' + str(item_id))
    keyboard.add(key_edit_item_type)
    key_edit_item_desc = types.InlineKeyboardButton(text='Описание вещи',
                                                    callback_data='edit_item_desc_' + str(item_id))
    keyboard.add(key_edit_item_desc)
    key_edit_item_photo = types.InlineKeyboardButton(text='Изменить фотографию',
                                                     callback_data='edit_item_photo_' + str(item_id))
    keyboard.add(key_edit_item_photo)
    key_edit_back = types.InlineKeyboardButton(text='Вернуться назад', callback_data='edit_back_' + str(item_id))
    keyboard.add(key_edit_back)
    photo = item_for_rent_def.get_item_photo(cursor, item_id)
    bot.edit_message_media(types.InputMedia(type='photo', media=photo), message.chat.id, message.message_id)
    bot.edit_message_caption(chat_id=message.chat.id, message_id=message.message_id,
                             caption='Выбери, что именно ты хочешь отредактировать:',
                             reply_markup=keyboard)


def edit_item_type(message, item_id):
    user_id = message.chat.id
    del_not_actual_messages(user_id, item_id)
    user_state_def.set_user_item_edit_state(conn, cursor, user_id, item_id)
    item_type_id = item_for_rent_def.get_item_type_id(cursor, item_id)
    item_type_name = item_type_def.get_item_type_name(cursor, item_type_id)
    bot.register_next_step_handler(message, get_new_item_type)
    message_id = bot.send_message(message.chat.id,
                                  "Введи название новой категории вещи.\n" +
                                  "Действующая категория: " + item_type_name).message_id
    add_to_queue_messages(user_id, message_id, -1)


def get_new_item_type(message):
    user_id = message.chat.id
    add_to_queue_messages(user_id, message.message_id, -1)
    item_id = user_state_def.get_user_item_edit_state(cursor, user_id)
    new_item_type_name = message.text
    new_item_type_id = item_type_def.check_item_type(conn, cursor, new_item_type_name)
    item_for_rent_def.set_item_type_id(conn, cursor, item_id, new_item_type_id)
    message_id = bot.send_message(user_id, 'Категория вещи обновлена').message_id
    add_to_queue_messages(user_id, message_id, -2)
    del_not_actual_notification(user_id)
    del_not_actual_messages(user_id, 0)
    user_state_def.set_current_user_state(conn, cursor, user_id,
                                          user_state_def.States.S_CHOICE_OPERATING_MODE.value)
    user_state_def.set_user_item_edit_state(conn, cursor, user_id, 0)
    start_sharing_procedure(message)


def edit_item_desc(message, item_id):
    user_id = message.chat.id
    del_not_actual_messages(user_id, item_id)
    user_state_def.set_user_item_edit_state(conn, cursor, user_id, item_id)
    item_desc = item_for_rent_def.get_item_desc(cursor, item_id)
    bot.register_next_step_handler(message, get_new_item_desc)
    message_id = bot.send_message(message.chat.id,
                                  "Введи новое описание вещи.\n" +
                                  "Действующее описание: " + item_desc).message_id
    add_to_queue_messages(user_id, message_id, -1)


def get_new_item_desc(message):
    user_id = message.chat.id
    item_id = user_state_def.get_user_item_edit_state(cursor, user_id)
    new_item_desc = message.text
    item_for_rent_def.set_item_desc(conn, cursor, item_id, new_item_desc)
    message_id = bot.send_message(user_id, 'Описание вещи обновлено.').message_id
    add_to_queue_messages(user_id, message_id, -2)
    del_not_actual_notification(user_id)
    del_not_actual_messages(user_id, 0)
    user_state_def.set_current_user_state(conn, cursor, user_id,
                                          user_state_def.States.S_CHOICE_OPERATING_MODE.value)
    user_state_def.set_user_item_edit_state(conn, cursor, user_id, 0)
    start_sharing_procedure(message)


def edit_item_photo(message, item_id):
    user_id = message.chat.id
    del_not_actual_messages(user_id, item_id)
    user_state_def.set_user_item_edit_state(conn, cursor, user_id, item_id)
    message_id = bot.send_message(user_id, "Пришли новую фотографию").message_id
    add_to_queue_messages(user_id, message_id, -1)
    bot.register_next_step_handler(message, get_new_item_photo)


def get_new_item_photo(message):
    user_id = message.chat.id
    add_to_queue_messages(user_id, message.message_id, -1)
    item_id = user_state_def.get_user_item_edit_state(cursor, user_id)
    if message.content_type == 'photo':
        f_id = message.photo[-1].file_id
        file_info = bot.get_file(f_id)
        new_item_photo = bot.download_file(file_info.file_path)
        item_for_rent_def.set_item_photo(conn, cursor, item_id, new_item_photo)
        message_id = bot.send_message(user_id, "Фотография обновлена!").message_id
        add_to_queue_messages(user_id, message_id, -2)
        del_not_actual_notification(user_id)
        del_not_actual_messages(user_id, 0)
        user_state_def.set_current_user_state(conn, cursor, user_id,
                                              user_state_def.States.S_CHOICE_OPERATING_MODE.value)
        user_state_def.set_user_item_edit_state(conn, cursor, user_id, 0)
        start_sharing_procedure(message)
    else:
        message_text = "Присланное сообщение не является изображением. Нужно прислать файл с фотографией"
        message_id = bot.send_message(user_id, message_text).message_id
        add_to_queue_messages(user_id, message_id, -1)
        bot.register_next_step_handler(message, get_new_item_photo)


def del_item(call, message, item_id):
    keyboard = types.InlineKeyboardMarkup()
    key_del_yes = types.InlineKeyboardButton(text='Да', callback_data='del_yes_' + str(item_id))
    key_del_no = types.InlineKeyboardButton(text='Нет', callback_data='del_no_' + str(item_id))
    keyboard.row(key_del_yes, key_del_no)
    photo = item_for_rent_def.get_item_photo(cursor, item_id)
    bot.edit_message_media(types.InputMedia(type='photo', media=photo), message.chat.id, message.message_id)
    bot.edit_message_caption(chat_id=message.chat.id, message_id=message.message_id,
                             caption='Точно хочешь удалить эту вещь?', reply_markup=keyboard)


def back_to_admin_item_list_menu(message, item_id):
    records = item_for_rent_def.get_user_item(cursor, item_id)
    if records:
        item_type_id = records[0]
        item_desc = records[1]
        item_type_name = item_type_def.get_item_type_name(cursor, item_type_id)
        keyboard = types.InlineKeyboardMarkup()
        key_edit = types.InlineKeyboardButton(text='Редактировать', callback_data='edit_item_' + str(item_id))
        key_del = types.InlineKeyboardButton(text='Удалить', callback_data='del_item_' + str(item_id))
        keyboard.add(key_edit, key_del)
        bot.edit_message_media(types.InputMedia(type='photo', media=get_small_picture(records[3])),
                               message.chat.id, message.message_id)
        bot.edit_message_caption(chat_id=message.chat.id,
                                 message_id=message.message_id,
                                 caption='Название: ' + item_type_name + '. \n' +'Характеристики: '+item_desc+'.',
                                 reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "share":
        share_item(call.message)
    elif call.data == "find":
        find_item(call.message)
    elif call.data == "view_all_category":
        view_all_category(call.message)
    elif call.data.find('category_view_') != -1:
        item_type_id = call.data.split('_')[2]
        user_id = call.message.chat.id
        del_not_actual_messages(user_id, 0)
        view_item_for_rent_list(user_id, item_type_id)
        message_id = bot.send_message(user_id, 'Вернутся к перечню категорий /view_all_category').message_id
        add_to_queue_messages(user_id, message_id, -1)
    elif call.data == "admin_self":
        admin_self(call.message)
    elif call.data == "admin_item_list":
        admin_item_list(call.message)
    elif call.data.find('edit_back_') != -1:
        item_id = call.data.split('_')[2]
        back_to_admin_item_list_menu(call.message, item_id)
    elif call.data.find('edit_item_desc_') != -1:
        item_id = call.data.split('_')[3]
        edit_item_desc(call.message, item_id)
    elif call.data.find('edit_item_type_') != -1:
        item_id = call.data.split('_')[3]
        edit_item_type(call.message, item_id)
    elif call.data.find('edit_item_photo_') != -1:
        item_id = call.data.split('_')[3]
        edit_item_photo(call.message, item_id)
    elif call.data.find('edit_item_') != -1:
        item_id = call.data.split('_')[2]
        edit_item(call.message, item_id)
    elif call.data.find('del_item_') != -1:
        item_id = call.data.split('_')[2]
        del_item(call, call.message, item_id)
    elif call.data.find('del_yes_') != -1:
        item_id = call.data.split('_')[2]
        item_for_rent_def.del_item(conn, cursor, item_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        user_state_def.set_current_user_state(conn, cursor, call.message.chat.id,
                                              user_state_def.States.S_CHOICE_OPERATING_MODE.value)
    elif call.data.find('del_no_') != -1:
        # TODO вынести этот блок в отдельную процедуру, возможно написать
        #  сообщение, что удаление отменено
        item_id = call.data.split('_')[2]
        back_to_admin_item_list_menu(call.message, item_id)
        user_state_def.set_current_user_state(conn, cursor, call.message.chat.id,
                                              user_state_def.States.S_CHOICE_OPERATING_MODE.value)


# asyncio.run(main())
bot.infinity_polling()

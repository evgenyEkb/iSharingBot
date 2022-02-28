from enum import Enum


class States(Enum):
    S_START = 0  # Начало нового диалога
    S_ENTER_ADDRESS = 1
    S_CHOICE_OPERATING_MODE = 2
    S_SELECT_SHARING_OPERATING_MODE = 3
    S_SHARING_ENTER_ITEM_TYPE_FOR_ADD_DB = 4
    S_SHARING_ENTER_ITEM_DESC_FOR_ADD_DB = 5
    S_SHARING_ENTER_ITEM_PHOTO_FOR_ADD_DB = 6
    S_SELECT_FIND_OPERATING_MODE = 7
    S_FIND_ENTER_ITEM_TYPE = 8
    S_FIND_PRINT_ITEM_LIST = 9
    S_FIND_SEND_MESSAGE_ITEM_OWNER = 10
    S_ADMIN_SELF = 11
    S_ADMIN_SELF_UPDATE_ADDRESS = 12
#    S_ADMIN_ITEMS_CHOICE_OPERATING_MODE = 13
    S_ADMIN_ITEMS_EDIT_ITEM_TYPE = 14
    S_ADMIN_ITEMS_EDIT_ITEM_DESC = 15
    S_ADMIN_ITEMS_EDIT_ITEM_PHOTO = 16


# Пытаемся узнать из базы «состояние» пользователя
def get_current_user_state(cursor_db, user_id):
    try:
        cursor_db.execute('SELECT user_state FROM users WHERE user_id=%s', (user_id,))
        info = cursor_db.fetchone()
        user_state = info[0]
        if user_state >= 0:
            return user_state
        else:
            return States.S_START.value
    except:
        return States.S_START.value


# Сохраняем текущее «состояние» пользователя в нашу базу
def set_current_user_state(connection, cursor_db, user_id, value):
    # TODO сделать проверку существования id пользователя
    try:
        cursor_db.execute('UPDATE users SET user_state=%s WHERE user_id=%s', (value, user_id))
        connection.commit()
        return True
    except:
        return False


def get_user_item_edit_state(cursor_db, user_id):
    try:
        cursor_db.execute('SELECT user_item_edit_state FROM users WHERE user_id=%s', (user_id,))
        records = cursor_db.fetchone()
        if records[0] >= 0:
            return records[0]
        else:
            return 0
    except:
        return 0


def set_user_item_edit_state(connection, cursor_db, user_id, value):
    try:
        cursor_db.execute('UPDATE users SET user_item_edit_state=%s WHERE user_id=%s', (value, user_id))
        connection.commit()
        return True
    except:
        return False
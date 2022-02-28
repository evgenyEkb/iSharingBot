# в модуле собраны функции для добавления, проверки и получения типа вещи,
# сдаваемой в аренду

# по названию вещи ищем id или возвращаем false если такой вещи нет в БД
def get_item_type_id(cursor_db, item_type_name):
    item_type_name = item_type_name.strip()
    item_type_name = item_type_name.lower()
    cursor_db.execute('SELECT id, item_type_name FROM item_type WHERE item_type_name = %s', (item_type_name,))
    records = cursor_db.fetchone()
    if records:
        item_type_id = records[0]
        item_type_name_db = records[1].strip()
        if item_type_name == item_type_name_db.lower():
            return item_type_id
        else:
            return 0
    else:
        return 0


def add_item_type_name_db(connection, cursor_db, item_type_name):
    item_type_name = item_type_name.strip()
    item_type_name = item_type_name.lower()
    cursor_db.execute('INSERT INTO item_type (item_type_name) VALUES (%s)', (item_type_name,))
    connection.commit()


# проверяем есть такой тип вещи в БД. Есть - сохраняем id в переменную.
# Нет - заносим в БД и возвращаем id
def check_item_type(connection, cursor_db, item_type_name):
    item_type_id = get_item_type_id(cursor_db, item_type_name)
    if item_type_id:
        return item_type_id
    else:
        add_item_type_name_db(connection, cursor_db, item_type_name)
        item_type_id = get_item_type_id(cursor_db, item_type_name)
        return item_type_id


def get_all_type_category(cursor_db):
    try:
        cursor_db.execute('SELECT id, item_type_name FROM item_type')
        records = cursor_db.fetchall()
        return records
    except:
        return False


def get_item_type_name(cursor_db, item_type_id):
    try:
        cursor_db.execute('SELECT item_type_name FROM item_type WHERE id=%s', (item_type_id,))
        records = cursor_db.fetchone()
        return records[0]
    except:
        return 'Нет категории'
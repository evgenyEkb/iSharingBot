# в модуле собраны функции для добавления, проверки и получения типа вещи, сдаваемой в аренду

# по названию вещи ищем id или возвращаем false если такой вещи нет в БД
def get_item_type_id(cursor_db, item_type_name):
    item_type_name = item_type_name.strip()
    item_type_name = item_type_name.lower()
    cursor_db.execute('SELECT id, item_type_name FROM item_type WHERE '
                      'item_type_name = ?',
                      (item_type_name,))
    records = cursor_db.fetchall()
    if records:
        for row in records:
            item_type_id = row[0]
            item_type_name_db = row[1].strip()
        if item_type_name == item_type_name_db.lower():
            return item_type_id
        else:
            return False
    else:
        return False

def add_item_type_name_db(connection, cursor_db, item_type_name):
    cursor_db.execute('INSERT INTO item_type (item_type_name) VALUES (?)', (item_type_name,))
    connection.commit()

# проверяем есть такой тип вещи в БД. Есть - сохраняем id в переменную. Нет - заносим в БД и возвращаем id
def check_item_type(connection, cursor_db, item_type_name):
    item_type_id = get_item_type_id(cursor_db, item_type_name)
    if item_type_id:
        return item_type_id
    else:
        add_item_type_name_db(connection, cursor_db, item_type_name)
        item_type_id = get_item_type_id(cursor_db, item_type_name)
        return item_type_id



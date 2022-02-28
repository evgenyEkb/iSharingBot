# в модуле собраны функции для работы с сохранением и отображением списка
# вещей сдаваемых в аренду

def add_item_for_rent_db(connection, cursor_db, item_type_id, item_desc, item_owner_id, item_photo):
    cursor_db.execute('INSERT INTO item_for_rent (item_type_id, item_desc, item_owner_id, item_photo) '
                      'VALUES (%s, %s, %s, %s)', (item_type_id, item_desc, item_owner_id, item_photo))
    connection.commit()


def search_item_for_rent(cursor_db, item_type_id):
    # TODO сделать отработку исключений и ошибок
    cursor_db.execute('SELECT id, item_type_id, item_desc, item_owner_id, item_photo '
                      'FROM item_for_rent WHERE item_type_id=%s', (item_type_id,))
    records = cursor_db.fetchall()
    if records:
        return records
    else:
        return False


def tmp_save_item_type_id_and_owner_id(connection, cursor_db, item_owner_id, item_type_id):
    try:
        cursor_db.execute('INSERT INTO tmp_item_for_rent(owner_id, item_type_id) VALUES (%s, %s)',
                          (item_owner_id, item_type_id))
        connection.commit()
    except:
       pass


def tmp_save_item_desc(connection, cursor_db, item_owner_id, item_desc):
    try:
        cursor_db.execute('UPDATE tmp_item_for_rent SET item_desc=%s WHERE owner_id=%s',
                          (item_desc, item_owner_id))
        connection.commit()
    except:
        pass


def tmp_get_item_for_rent(cursor_db, owner_id):
    try:
        cursor_db.execute('SELECT item_type_id, item_desc FROM tmp_item_for_rent WHERE owner_id = %s',
                          (owner_id,))
        records = cursor_db.fetchall()
        if records:
            for row in records:
                item_type_id = row[0]
                item_desc = row[1]
            return item_type_id, item_desc
        else:
            return False
    except:
        pass


def tmp_del_item_for_rent(connection, cursor_db, item_owner_id):
    try:
        cursor_db.execute('DELETE from tmp_item_for_rent WHERE owner_id=%s', (item_owner_id,))
        connection.commit()
    except:
        pass


def get_count_item_for_rent_by_type(cursor_db, item_type_id):
    try:
        cursor_db.execute('SELECT count(*) FROM item_for_rent WHERE item_type_id= %s', (item_type_id,))
        records = cursor_db.fetchone()
        return records[0]
    except:
        return 0


def get_user_item_list(cursor_db, owner_id):
    # TODO сделать отработку исключений и ошибок
    cursor_db.execute('SELECT id, item_type_id, item_desc, item_owner_id, item_photo FROM item_for_rent '
                      'WHERE item_owner_id = %s', (owner_id,))
    records = cursor_db.fetchall()
    if records:
        return records
    else:
        return False


def get_user_item(cursor_db, item_id):
    # TODO сделать отработку исключений и ошибок
    cursor_db.execute('SELECT item_type_id, item_desc, item_owner_id,item_photo FROM item_for_rent '
                      'WHERE id = %s', (item_id,))
    records = cursor_db.fetchone()
    if records:
        return records
    else:
        return False

def del_item(connection, cursor_db, item_id):
    # TODO сделать отработку исключений и ошибок
    try:
        cursor_db.execute('DELETE from item_for_rent WHERE id=%s', (item_id,))
        connection.commit()
    except:
        return False


def get_item_type_id(cursor_db, item_id):
    try:
        cursor_db.execute('SELECT item_type_id FROM item_for_rent WHERE id= %s', (item_id,))
        records = cursor_db.fetchone()
        return records[0]
    except:
        return False


def get_item_desc(cursor_db, item_id):
    try:
        cursor_db.execute('SELECT item_desc FROM item_for_rent WHERE id= %s', (item_id,))
        records = cursor_db.fetchone()
        return records[0]
    except:
        return False


def get_item_photo(cursor_db, item_id):
    try:
        cursor_db.execute('SELECT item_photo FROM item_for_rent WHERE id= %s', (item_id,))
        records = cursor_db.fetchone()
        return records[0]
    except:
        return False


def set_item_type_id(connection, cursor_db, item_id, value):
    try:
        cursor_db.execute('UPDATE item_for_rent SET item_type_id=%s WHERE id=%s', (value, item_id))
        connection.commit()
        return True
    except:
        return False


def set_item_desc(connection, cursor_db, item_id, value):
    try:
        cursor_db.execute('UPDATE item_for_rent SET item_desc=%s WHERE id=%s', (value, item_id))
        connection.commit()
        return True
    except:
        return False


def set_item_photo(connection, cursor_db, item_id, value):
    try:
        cursor_db.execute('UPDATE item_for_rent SET item_photo=%s WHERE id=%s', (value, item_id))
        connection.commit()
        return True
    except:
        return False
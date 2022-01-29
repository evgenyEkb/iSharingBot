# в модуле собраны функции для работы с сохранением и отображением списка вещей сдаваемых в аренду

def add_item_for_rent_db(connection, cursor_db, item_type_id, item_desc, item_owner_id, item_photo):
    cursor_db.execute('INSERT INTO item_for_rent (item_type_id, item_desc, item_owner_id, item_photo) \
                      VALUES (?, ?, ?, ?)',
                      (item_type_id, item_desc, item_owner_id, item_photo))
    connection.commit()


def search_item_for_rent(cursor_db, item_type_id):
    # TODO сделать отработку исключений и ошибок
    cursor_db.execute('SELECT id, item_type_id, item_desc, item_owner_id, item_photo FROM item_for_rent \
                        WHERE item_type_id = ?', (item_type_id,))
    records = cursor_db.fetchall()
    if records:
        return records
    else:
        return False


def tmp_save_item_type_id_and_owner_id(connection, cursor_db, item_owner_id,
                                       item_type_id):
    try:
        cursor_db.execute('INSERT INTO tmp_item_for_rent ('
                          'owner_id, item_type_id) VALUES (?, ?)',
                          (item_owner_id, item_type_id))
        connection.commit()
    except:
       pass
    finally:
        pass



def tmp_save_item_desc(connection, cursor_db, item_owner_id, item_desc):
    try:
        cursor_db.execute('UPDATE tmp_item_for_rent SET item_desc=? '
                          'WHERE owner_id=?', (item_desc, item_owner_id))
        connection.commit()
    except:
        pass
    finally:
        pass



def tmp_get_item_for_rent(cursor_db, owner_id):
    try:
        cursor_db.execute('SELECT item_type_id, item_desc FROM '
                          'tmp_item_for_rent WHERE owner_id = ?',
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
    finally:
        pass


def tmp_del_item_for_rent(connection, cursor_db, item_owner_id):
    try:
        cursor_db.execute('DELETE from tmp_item_for_rent WHERE owner_id=?',
                          (item_owner_id,))
        connection.commit()
    except:
        pass
    finally:
        pass


def get_count_item_for_rent_by_type(cursor_db, item_type_id):
    try:
        cursor_db.execute('SELECT count(*) FROM item_for_rent WHERE '
                          'item_type_id= ?',
                          (item_type_id,))
        records = cursor_db.fetchone()
        return records[0]
    except:
        return 0
    finally:
        pass
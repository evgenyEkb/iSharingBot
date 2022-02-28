def get_queue_message_by_owner_id(cursor_db, owner_id, item_id):
    if item_id == 0:
        sql = 'SELECT message_id FROM messages_queue WHERE (owner_id = %s) and (owner_id <> -2)'
        cursor_db.execute(sql, (owner_id,))
    elif item_id == -2:
        sql = 'SELECT message_id FROM messages_queue WHERE (owner_id = %s) and (item_id = %s)'
        cursor_db.execute(sql, (owner_id, -2,))
    else:
        sql = 'SELECT message_id FROM messages_queue WHERE (owner_id = %s) and (item_id <> %s)'
        cursor_db.execute(sql, (owner_id, item_id,))
    try:
        records = cursor_db.fetchall()
        return records
    except:
        return False


def add_item_in_queue_message(connection, cursor_db, owner_id, message_id, item_id):
    try:
        cursor_db.execute('INSERT INTO messages_queue (owner_id, message_id, item_id) VALUES (%s, %s, %s)',
                          (owner_id, message_id, item_id))
        connection.commit()
        return True
    except:
        return False


def clear_queue_message(connection, cursor_db, owner_id):
    try:
        cursor_db.execute('DELETE from messages_queue WHERE owner_id=%s AND item_id <> -1', (owner_id,))
        connection.commit()
        return True
    except:
        return False


def del_queue_message_by_id(connection, cursor_db, message_id):
    try:
        cursor_db.execute('DELETE from messages_queue WHERE message_id=%s', (message_id,))
        connection.commit()
        return True
    except:
        return False


def check_message_in_queue(cursor_db, message_id):
    try:
        cursor_db.execute('SELECT * from messages_queue WHERE message_id=%s', (message_id,))
        records = cursor_db.fetchall()
        if records:
            return True
        else:
            return False
    except:
        return False
def add_tmp_find_request(connection, cursor_db, request_author_id, owner_id, request_result_id,
                         item_type_name, item_desc, item_id):
    try:
        cursor_db.execute('INSERT INTO tmp_find_request '
                          '(request_author_id, owner_id, request_result_id, item_type_name, item_desc, item_id) '
                          'VALUES (%s, %s, %s, %s, %s, %s)',
                          (request_author_id, owner_id, request_result_id, item_type_name, item_desc, item_id))
        connection.commit()
    except:
       pass


def del_tmp_find_request_for_author(connection, cursor_db, request_author_id):
    cursor_db.execute('DELETE from tmp_find_request WHERE request_author_id=%s', (request_author_id,))
    connection.commit()


def get_tmp_find_result_record(cursor_db, request_result_id):
    cursor_db.execute('SELECT request_author_id, owner_id, item_type_name, item_desc, item_id '
                      'FROM tmp_find_request WHERE request_result_id = %s', (request_result_id,))
    records = cursor_db.fetchone()
    if records:
        return records
    else:
        return False
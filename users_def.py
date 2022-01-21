# В данном модуле собраны функции, связанные с регистрацией, проверкой, валидацией и получением данных о пользователе

# user - список с данными пользователя, index:
# 0 - user_id
# 1 - user_first_name
# 2 - user_last_name
# 3 - user_data
# 4 - user_date_registration

def check_user_registration(cursor_db, user_id):
    info = cursor_db.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    if info.fetchone():
        return True
    else:
        return False


def check_user_data(user_id, user_first_name, user_last_name, user_data, user_date_registration):
    # TODO в дальнейшем нужно так же проверять строки с пробелами и опмечать их как пустые или us_name = us_id
    if not user_first_name:
        user_first_name = "-"
    if not user_last_name:
        user_last_name = "-"
    if user_id and user_first_name and user_last_name and user_data and user_date_registration:
        return [user_id, user_first_name, user_last_name, user_data, user_date_registration]
    else:
        return False


def get_user_data_from_db(cursor_db, user, user_id):
    if not user:
        cursor_db.execute(
                'SELECT user_first_name, user_last_name, user_data, user_date_registration, user_address FROM users \
                WHERE user_id = ?', (user_id,))
        records = cursor_db.fetchall()
        for row in records:
            user = [user_id, row[0], row[1], row[2], row[3]]
        return user
    else:
        if user[0] == user_id:
            return user
        else:
            cursor_db.execute('SELECT user_first_name, user_last_name, user_data, user_date_registration, \
                               user_address FROM users WHERE user_id = ?', (user_id,))
            records = cursor_db.fetchall()
            for row in records:
                user = [user_id, row[0], row[1], row[2], row[3]]
            return user


def registration_user_in_db(connection, cursor_db, user_id, user_first_name, user_last_name, user_data,
                            user_date_registration, user_cities_id, user_address):
    cursor_db.execute('INSERT INTO users (user_id, user_first_name, user_last_name, user_data, user_date_registration, \
    user_cities_id, user_address) VALUES (?,?,?,?,?,?,?)', (user_id, user_first_name, user_last_name, user_data,
                                                            user_date_registration, user_cities_id, user_address))
    connection.commit()

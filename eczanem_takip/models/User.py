import MySQLdb

class User:
    def __init__(self, id, name, surname, username, email, password):
        self.id = id
        self.name = name
        self.surname = surname
        self.username = username
        self.email = email
        self.password = password

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'surname': self.surname,
            'username': self.username,
            'email': self.email
        }

    @staticmethod
    def login(connection, usernameoremail, password):
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE (username = %s OR email = %s) AND password = %s',
                       (usernameoremail, usernameoremail, password))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return User(**row)
        return None

    @staticmethod
    def get_all(connection):
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM user")
        rows = cursor.fetchall()
        cursor.close()
        return [User(**row) for row in rows]

    @staticmethod
    def get_by_id(connection, user_id):
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM user WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return User(**row)
        return None

    @staticmethod
    def get_by_username(connection, username):
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return User(**row)
        return None

    @staticmethod
    def get_by_email(connection, email):
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return User(**row)
        return None

    @staticmethod
    def add(connection, user):
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO user (name, surname, username, email, password) 
            VALUES (%s, %s, %s, %s, %s)
        """, (user.name, user.surname, user.username, user.email, user.password))
        connection.commit()
        cursor.close()

    @staticmethod
    def update(connection, user):
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE user SET name = %s, surname = %s, username = %s, email = %s, password = %s
            WHERE id = %s
        """, (user.name, user.surname, user.username, user.email, user.password, user.id))
        connection.commit()
        cursor.close()

    @staticmethod
    def delete(connection, user_id):
        cursor = connection.cursor()
        cursor.execute("DELETE FROM user WHERE id = %s", (user_id,))
        connection.commit()
        cursor.close()

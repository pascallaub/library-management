import sqlite3
import getpass
import hashlib

def userdb_connection():
    return sqlite3.connect("Database/userdb.db")

def bookdb_connection():
    return sqlite3.connect("Database/bookdb.db")

def permissiondb_connection():
    return sqlite3.connect("Database/rbac.db")

def create_database_tables():
    userconn = userdb_connection()
    bookconn = bookdb_connection()
    user_cursor = userconn.cursor()
    book_cursor = bookconn.cursor()

    user_cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL,
                            email TEXT NOT NULL,
                            password BLOB NOT NULL,
                            register_date TEXT DEFAULT CURRENT_TIMESTAMP,
                            role_id INTEGER
                            )
                        ''')
    
    book_cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            author TEXT NOT NULL,
                            genre TEXT NOT NULL,
                            status TEXT NOT NULL,
                            lent_to TEXT
                            )
                        ''')
        
    userconn.commit()
    bookconn.commit()
    userconn.close()
    bookconn.close()

def add_book():
    bookconn = bookdb_connection()
    book_cursor = bookconn.cursor()

    choice1 = input("Möchtest du ein Buch hinzufügen? j/n: ").lower()
    if choice1 == 'j':
        title = input("Titel des Buches: ")
        author = input("Autor: ")
        genre = input("Genre: ")
        status = input("Status (verfügbar/ausgeliehen): ").lower()
        if status == 'ausgeliehen':
            lent_to = input("Ausgeliehen an: ")
        else:
            None

    book_cursor.execute("INSERT INTO books (title, author, genre, status, lent_to) VALUES (?,?,?,?,?)", (title, author, genre, status, lent_to))
    bookconn.commit()
    again = input("Buch erfolgreich hinzugefügt! Möchtest du ein weiteres Buch hinzufügen? j/n: ").lower()
    if again == 'j':
        add_book()
    else:
        main_menu()
    bookconn.close()

def register():
    userconn = userdb_connection()
    user_cursor = userconn.cursor()

    user_cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL,
                            email TEXT NOT NULL,
                            password BLOB NOT NULL,
                            register_date TEXT DEFAULT CURRENT_TIMESTAMP,
                            role_id INTEGER
                            )
                        ''')
    user_cursor.execute('''CREATE TABLE IF NOT EXISTS roles (
                            id INTEGER PRIMARY KEY,
                            role_name TEXT UNIQUE
                            )
                        ''')
    user_cursor.execute("INSERT INTO roles (role_name) VALUES ('admin'), ('user')")
    roles()

    print("Willkommen! Du befindest dich im Registrierungsprozess!")
    username = input("Benutzername: ")
    user_cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    result = user_cursor.fetchone()
    if result:
        print("Benutzername bereits vergeben!")
        userconn.close()
        register()
        return
    email = input("Email-Adresse: ")
    password = getpass.getpass("Passwort: ")
    password_check = getpass.getpass("Passwort wiederholen: ")

    if password == password_check:
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            b'some_salt',
            100000
        )
        user_cursor.execute("INSERT INTO users (username, email, password) VALUES (?,?,?)", (username, email, password_hash))
        print("Registrierung erfolgreich!")
    else:
        print("Passwörter stimmen nicht überein!")
        userconn.close()
        register()

    userconn.commit()
    userconn.close()
    main_menu()

def rent_book():
    bookconn = bookdb_connection()
    book_cursor = bookconn.cursor()

    search = input("Möchtest du nach dem Autor(1) oder Titel(2) suchen: ")
    if search == '1':
        author = input("Gib den Namen des/der Autor/in ein: ")
        book_cursor.execute("SELECT * FROM books WHERE author = ?", ('%' + author + '%',))
    elif search == '2':
        title = input("Gib den Titel des Buches ein: ")
        book_cursor.execute("SELECT * FROM books WHERE title = ?", ('%' + title + '%',))
    else:
        print("Ungültige Eingabe!")
        return

    result = book_cursor.fetchall()

    if not result:
        print("Keine Bücher gefunden!")
    else:
        for book in result:
            print(f"ID: {book[0]}, Titel: {book[1]}, Autor: {book[2]}, Verfügbarkeit: {book[3]}")
        
        try:
            book_id = int(input("Gib die ID des Buches ein: "))
            selected_book = next((book for book in result if book[0] == book_id), None)
            if selected_book:
                if selected_book[3] == 'verfügbar':
                    book_cursor.execute("UPDATE books SET status = ? WHERE id = ?", ('ausgeliehen', book_id))
                    bookconn.commit()
                    print(f"Das Buch {selected_book[1]} wurde ausgeliehen")
                else:
                    print("Das Buch ist nicht verfügbar!")
            else:
                print("Ungültige Buch-ID!")
        except ValueError:
            print("Bitte gib eine gültige Buch-ID ein!")
    
    bookconn.close()


def return_book():
    book_con = bookdb_connection()
    cursor_book = book_con.cursor()

    author = input("Gib den Autor ein: ")
    title = input("Gib den Titel ein: ")

    cursor_book.execute("SELECT * FROM books WHERE author = ? AND title = ?", (author, title))
    result = cursor_book.fetchone()
    
    if not result:
        print("Keine Bücher gefunden!")
    else:
        for book in result:
            print(f"ID: {book[0]}, Titel: {book[1]}, Autor: {book[2]}")
        try:
            book_id = int(input("Gib die ID ein: "))
            cursor_book.execute("UPDATE books SET status = ? WHERE id = ?", ('verfügbar', book_id))
            book_con.commit()
        except ValueError:
            print("Falsche Eingabe!")

    book_con.close()


def delete_book():
    book_con = bookdb_connection()
    cursor_book = book_con.cursor()

    search = input("Möchtest du nach dem Autor(1) oder Titel(2) suchen: ")
    if search == '1':
        author = input("Gib den Namen des/der Autor/in ein: ")
        cursor_book.execute("SELECT * FROM books WHERE author = ?", ('%' + author + '%',))
    elif search == '2':
        title = input("Gib den Titel des Buches ein: ")
        cursor_book.execute("SELECT * FROM books WHERE title = ?", ('%' + title + '%',))
    else:
        print("Ungültige Eingabe!")
        return

    result = cursor_book.fetchall()

    if not result:
        print("Keine Bücher gefunden!")
    else:
        for book in result:
            print(f"ID: {book[0]}, Titel: {book[1]}, Autor: {book[2]}, Verfügbarkeit: {book[3]}")
        try:
            book_id = int(input("Gib die ID ein: "))
            cursor_book.execute("DELETE FROM books WHERE id = ?", (book_id,))
            book_con.commit()
        except ValueError:
            print("Falsche Eingabe!")
    
    book_con.close()


def assign_role(username, role):
    permissionconn = permissiondb_connection()
    cursor_per = permissionconn.cursor()

    cursor_per.execute('''CREATE TABLE IF NOT EXISTS user_roles (
                            username TEXT NOT NULL,
                            role_name TEXT NOT NULL,
                            FOREIGN KEY (role_name) REFERENCES roles(role_name)
                            )
                       ''')
    
    cursor_per.execute("INSERT INTO user_roles (username, role_name) VALUES (?,?)", (username, role))
    permissionconn.commit()
    permissionconn.close()

def roles():
    permissioncon = permissiondb_connection()
    cursor_per = permissioncon.cursor()

    cursor_per.execute('''CREATE TABLE IF NOT EXISTS permissions(
                   id INTEGER PRIMARY KEY,
                   permission_name TEXT UNIQUE
                   )
                ''')
    
    cursor_per.execute('''CREATE TABLE IF NOT EXISTS roles (
                   id INTEGER PRIMARY KEY,
                   role_name TEXT UNIQUE
                   )
                ''')
    
    cursor_per.execute("INSERT INTO roles (role_name) VALUES ('admin'), ('user')")
    
    cursor_per.execute("INSERT INTO permissions (permission_name) VALUES ('create'), ('read'), ('update'), ('delete')")

    cursor_per.execute('''CREATE TABLE IF NOT EXISTS role_permissions (
                   role_id INTEGER,
                   permission_id INTEGER,
                   FOREIGN KEY(role_id) REFERENCES roles(id),
                   FOREIGN KEY(permission_id) REFERENCES permissions(id))''')

    cursor_per.execute('''INSERT INTO role_permissions (role_id, permission_id)
                   VALUES ((SELECT id FROM roles WHERE role_name = 'admin'), (SELECT id FROM permissions WHERE permission_name = 'create')),
                          ((SELECT id FROM roles WHERE role_name = 'admin'), (SELECT id FROM permissions WHERE permission_name = 'read')),
                           ((SELECT id FROM roles WHERE role_name = 'admin'), (SElECT id FROM permissions WHERE permission_name = 'update')),
                            ((SELECT id FROM roles WHERE role_name = 'admin'), (SELECT id FROM permissions WHERE permission_name = 'delete'))
                    ''')
    
    cursor_per.execute('''INSERT INTO role_permissions (role_id, permission_id)
                       VALUES ((SELECT id FROM roles WHERE role_name = 'user'), (SELECT id FROM permissions WHERE permission_name = 'read')),
                                ((SELECT id FROM roles WHERE role_name = 'user'), (SELECT id FROM permissions WHERE permission_name = 'update'))
                       ''')
    
    permissioncon.commit()
    permissioncon.close()

def check_permission(username, action):
    user_con = userdb_connection()
    perm_con = permissiondb_connection()
    user_cursor = user_con.cursor()
    perm_cursor = perm_con.cursor()

    user_cursor.execute('''
            SELECT r.role_name
            FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE u.username = ?
            ''', (username,))
    
    role = user_cursor.fetchone()

    if role is None:
        user_con.close()
        raise PermissionDenied("Keine Berechtigung!")
    main_menu()

    return True

class PermissionDenied(Exception):
    pass



def current_user(username):
    user_conn = userdb_connection()
    cursor_user = user_conn.cursor()

    cursor_user.execute("SELECT username FROM users WHERE username = ?", (username,))
    result = current_user.fetchone()

    if result:
        return result[0]
    else:
        return None
    
    current_username = result[0]

    user_conn.close()


def login_menu():
    userconn = userdb_connection()
    user_cursor = userconn.cursor()

    choice = input("Willst du dich anmelden(1) oder registrieren(2): ")
    try:
        if choice == '1':
            username = input("Benutzername: ")
            password = getpass.getpass("Passwort: ")
            user_cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
            result = user_cursor.fetchone()
            if result:
                stored_password_hash = result[0]
                password_hash = hashlib.pbkdf2_hmac(
                    'sha256',
                    password.encode('utf-8'),
                    b'some_salt',
                    100000
                )
                if stored_password_hash == password_hash:
                    main_menu()
                else:
                    print("Falsches Passwort!")
                    login_menu()
        elif choice == '2':
            register()
    except ValueError:
        print("Gib eine Zahl ein!")


def main_menu():
    current_username = current_user('username')
    while True:
        try:
            choice = input("Bücher ausleihen (2)\nBücher zurückgeben (3)\nBücher hinzufügen (4)\nBücher löschen (5)\nBeenden (6)\nGib eine Zahl ein: ")

            if choice == '1':
                check_permission(current_user, 'update')
                rent_book()
            elif choice == '2':
                check_permission(current_user, 'update')
                return_book()
            elif choice == '3':
                check_permission(current_user, 'create')
                add_book()
            elif choice == '4':
                check_permission(current_user, 'delete')
                delete_book()
            elif choice == '5':
                quit()
            else:
                print("Falsche Eingabe!")
        except ValueError:
            print("Falsche Eingabe!")

if __name__ == '__main__':
    create_database_tables()
    login_menu()
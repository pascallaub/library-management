import sqlite3
import getpass
import hashlib

def userdb_connection():
    return sqlite3.connect("Database/userdb.db")

def bookdb_connection():
    return sqlite3.connect("Database/bookdb.db")

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
                            register_date TEXT DEFAULT CURRENT_TIMESTAMP
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
        

def main_menu():
    while True:
        choice = input("Registrieren (1)\nBücher ausleihen (2)\nBücher zurückgeben (3)\nBücher hinzufügen (4)\nBücher löschen (5)\nBeenden (6)\nGib eine Zahl ein: ")

        if choice == '1':
            register()
        elif choice == '2':
            rent_book()
        elif choice == '3':
            return_book()
        elif choice == '4':
            add_book()
        elif choice == '5':
            delete_book()
        elif choice == '6':
            quit()
        else:
            print("Falsche Eingabe!")

if __name__ == '__main__':
    create_database_tables()
    main_menu()
import sqlite3
import getpass
import hashlib
import tkinter as tk
from tkinter import messagebox, simpledialog

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

def add_book(title, author, genre, status, lent_to):
    bookconn = bookdb_connection()
    book_cursor = bookconn.cursor()

    book_cursor.execute("INSERT INTO books (title, author, genre, status, lent_to) VALUES (?,?,?,?,?)", (title, author, genre, status, lent_to))
    bookconn.commit()
    bookconn.close()
    again = input("Buch erfolgreich hinzugefügt! Möchtest du ein weiteres Buch hinzufügen? j/n: ").lower()
    messagebox.showinfo("Erfolg!", "Buch hinzugefügt!")

def register_user(username, email, password):
    userconn = userdb_connection()
    user_cursor = userconn.cursor()
    password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            b'some_salt',
            100000
        )
    user_cursor.execute("INSERT INTO users (username, email, password) VALUES (?,?,?)", (username, email, password_hash))
    print("Registrierung erfolgreich!")
    userconn.commit()
    userconn.close()
    messagebox.showinfo("Erfolg!", "Registrierung erfolgreich!")


def rent_book():
    bookconn = bookdb_connection()
    book_cursor = bookconn.cursor()

    search = input("Möchtest du nach dem Autor(1) oder Titel(2) suchen: ")
    if search == '1':
        author = simpledialog.askstring("Buchausleihe", "Gib den Namen des/der Autor/in ein: ")
        book_cursor.execute("SELECT * FROM books WHERE author = ?", ('%' + author + '%',))
    elif search == '2':
        title = simpledialog.askstring("Gib den Titel des Buches ein: ")
        book_cursor.execute("SELECT * FROM books WHERE title = ?", ('%' + title + '%',))
    else:
        messagebox.showerror("Ungültige Eingabe!")
        return

    result = book_cursor.fetchall()

    if not result:
        print("Keine Bücher gefunden!")
    else:
        books_list = "\n".join([f"ID: {book[0]}, Titel: {book[1]}, Autor: {book[2]}, Verfügbarkeit: {book[3]}" for book in result])
        book_id = simpledialog.askinteger("Buchausleihe", f"Gefundene Bücher:\n{books_list}\nGib die ID des Buches ein: ")
        
        selected_book = next((book for book in result if book[0] == book_id), None)
        if selected_book:
            if selected_book[3] == 'verfügbar':
                book_cursor.execute("UPDATE books SET status = ? WHERE id = ?", ('ausgeliehen', book_id))
                bookconn.commit()
                messagebox.showinfo("Info", f"Das Buch {selected_book[1]} wurde ausgeliehen")
            else:
                messagebox.showerror("Info", "Das Buch ist nicht verfügbar!")
        else:
            messagebox.showerror("Ungültige Buch-ID!")


def return_book():
    book_con = bookdb_connection()
    cursor_book = book_con.cursor()

    author = simpledialog.askstring("Buchrückgabe", "Gib den Autor ein: ")
    title = simpledialog.askstring("Buchrückgabe", "Gib den Titel ein: ")

    cursor_book.execute("SELECT * FROM books WHERE author = ? AND title = ?", (author, title))
    result = cursor_book.fetchone()
    
    if not result:
        messagebox.showinfo("Keine Bücher gefunden!")
    else:
        book_id = simpledialog.askinteger("Buchrückgabe", f"ID: {result[0]}, Titel: {result[1]}, Autor: {result[2]}\nGib die ID ein: ")
        cursor_book.execute("UPDATE books SET status = ? WHERE id = ?", ('verfügbar', book_id))
        book_con.commit()
    book_con.close()


def delete_book():
    book_con = bookdb_connection()
    cursor_book = book_con.cursor()

    search = simpledialog.askstring("Buch löschen", "Möchtest du nach dem Autor(1) oder Titel(2) suchen: ")
    if search == '1':
        author = simpledialog.askstring("Buch löschen", "Gib den Namen des/der Autor/in ein: ")
        cursor_book.execute("SELECT * FROM books WHERE author = ?", ('%' + author + '%',))
    elif search == '2':
        title = simpledialog.askstring("Buch löschen", "Gib den Titel des Buches ein: ")
        cursor_book.execute("SELECT * FROM books WHERE title = ?", ('%' + title + '%',))
    else:
        messagebox.showerror("Ungültige Eingabe!")
        return

    result = cursor_book.fetchall()

    if not result:
        messagebox.showerror("Keine Bücher gefunden!")
    else:
        books_list = "\n".join([f"ID: {book[0]}, Titel: {book[1]}, Autor: {book[2]}, Verfügbarkeit: {book[3]}" for book in result])
        book_id = simpledialog.askinteger("Buch löschen", f"Gefundene Bücher:\n{books_list}\nGib die ID ein: ")
        cursor_book.execute("DELETE FROM books WHERE id = ?", (book_id,))
        book_con.commit()

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


def login_user(username, password):
    userconn = userdb_connection()
    user_cursor = userconn.cursor()

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
            messagebox.showinfo("Erfolg", "Login erfolgreich!")
            return True
        else:
            messagebox.showerror("Fehler", "Falsches Passwort!")
            return False


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

def create_gui():
    root = tk.Tk()
    root.title("Bücherverwaltung")

    def open_register():
        register_window = tk.Toplevel(root)
        register_window.title("Registrierung")

        tk.Label(register_window, text="Benutzername:").pack()
        username_entry = tk.Entry(register_window)
        username_entry.pack()

        tk.Label(register_window, text="Email:").pack()
        email_entry = tk.Entry(register_window)
        email_entry.pack()

        tk.Label(register_window, text="Passwort:").pack()
        password_entry = tk.Entry(register_window, show='*')
        password_entry.pack()

        def register():
            username = username_entry.get()
            email = email_entry.get()
            password = password_entry.get()
            register_user(username, email, password)
            register_window.destroy()
        
        tk.Button(register_window, text="Registrieren", command=register).pack()

    def open_login():
        login_window = tk.Toplevel(root)
        login_window.title("login")

        tk.Label(login_window, text="Benutzername:").pack()
        username_entry = tk.Entry(login_window)
        username_entry.pack()

        tk.Label(login_window, text="Passwort:").pack()
        password_entry = tk.Entry(login_window, show='*')
        password_entry.pack()

        def login():
            username = username_entry.get()
            password = password_entry.get()
            if login_user(username, password):
                login_window.destroy()
                main_menu()

        tk.Button(login_window, text="Anmelden", command=login).pack()


    # Hauptmenü
    def main_menu():
        menu_window = tk.Toplevel(root)
        menu_window.title("Hauptmenü")

        def add_book_prompt():
            title = simpledialog.askstring("Buch hinzufügen", "Titel des Buches:")
            author = simpledialog.askstring("Buch hinzufügen", "Autor:")
            genre = simpledialog.askstring("Buch hinzufügen", "Genre:")
            status = simpledialog.askstring("Buch hinzufügen", "Status (verfügbar/ausgeliehen):")
            lent_to = simpledialog.askstring("Buch hinzufügen", "Ausgeliehen an (falls ausgeborgt):")
            add_book(title, author, genre, status, lent_to)

        def rent_book_prompt():
            book_id = simpledialog.askinteger("Buch ausleihen", "Gib die ID des Buches ein:")
            rent_book(book_id)

        def return_book_prompt():
            book_id = simpledialog.askinteger("Buch zurückgeben", "Gib die ID des Buches ein:")
            return_book(book_id)

        tk.Button(menu_window, text="Buch hinzufügen", command=add_book_prompt).pack(pady=10)
        tk.Button(menu_window, text="Buch ausleihen", command=rent_book_prompt).pack(pady=10)
        tk.Button(menu_window, text="Buch zurückgeben", command=return_book_prompt).pack(pady=10)
        tk.Button(menu_window, text="Beenden", command=menu_window.destroy).pack(pady=10)

    # Buttons für Login und Registrierung
    tk.Button(root, text="Registrieren", command=open_register).pack(pady=10)
    tk.Button(root, text="Anmelden", command=open_login).pack(pady=10)

    root.mainloop()

if __name__ == '__main__':
    create_database_tables()
    create_gui()
from connect import get_connection
import csv

conn = get_connection()
cur = conn.cursor()

def work():
    print("Вы в телефонной книге, выберите действие:")
    print("1) вставить данные из csv файла")
    print("2) добавить нового пользователя(имя, номер)")
    print("3) обновить имя или номер контакта")
    print("4) вывести пользователей с фильтром по имени(А-Я) или по префиксу телефона")
    print("5) удалить по имени или телефону")
    print("6) выйти из программы")
    choise = int(input("Введите цифру: "))
    
    
    if choise == 1:
        imprt()
    elif choise == 2:
        new_per()
    elif choise == 3:
        update_kon()
    elif choise == 4:
        sorting()
    elif choise == 5:
        deleting()
    elif choise == 6:
        exit()
    
    
def imprt():
    with open ("contacts.csv", "r", encoding = "utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        
        for row in reader:
            cur.execute("INSERT INTO contacts(name, phone_num) VALUES (%s, %s)", 
            (row[0], row[1])
                        )
            
    conn.commit()
    print("данные успешно загруженны!!!!!\n\n\n\n\n\n")
    
def new_per():
    name = input("введите имя: ")
    surname = input("введите номер(+X XXX XXX XXXX): ")
    cur.execute("INSERT INTO contacts(name, phone_num) VALUES(%s, %s)", (name, surname))
    conn.commit()
    print("Ti dobavil polzovatelya\n\n\n\n\n\n")

def update_kon():
    id = input("id контакта который хочешь обновить: ")
    vib = int(input("выбери 1 если хочешь поменять только имя, 2 если номер, и 3 если все сразу: "))
    if vib == 1:
        name = input("напиши имя: ")
        cur.execute('''UPDATE contacts 
                    SET name = %s
                    where id = %s''', (name, id))
        conn.commit()
        print("ti vse obnovil")
    elif vib == 2:
        nom = input("напиши номер: ")
        cur.execute('''UPDATE contacts 
                    SET phone_num = %s
                    where id = %s''', (nom, id))
        conn.commit()
        print("ti vse obnovil")
    elif vib == 3:
        name = input("напиши имя: ")
        nom = input("напиши номер: ")
        cur.execute('''UPDATE contacts 
                    SET name = %s,
                        phone_num = %s
                    where id = %s''', (name, nom, id))
        conn.commit()
        print("ti vse obnovil")
        
def sorting():
    numm = int(input("Если хочешь сортировать по имени, нажми 1, если по префиксу, нажми 2: "))

    if numm == 1:
        cur.execute("""
            SELECT name, phone_num
            FROM contacts
            ORDER BY name ASC, phone_num ASC
        """)

        rows = cur.fetchall()

        for row in rows:
            print(row[0], row[1])

    elif numm == 2:
        cur.execute("""
            SELECT name, phone_num
            FROM contacts
            ORDER BY 
                name ASC,
                substring(phone_num FROM 1 FOR 3) ASC
        """)

        rows = cur.fetchall()

        for row in rows:
            print(row[0], row[1])

def deleting():
    print("\nЧто хочешь удалить?")
    print("1) по имени")
    print("2) по номеру телефона")

    choice = input("Выбор: ")

    if choice == "1":
        name = input("Введите имя: ")

        cur.execute("""
            DELETE FROM contacts
            WHERE name = %s
        """, (name,))

        conn.commit()
        print("Контакт удалён по имени")

    elif choice == "2":
        phone = input("Введите номер телефона: ")

        cur.execute("""
            DELETE FROM contacts
            WHERE phone_num = %s
        """, (phone,))

        conn.commit()
        print("Контакт удалён по номеру")
        
if __name__ == "__main__":
    while True:
        work()
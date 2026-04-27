from connect import get_connection
import csv
import json

conn = get_connection()
cur = conn.cursor()

def work():
    print("\n1) вставить данные из csv файла")
    print("2) добавить нового пользователя")
    print("3) обновить контакт")
    print("4) вывод с сортировкой")
    print("5) удалить по имени или телефону")
    print("6) поиск (имя/email/телефон)")
    print("7) фильтр по группе")
    print("8) поиск по email")
    print("9) постраничный просмотр")
    print("10) добавить телефон к контакту")
    print("11) переместить в группу")
    print("12) экспорт в JSON")
    print("13) импорт из JSON")
    print("0) выйти")
    choice = input("Введите цифру: ")

    if choice == "1": imprt()
    elif choice == "2": new_per()
    elif choice == "3": update_kon()
    elif choice == "4": sorting()
    elif choice == "5": deleting()
    elif choice == "6": search()
    elif choice == "7": filter_group()
    elif choice == "8": search_email()
    elif choice == "9": paginate()
    elif choice == "10": add_phone()
    elif choice == "11": move_group()
    elif choice == "12": export_json()
    elif choice == "13": import_json()
    elif choice == "0": exit()

def imprt():
    with open("contacts.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            group_id = None
            if row.get("group"):
                cur.execute("SELECT id FROM groups WHERE name = %s", (row["group"],))
                group_id = cur.fetchone()[0]
            cur.execute("INSERT INTO contacts(name, email, birthday, group_id) VALUES (%s, %s, %s, %s) RETURNING id",
                        (row["name"], row.get("email"), row.get("birthday") or None, group_id))
            cid = cur.fetchone()[0]
            if row.get("phone"):
                cur.execute("INSERT INTO phones(contact_id, phone, type) VALUES (%s, %s, %s)",
                            (cid, row["phone"], row.get("phone_type") or "mobile"))
    conn.commit()
    print("данные успешно загружены")

def new_per():
    name = input("введите имя: ")
    email = input("email: ") or None
    birthday = input("день рождения ГГГГ-ММ-ДД: ") or None
    group_name = input("группа Family/Work/Friend/Other: ")
    group_id = None
    if group_name:
        cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
        group_id = cur.fetchone()[0]
    cur.execute("INSERT INTO contacts(name, email, birthday, group_id) VALUES(%s, %s, %s, %s) RETURNING id",
                (name, email, birthday, group_id))
    cid = cur.fetchone()[0]
    phone = input("телефон: ")
    if phone:
        p_type = input("тип home/work/mobile: ") or "mobile"
        cur.execute("INSERT INTO phones(contact_id, phone, type) VALUES(%s, %s, %s)", (cid, phone, p_type))
    conn.commit()
    print("пользователь добавлен")

def update_kon():
    id = input("id контакта: ")
    vib = int(input("1-имя 2-телефон 3-email 4-день рождения: "))
    if vib == 1:
        name = input("новое имя: ")
        cur.execute("UPDATE contacts SET name=%s WHERE id=%s", (name, id))
    elif vib == 2:
        phone = input("новый номер: ")
        p_type = input("тип home/work/mobile: ") or "mobile"
        cur.execute("INSERT INTO phones(contact_id, phone, type) VALUES(%s, %s, %s)", (id, phone, p_type))
    elif vib == 3:
        email = input("новый email: ")
        cur.execute("UPDATE contacts SET email=%s WHERE id=%s", (email, id))
    elif vib == 4:
        bd = input("день рождения ГГГГ-ММ-ДД: ")
        cur.execute("UPDATE contacts SET birthday=%s WHERE id=%s", (bd, id))
    conn.commit()
    print("обновлено")

def sorting():
    print("1-имя 2-день рождения 3-дата добавления")
    ch = input("выбор: ")
    order = {"1": "c.name", "2": "c.birthday", "3": "c.created_at"}.get(ch, "c.name")
    cur.execute(f"""
        SELECT c.id, c.name, c.email, c.birthday, g.name, ph.phone, ph.type
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        LEFT JOIN phones ph ON ph.contact_id = c.id
        ORDER BY {order}
    """)
    for row in cur.fetchall():
        print(row)

def deleting():
    print("1) по имени  2) по номеру телефона")
    choice = input("Выбор: ")
    if choice == "1":
        name = input("Введите имя: ")
        cur.execute("DELETE FROM contacts WHERE name = %s", (name,))
    elif choice == "2":
        phone = input("Введите номер телефона: ")
        cur.execute("DELETE FROM contacts WHERE id IN (SELECT contact_id FROM phones WHERE phone = %s)", (phone,))
    conn.commit()
    print("удалено")

def search():
    query = input("введите запрос: ")
    cur.execute("SELECT * FROM search_contacts(%s)", (query,))
    for row in cur.fetchall():
        print(row)

def filter_group():
    group = input("введите группу: ")
    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday, g.name, ph.phone, ph.type
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        LEFT JOIN phones ph ON ph.contact_id = c.id
        WHERE g.name = %s
    """, (group,))
    for row in cur.fetchall():
        print(row)

def search_email():
    query = input("введите часть email: ")
    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday, g.name, ph.phone, ph.type
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        LEFT JOIN phones ph ON ph.contact_id = c.id
        WHERE c.email ILIKE %s
    """, (f"%{query}%",))
    for row in cur.fetchall():
        print(row)

def paginate():
    offset = 0
    page_size = 3
    while True:
        cur.execute("SELECT * FROM get_contacts_page(%s, %s)", (page_size, offset))
        rows = cur.fetchall()
        for row in rows:
            print(row)
        cmd = input("next/prev/quit: ").strip().lower()
        if cmd == "next":
            offset += page_size
        elif cmd == "prev" and offset > 0:
            offset -= page_size
        elif cmd == "quit":
            break

def add_phone():
    name = input("имя контакта: ")
    phone = input("телефон: ")
    p_type = input("тип home/work/mobile: ") or "mobile"
    cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, p_type))
    conn.commit()
    print("добавлено")

def move_group():
    name = input("имя контакта: ")
    group = input("новая группа: ")
    cur.execute("CALL move_to_group(%s, %s)", (name, group))
    conn.commit()
    print("перемещено")

def export_json():
    cur.execute("""
        SELECT c.id, c.name, c.email, TO_CHAR(c.birthday, 'YYYY-MM-DD'), g.name
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
    """)
    result = []
    for cid, name, email, birthday, group in cur.fetchall():
        cur.execute("SELECT phone, type FROM phones WHERE contact_id = %s", (cid,))
        phones = [{"phone": p, "type": t} for p, t in cur.fetchall()]
        result.append({"name": name, "email": email, "birthday": birthday, "group": group, "phones": phones})
    with open("contacts.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("экспорт завершен")

def import_json():
    with open("contacts.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    for item in data:
        name = item.get("name")
        cur.execute("SELECT id FROM contacts WHERE name = %s LIMIT 1", (name,))
        existing = cur.fetchone()
        if existing:
            action = input(f"'{name}' уже существует. s-пропустить o-перезаписать: ")
            if action == "o":
                cur.execute("DELETE FROM contacts WHERE id = %s", (existing[0],))
            else:
                continue
        group_id = None
        if item.get("group"):
            cur.execute("SELECT id FROM groups WHERE name = %s", (item["group"],))
            group_id = cur.fetchone()[0]
        cur.execute("INSERT INTO contacts(name, email, birthday, group_id) VALUES(%s, %s, %s, %s) RETURNING id",
                    (name, item.get("email"), item.get("birthday"), group_id))
        cid = cur.fetchone()[0]
        for ph in item.get("phones", []):
            cur.execute("INSERT INTO phones(contact_id, phone, type) VALUES(%s, %s, %s)",
                        (cid, ph.get("phone"), ph.get("type")))
    conn.commit()
    print("импорт завершен")

if __name__ == "__main__":
    while True:
        work()
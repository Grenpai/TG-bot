from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector
import os
import sys
import random

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

# База данных
CONFIG = {
    'user': 'j1007852',
    'password': 'el|N#2}-F8',
    'host': 'srv201-h-st.jino.ru',
    'database': 'j1007852_13423'
}


# _________________________________________________________________________________

# Создает таблицу для хранения характеристик (если такая НЕ существует)
def create_table():
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS характеристики (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),  -- Новый столбец для имени
                strength INT,
                constitution INT,
                dexterity INT,
                intelligence INT,
                wisdom INT,
                charisma INT
            )
        ''')
        conn.commit()
        print("Таблица 'характеристики' создана или уже существует.")
    except mysql.connector.Error as err:
        print(f"Ошибка при создании таблицы: {err}")
    finally:
        if conn:
            cursor.close()
            conn.close()


# Создает таблицу logs (если такой НЕ существует)
def create_logs_table():
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor()
        cursor.execute('''
           CREATE TABLE IF NOT EXISTS logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                username VARCHAR(255),
                command VARCHAR(255) NOT NULL,
                timestamp DATETIME NOT NULL
            )
        ''')
        conn.commit()
        print("Таблица 'logs' создана или уже существует.")
    except mysql.connector.Error as err:
        print(f"Ошибка при создании таблицы 'logs': {err}")
    finally:
        if conn:
            cursor.close()
            conn.close()


# Сохраняет в БД значения характеристик
def save_specifications(name, strength, constitution, dexterity, intelligence, wisdom, charisma):
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor()
        query = '''
            INSERT INTO характеристики (name, strength, constitution, dexterity, intelligence, wisdom, charisma)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(query, (name, strength, constitution, dexterity, intelligence, wisdom, charisma))
        conn.commit()
        print("Характеристики сохранены в базе данных.")
    except mysql.connector.Error as err:
        print(f"Ошибка при сохранении характеристик: {err}")
    finally:
        if conn:
            cursor.close()
            conn.close()


# Получает характеристики по ID.
def get_specifications(spec_id):
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM характеристики WHERE id = %s', (spec_id,))
        return cursor.fetchone()  # Возвращает одну запись
    except mysql.connector.Error as err:
        print(f"Ошибка при получении характеристик: {err}")
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()


# Возвращает последний вставленный ID из таблицы характеристик.
def get_last_inserted_id():
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(id) FROM характеристики')
        last_id = cursor.fetchone()[0]
        return last_id
    except mysql.connector.Error as err:
        print(f"Ошибка при получении последнего ID: {err}")
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()


# Возвращает случайное имя из файла Names.txt.
def get_random_name():
    with open("Names.txt", "r") as file:
        names = file.readlines()
    return random.choice(names).strip()


# Генерирует случайные значения для характеристик
def get_random_specifications():
    strength = random.randint(10, 99)
    constitution = random.randint(10, 99)
    dexterity = random.randint(10, 99)
    intelligence = random.randint(10, 99)
    wisdom = random.randint(10, 99)
    charisma = random.randint(10, 99)
    return strength, constitution, dexterity, intelligence, wisdom, charisma


# Получение данных из таблицы logs
def get_logs_data(sort_by='id', order='ASC'):
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor(dictionary=True)
        query = f'SELECT * FROM logs ORDER BY {sort_by} {order}'
        cursor.execute(query)
        logs_data = cursor.fetchall()
        return logs_data
    except mysql.connector.Error as err:
        print(f"Ошибка при получении данных из таблицы logs: {err}")
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()


# _________________________________________________________________________________


@app.route('/')
def index():
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'ASC')
    logs = get_logs_data(sort_by, order)
    return render_template('index.html', logs=logs, sort_by=sort_by, order=order)


# Обработчик команды /submit
@app.route('/submit', methods=['POST'])
def submit():
    name = get_random_name()
    strength, constitution, dexterity, intelligence, wisdom, charisma = get_random_specifications()

    save_specifications(name, strength, constitution, dexterity, intelligence, wisdom, charisma)
    return redirect(url_for('results'))


# Обработчик команды для получения последнего вставленного ID
@app.route('/results')
def results():
    last_id = get_last_inserted_id()
    TakenSpecifications = get_specifications(last_id)
    return render_template('results.html', specifications=TakenSpecifications)


# Обработчик команды /random_character
@app.route('/random_character', methods=['GET'])
def random_character():
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM характеристики ORDER BY RAND() LIMIT 1')
        result = cursor.fetchone()
        print(result)  # отладка
        if result:
            return jsonify(result)
        else:
            return jsonify({'message': 'Нет характеристик в базе данных.'}), 404
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()


# Запуск
if __name__ == '__main__':
    create_table()
    create_logs_table()
    app.run(debug=True)
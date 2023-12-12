import psycopg2

def connect():
    con = psycopg2.connect(dbname = 'user_data', user = 'aideas', password = '&w*a*t*c_', host = 'localhost')
    #con.set_client_encoding('utf-8')
    return con

query_create_user = """
CREATE TABLE IF NOT EXISTS "user" (
    id TEXT PRIMARY KEY,
    count INTEGER DEFAULT 0,
    processing BOOLEAN DEFAULT false,
    answer_type TEXT DEFAULT 'text',
    save_history BOOLEAN DEFAULT true,
    vip BOOLEAN DEFAULT false
)"""
query_delete_user = """DROP TABLE IF EXISTS "user" """

query_create_chat = """
CREATE TABLE IF NOT EXISTS "chat" (
    id TEXT PRIMARY KEY,
    count INTEGER DEFAULT 0,
    processing BOOLEAN DEFAULT false,
    answer_type TEXT DEFAULT 'text',
    save_history BOOLEAN DEFAULT true,
    vip BOOLEAN DEFAULT false,
    keywords TEXT DEFAULT 'bot,бот,gpt',
    answer_voice_chat TEXT DEFAULT 'recognition'
);"""
query_delete_chat = """DROP TABLE IF EXISTS "chat" """

# Подключение к базе данных
conn = connect()
cursor = conn.cursor()

# Функция для создания баз данных
def create_databases():
    # Создание таблицы "chat"
    cursor.execute(query_create_chat)


    # Создание таблицы "user"
    cursor.execute(query_create_user)

    # Сохранение изменений
    conn.commit()
    print("Базы данных успешно созданы.")

# Функция для удаления баз данных
def delete_databases():
    # Удаление таблицы "user"
    cursor.execute(query_delete_user)

    # Удаление таблицы "tokens"
    cursor.execute(query_delete_chat)

    # Сохранение изменений
    conn.commit()
    print("Базы данных успешно удалены.")

# Функция для повторного создания баз данных
def recreate_databases():
    delete_databases()
    create_databases()

# Основная функция
def main():
    while True:
        # Получение ввода пользователя
        action = input("Введите 'create' для создания баз данных, 'delete' для удаления баз данных, 'recreate' для повторного создания баз данных, или 'exit' для выхода: ")

        if action == 'create':
            create_databases()
        elif action == 'delete':
            delete_databases()
        elif action == 'recreate':
            recreate_databases()
        elif action == 'exit':
            break
        else:
            print("Некорректный ввод. Повторите попытку.")

    # Закрытие подключения к базе данных
    conn.close()

if __name__ == '__main__':
    main()

import sqlite3
from typing import Optional
from typing import Any, List, Optional, Tuple
from bot.utils.logger import log_error


class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        """Создание таблицы участников с измененной структурой"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Таблица менеджеров
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS managers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    username TEXT,
                    phone_number TEXT
                )
            ''')

            # Таблица заявок
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    manager_id INTEGER NOT NULL,
                    salon TEXT,
                    request_type INTEGER,
                    client_name TEXT,
                    client_age INTEGER,
                    procedure_name TEXT,
                    procedure_date TEXT,
                    procedure_time TEXT,
                    client_phone TEXT,
                    rejection_reason TEXT,
                    request_date TEXT NOT NULL,
                    FOREIGN KEY (manager_id) REFERENCES managers (id)
                )
            ''')

            # Статистика менеджеров
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS manager_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    manager_id INTEGER NOT NULL,
                    total_clients INTEGER DEFAULT 0,
                    total_requests INTEGER DEFAULT 0,
                    last_update TEXT NOT NULL,
                    FOREIGN KEY (manager_id) REFERENCES managers (id)
                )
            ''')
            
            conn.commit()




    def create_new_request(self, manager_id: int, client_name: str = None) -> int:
        """Создать новую заявку и вернуть ее ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO requests (manager_id, client_name, client_age, procedure_name, 
                                    procedure_date, procedure_time, client_phone, request_date)
                VALUES (?, ?, NULL, NULL, NULL, NULL, NULL, datetime('now'))
            ''', (manager_id, client_name))
            conn.commit()
            return cursor.lastrowid

    def update_request(self, request_id: int, salon: str, request_type: int, client_name: str, client_age: int, procedure_name: str,
                        procedure_date: str, procedure_time: str, client_phone: str, rejection_reason: str = None):
        """Обновить данные в существующей заявке, включая причину отказа (если есть)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE requests
                SET salon = ?, request_type = ?, client_name = ?, client_age = ?, procedure_name = ?, procedure_date = ?, 
                    procedure_time = ?, client_phone = ?, rejection_reason = ?
                WHERE id = ?
            ''', (salon, request_type, client_name, client_age, procedure_name, procedure_date, procedure_time, client_phone, rejection_reason, request_id))
            conn.commit()


    

    # == For admin ==
    def add_person(self, name: str) -> bool:
        """
        Добавление пользователя в базу данных.
        Возвращает True, если пользователь успешно добавлен, иначе False.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO managers (name) VALUES (?)', (name,))
                conn.commit()
                return True
        except sqlite3.Error as e:
            log_error(f"Ошибка добавления пользователя: {e}")
            return False

    def delete_person_by_name(self, name: str) -> bool:
        """Удаление пользователя по имени."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM managers WHERE name = ?", (name,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка удаления пользователя: {e}")
            return False
    # == For admin ==




    # == Handlers ==
    def execute_query(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[List[Tuple]]:
        """
        Выполняет SQL-запрос с параметрами.
        :param query: SQL-запрос для выполнения.
        :param params: Кортеж с параметрами для подстановки в запрос.
        :return: Список кортежей с результатами запроса (только для SELECT).
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                if query.strip().upper().startswith("SELECT"):
                    return cursor.fetchall()
                conn.commit()
                return None
        except sqlite3.Error as e:
            print(f"Ошибка выполнения SQL-запроса: {e}")
            return None

    def get_managers(self) -> List[dict]:
        """
        Получение списка пользователей для отображения на кнопках.
        Возвращает список словарей с полями 'id' и 'name'.
        """
        query = "SELECT id, name FROM managers"
        result = self.execute_query(query)
        return [{"id": row[0], "name": row[1]} for row in result] if result else []
        
    def get_manager_by_name(self, name: str) -> Optional[dict]:
        query = 'SELECT id, name FROM managers WHERE name = ?'
        result = self.execute_query(query, (name,))
        if result:
            return {"id": result[0][0], "name": result[0][1]}
        return None
    
    def get_manager_by_id(self, manager_id: int) -> dict:
        """Получаем менеджера по его ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM managers WHERE id = ?', (manager_id,))
            manager = cursor.fetchone()
            return dict(manager) if manager else None
    # == Handlers ==


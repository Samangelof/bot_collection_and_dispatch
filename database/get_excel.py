import sqlite3
from openpyxl import Workbook
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile
from aiogram.types import ParseMode


def export_to_excel(db_path: str, excel_path: str):
    """Экспорт данных из базы данных в Excel"""

    #! определить поля для вывода из бд
    query = """
        SELECT id, full_name, first_name, last_name, username, language_code, check_number, telegram_id, phone_number
        FROM participants
    """

    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(query).fetchall()

    wb = Workbook()
    ws = wb.active
    ws.title = "Participants"

    #! Заголовки в Excel таблице
    headers = ["", "", "", "Фамилия", "Username", "Язык", "№ чека", "Telegram ID", "Телефон"]
    ws.append(headers)

    for row in rows:
        ws.append(row)

    # Автоподгон ширины колонок
    for col in ws.columns:
        max_length = max(len(str(cell.value) if cell.value else "") for cell in col)
        ws.column_dimensions[col[0].column_letter].width = max_length + 2

    wb.save(excel_path)

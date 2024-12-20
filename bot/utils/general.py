from database.sqlite_db import DatabaseManager


async def get_manager_name(manager_id: int, db: DatabaseManager):
    """Получаем имя менеджера по его ID."""
    manager = db.get_manager_by_id(manager_id)
    if manager:
        return manager["name"]
    return "Неизвестный менеджер"

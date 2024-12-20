from database.sqlite_db import DatabaseManager
from services.setup_bot import bot
from bot.utils.general import get_manager_name


CONFIRMED_REQUEST_CHAT_ID = "-4602943365"
UNCONFIRMED_REQUEST_CHAT_ID = "-4731420166"



async def send_request_to_chat(request_data: dict, db: DatabaseManager):
    """Формируем анкету и отправляем в соответствующий чат."""
    
    if not request_data.get('manager_name'):
        manager_name = await get_manager_name(request_data.get('manager_id'), db)
        request_data['manager_name'] = manager_name

    request_text = (
        f"*Заявка ID:* {request_data.get('request_id')}\n"
        f"*Менеджер:* {request_data.get('manager_name')}\n"
        f"*Салон:* {request_data.get('salon_name')}\n"
        f"*Тип заявки:* {request_data.get('request_type')}\n"
        f"*Имя клиента:* {request_data.get('client_name')}\n"
        f"*Возраст клиента:* {request_data.get('client_age')}\n"
        f"*Название процедуры:* {request_data.get('procedure_name')}\n"
        f"*Дата процедуры:* {request_data.get('procedure_date')}\n"
        f"*Время процедуры:* {request_data.get('procedure_time')}\n"
        f"*Телефон клиента:* {request_data.get('client_phone')}\n"
        f"*Причина отказа:* {request_data.get('rejection_reason')}\n"
    )

    if request_data.get('request_type') == "Подтвержденная":
        chat_id = CONFIRMED_REQUEST_CHAT_ID
    else:
        chat_id = UNCONFIRMED_REQUEST_CHAT_ID

    await bot.send_message(chat_id, request_text, parse_mode="Markdown")

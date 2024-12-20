from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import (
    InputFile, 
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    ReplyKeyboardRemove
)
from database.sqlite_db import DatabaseManager
from bot.states.all_states import GeneralStates, ConfirmedRequestStates, UnconfirmedRequestStates
from bot.utils.send_chat import send_request_to_chat
from bot.utils.logger import log_info, log_error
from bot.handlers.confirmed_handler import process_confirmed_request


# ===============================================================================
# == Салоны на выбор ==
SALONS = ["Kedma luxury spa", "Fashiontv Studio"]
# == Типы заявок ==
REQUEST_TYPES = ["Подтвержденная", "Не готовая"]


# ===============================================================================
#* == Начинаем ==
async def start_command(message: types.Message, state: FSMContext, db: DatabaseManager):
    """Обработчик команды /start."""
    log_info(f'start_command_data={message}')
    users = db.get_managers()
    if not users:
        log_info("Список пользователей пуст!")
        await message.answer("Список менеджеров пуст. Обратитесь к администратору.")
        return

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for user in users:
        keyboard.add(KeyboardButton(user["name"]))

    await message.answer(
        "Выберите свое имя:",
        reply_markup=keyboard
    )

    await GeneralStates.WAITING_FOR_SELECT_NAME.set()


# ===============================================================================
# == Выбор имени менеджера ==
async def process_manager_name(message: types.Message, state: FSMContext, db: DatabaseManager):
    """Обработка выбора имени менеджера."""
    log_info(f'process_manager_name_data={message}')

    manager_name = message.text
    manager = db.get_manager_by_name(manager_name)
    if not manager:
        log_info(f"Менеджер с именем {manager_name} не найден.")
        await message.answer("Менеджер с таким именем не найден. Попробуйте еще раз.")
        return

    new_request_id = db.create_new_request(manager_id=manager["id"])

    await state.update_data(request_id=new_request_id)
    await state.update_data(manager_id=manager["id"])


    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for salon in SALONS:
        keyboard.add(KeyboardButton(salon))

    keyboard.add(KeyboardButton("Назад"))

    #? Переход в следующее состояние
    await message.answer(
        f"{manager_name}, выберите салон:",
        reply_markup=keyboard
    )

    await GeneralStates.WAITING_FOR_SELECT_SALON.set()


# =============================================================================== 
# == Выбор салона == 
async def process_salon_selection(message: types.Message, state: FSMContext, db: DatabaseManager):
    """Обработка и проверка выбора салона."""
    log_info(f'process_salon_selection_data={message}')


    # == Вернуться назад ==
    if message.text == "Назад":
        await GeneralStates.WAITING_FOR_SELECT_NAME.set()
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for user in db.get_managers():
            keyboard.add(KeyboardButton(user["name"]))
        keyboard.add(KeyboardButton("Назад"))
        await message.answer(
            "Выберите свое имя:",
            reply_markup=keyboard
        )
        return
    # == Вернуться назад ==
    

    salon_name = message.text
    if salon_name not in SALONS:
        await message.answer("Такого салона нет. Попробуйте еще раз.")
        return

    await state.update_data(salon_name=salon_name)
    
    log_info(f"Выбран салон: {salon_name}. Продолжаем...")
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for request_type in REQUEST_TYPES:
        keyboard.add(KeyboardButton(request_type))
    keyboard.add(KeyboardButton("Назад"))


    await message.answer(
        "Выберите тип заявки:",
        reply_markup=keyboard
    )
    await GeneralStates.WAITING_FOR_SELECT_REQUEST_TYPE.set()


# == Выбор типа заявки ==
async def process_request_type_selection(message: types.Message, state: FSMContext, db: DatabaseManager):
    """Обработка и проверка выбора типа заявки."""
    log_info(f'process_request_type_selection_data={message}')

    # == Вернуться назад ==
    if message.text == "Назад":
        await message.answer("**Вы вернулись к выбору салона.**", parse_mode='Markdown')
        await GeneralStates.WAITING_FOR_SELECT_SALON.set()
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for salon in SALONS:
            keyboard.add(KeyboardButton(salon))

        keyboard.add(KeyboardButton("Назад"))
        await message.answer(
            f"Выберите салон:",
            reply_markup=keyboard
        )
        return
    
    request_type = message.text

    if request_type not in REQUEST_TYPES:
        await message.answer("Такого типа заявки нет. Попробуйте еще раз.")
        return

    await state.update_data(request_type=request_type)

    log_info(f"Выбран тип заявки: {request_type}. Продолжаем...")

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Назад"))
    
    # == Завершаем процесс или переходим к следующему шагу ==
    await message.answer(
        "Введите имя клиента:",
        reply_markup=keyboard
    )

    await GeneralStates.WAITING_FOR_CLIENT_NAME.set()


# ========================================================================
# == Ввод имени клиента ==
async def process_client_name(message: types.Message, state: FSMContext, db: DatabaseManager):
    """Обработка ввода имени клиента."""
    # == Вернуться назад ==
    if message.text == "Назад":
        await message.answer("**Вы вернулись к выбору типа заявки.**", parse_mode='Markdown')
        await GeneralStates.WAITING_FOR_SELECT_REQUEST_TYPE.set()
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for request_type in REQUEST_TYPES:
            keyboard.add(KeyboardButton(request_type))
        keyboard.add(KeyboardButton("Назад"))
        await message.answer(
            "Выберите тип заявки:",
            reply_markup=keyboard
        )
        return
    # == Вернуться назад ==
    

    client_name = message.text
    await state.update_data(client_name=client_name)

    await message.answer(f"Введите возраст клиента:")

    await GeneralStates.WAITING_FOR_CLIENT_AGE.set()


# ========================================================================
# == Возраст клиента ==
async def process_client_age(message: types.Message, state: FSMContext, db: DatabaseManager):
    """Обработка ввода возраста клиента."""
    # == Вернуться назад ==
    if message.text == "Назад":
        await message.answer("**Вы вернулись к вводу имени клиента.**")
        await GeneralStates.WAITING_FOR_CLIENT_NAME.set()
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("Назад"))
        await message.answer(
            "Введите имя клиента:",
            reply_markup=keyboard
        )
        return
    # == Вернуться назад ==

    try:
        client_age = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный возраст.")
        return

    await state.update_data(client_age=client_age)

    await message.answer(f"Введите название процедуры")
    await GeneralStates.WAITING_FOR_PROCEDURE_NAME.set()


# ========================================================================
# == Название процедуры ==
async def process_procedure_name(message: types.Message, state: FSMContext, db: DatabaseManager):
    """Обработка ввода названия процедуры."""
    # == Вернуться назад ==
    if message.text == "Назад":
        await message.answer("**Вы вернулись к вводу возраста клиента.**")
        await GeneralStates.WAITING_FOR_CLIENT_AGE.set()
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("Назад"))
        await message.answer(
            "Введите возраст клиента:",
            reply_markup=keyboard
        )
        return
    # == Вернуться назад ==

    procedure_name = message.text
    await state.update_data(procedure_name=procedure_name)

    await message.answer("Введите дату процедуры в формате: дд.мм.гггг (например, 01.01.1970).")

    await GeneralStates.WAITING_FOR_PROCEDURE_DATE.set()


#? https://github.com/noXplode/aiogram_calendar
# ========================================================================
# == Дата процедуры ==
async def process_procedure_date(message: types.Message, state: FSMContext, db: DatabaseManager):
    """Обработка ввода даты процедуры."""
    # == Вернуться назад ==
    if message.text == "Назад":
        await message.answer("**Вы вернулись к вводу названия процедуры.**")
        await GeneralStates.WAITING_FOR_PROCEDURE_NAME.set()
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("Назад"))
        await message.answer(
            "Введите название процедуры:",
            reply_markup=keyboard
        )
        return
    # == Вернуться назад ==

    procedure_date = message.text  # Проверку на формат даты можно сделать позже
    await state.update_data(procedure_date=procedure_date)

    await message.answer(f"Введите время процедуры:")
    await GeneralStates.WAITING_FOR_PROCEDURE_TIME.set()
# ========================================================================


# ========================================================================
# == Время процедуры ==
async def process_procedure_time(message: types.Message, state: FSMContext, db: DatabaseManager):
    """Обработка ввода времени процедуры."""
    # == Вернуться назад ==
    if message.text == "Назад":
        await message.answer("**Вы вернулись к вводу даты процедуры.**")
        await GeneralStates.WAITING_FOR_PROCEDURE_DATE.set()
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("Назад"))
        await message.answer(
            "Введите дату процедуры:",
            reply_markup=keyboard
        )
        return
    # == Вернуться назад ==

    #? Здесь можно добавить валидацию формата времени, если нужно
    procedure_time = message.text 
    await state.update_data(procedure_time=procedure_time)

    await message.answer(f"Введите номер телефона:")
    
    await GeneralStates.WAITING_FOR_CLIENT_PHONE.set()



# ========================================================================
# == Номер телефона клиента ==
async def process_client_phone(message: types.Message, state: FSMContext, db: DatabaseManager):
    """Обработка ввода номера телефона клиента."""
    data = await state.get_data()
    log_info(f'[FINAL] process_client_phone={data}')

    # == Вернуться назад ==
    if message.text == "Назад":
        await message.answer("**Вы вернулись к вводу времени процедуры.**")
        await GeneralStates.WAITING_FOR_PROCEDURE_TIME.set()
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("Назад"))
        await message.answer(
            "Введите время процедуры:",
            reply_markup=keyboard
        )
        return
    # == Вернуться назад ==

    client_phone = message.text
    await state.update_data(client_phone=client_phone)

    request_data = await state.get_data()

    request_type = request_data.get("request_type")

    if request_type == "Подтвержденная":
        # await message.answer(f"Заявка подтверждена. Все вопросы завершены.")
        await process_confirmed_request(message, state, db)

    else:  # "Не готовая"
        await message.answer(f"Заявка не готова. Пожалуйста, следуйте дальше.")
        await UnconfirmedRequestStates.WAITING_FOR_ADDITIONAL_INFO.set()
from aiogram.types import (
    InputFile, 
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    ReplyKeyboardRemove
)
from aiogram import types
from aiogram.dispatcher import FSMContext
from database.sqlite_db import DatabaseManager
from bot.utils.send_chat import send_request_to_chat
from bot.states.all_states import ConfirmedRequestStates
from bot.utils.general import get_manager_name
from bot.utils.logger import log_info


# ========================================================================
# == Подтвержденная заявка ==
async def process_confirmed_request(message: types.Message, state: FSMContext, db: DatabaseManager):
    """Обработка подтвержденной заявки."""

    # Получаем данные из состояния
    request_data = await state.get_data()
    # Формируем текст сообщения для подтверждения записи
    manager_name = await get_manager_name(request_data.get('manager_id'), db)
    procedure_name = request_data.get('procedure_name')
    procedure_date = request_data.get('procedure_date')
    procedure_time = request_data.get('procedure_time')
    
    request_text = (
        f"Добрый день! Это {manager_name}, представитель Kedma Luxury Spa. "
        f"Вы записались на {procedure_name} через нашу рекламу. Подтверждаю вашу запись на {procedure_date} в {procedure_time}. Все верно?"
    )

    # Клавиатура с кнопками "Да" и "Нет"
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Да"))
    keyboard.add(KeyboardButton("Нет"))

    # Отправляем сообщение пользователю
    await message.answer(request_text, reply_markup=keyboard)

    # # Переводим в состояние ожидания ответа
    await ConfirmedRequestStates.WAITING_FOR_CONFIRMATION_ANSWER.set()


# ========================================================================
# == Ответ на подтверждение ==
async def process_confirmation_answer(message: types.Message, state: FSMContext, db: DatabaseManager):
    """Обработка ответа на подтверждение заявки."""

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Да"))
    keyboard.add(KeyboardButton("Нет"))
    keyboard.add(KeyboardButton("Назад"))

    #? == Закрытие разговора ==
    if message.text == "Да":
        request_data = await state.get_data()
        procedure_date = request_data.get('procedure_date')
        procedure_time = request_data.get('procedure_time')

        confirmation_text = (
            f"Спасибо за ваш интерес! Мы ждем вас {procedure_date} в {procedure_time}. "
            "Убедитесь, что придете немного раньше, чтобы мы успели все подготовить. До встречи в Kedma Luxury Spa!"
        )
        await message.answer(confirmation_text, reply_markup=keyboard)


        new_req_for_manager = (
            f"✅ Отлично! Клиент подтвердил запись на {procedure_date} в {procedure_time}.\n"
            "Можете создать новую заявку нажав кнопку 'Новая заявка'"
        )
        
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("Новая заявка"))
        await message.answer(new_req_for_manager, reply_markup=keyboard)
        await state.finish()


    #? == Закрытие разговора ==

    elif message.text == "Нет":
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("Цена"))
        keyboard.add(KeyboardButton("Время"))
        keyboard.add(KeyboardButton("Общая польза"))
        keyboard.add(KeyboardButton("Назад"))
        
        await message.answer(
            "❗ Клиент отказался. Выберите причину отказа, чтобы получить скрипт ответа:",
            reply_markup=keyboard
        )
        await ConfirmedRequestStates.WAITING_FOR_CLARIFICATION.set()

    elif message.text == "Назад":
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("Да"))
        keyboard.add(KeyboardButton("Нет"))
        await message.answer("Вы вернулись назад. Пожалуйста, подтвердите вашу запись.", reply_markup=keyboard)
        await ConfirmedRequestStates.WAITING_FOR_CONFIRMATION_ANSWER.set()


async def process_clarification(message: types.Message, state: FSMContext):
    """Предоставление менеджеру скрипта ответа на возражение клиента"""
    
    if message.text == "Цена":
        response = (
            "💡 Скрипт ответа на возражение по цене:\n\n"
            "Да, стоимость действительно небольшая, но она позволит вам ощутить качество "
            "наших услуг и уникальность подхода. После процедуры мы сможем предложить вам "
            "индивидуальный план ухода, чтобы вы получили максимальный результат."
        )
    
    elif message.text == "Время":
        response = (
            "💡 Скрипт ответа на возражение по времени:\n\n"
            "Мы можем подобрать удобное время. Как насчет [Предложите альтернативное время]?"
        )
    
    elif message.text == "Общая польза":
        response = (
            "💡 Скрипт ответа на возражение о пользе:\n\n"
            "Это отличный шанс не только попробовать нашу услугу, но и узнать, какие "
            "результаты вы можете получить в дальнейшем. Многие клиенты возвращаются к нам, "
            "чтобы продолжить курс ухода."
        )
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Записать причину отказа"))
    keyboard.add(KeyboardButton("Назад"))

    await message.answer(
        f"{response}\n\n"
        "После разговора с клиентом выберите действие:",
        reply_markup=keyboard
    )
    await ConfirmedRequestStates.WAITING_FOR_FINAL_DECISION.set()

async def process_final_decision(message: types.Message, state: FSMContext):
    """Обработка финального решения менеджера"""
    
    if message.text == "Записать причину отказа":
        await message.answer(
            "Опишите причину отказа клиента:",
            reply_markup=ReplyKeyboardRemove()
        )
        await ConfirmedRequestStates.WAITING_FOR_REJECTION_REASON.set()
    
    elif message.text == "Назад":
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("Цена"))
        keyboard.add(KeyboardButton("Время"))
        keyboard.add(KeyboardButton("Общая польза"))
        keyboard.add(KeyboardButton("Назад"))
        
        await message.answer(
            "Выберите причину отказа клиента:",
            reply_markup=keyboard
        )
        await ConfirmedRequestStates.WAITING_FOR_CLARIFICATION.set()

async def process_rejection_reason(message: types.Message, state: FSMContext, db: DatabaseManager):
    """Сохранение причины отказа"""
    rejection_reason = message.text
    
    await state.update_data(rejection_reason=rejection_reason)
    data = await state.get_data()
    log_info(f'[FINAL] process_rejection_reason={data}')
    
    request_data = await state.get_data()


    db.update_request(
        request_id=request_data.get("request_id"),
        salon=request_data.get("salon_name"),
        request_type=request_data.get("request_type"),
        client_name=request_data.get("client_name"),
        client_age=request_data.get("client_age"),
        procedure_name=request_data.get("procedure_name"),
        procedure_date=request_data.get("procedure_date"),
        procedure_time=request_data.get("procedure_time"),
        client_phone=request_data.get("client_phone"),
        rejection_reason=request_data.get("rejection_reason")
    )

    await send_request_to_chat(request_data, db)
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Новая заявка"))
    
    await message.answer(
        "✅ Причина отказа сохранена.\n"
        "Можете создать новую заявку.",
        reply_markup=keyboard
    )
    
    await state.finish()
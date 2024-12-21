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
from bot.states.all_states import UnconfirmedRequestStates
from bot.utils.general import get_manager_name
from bot.utils.logger import log_info


# ========================================================================
# == Неподтвержденная заявка ==
async def process_unconfirmed_request(message: types.Message, state: FSMContext, db: DatabaseManager):
    """Начальная обработка неподтвержденной заявки."""
    request_data = await state.get_data()
    manager_name = await get_manager_name(request_data.get('manager_id'), db)
    
    await state.update_data(
        manager_name=manager_name,
        procedure_name=request_data.get('procedure_name'),
        procedure_date=request_data.get('procedure_date'),
        procedure_time=request_data.get('procedure_time')
    )

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Русский"), KeyboardButton("Қазақша"))
    keyboard.add(KeyboardButton("Назад"))

    await message.answer(
        "Выберите язык клиента:",
        reply_markup=keyboard
    )
    await UnconfirmedRequestStates.WAITING_FOR_LANGUAGE_CHOICE.set()

# ========================================================================
# == Выбор языка ==
async def process_language_choice(message: types.Message, state: FSMContext, db: DatabaseManager):
    """Обработка выбора языка и отправка первого уточняющего сообщения"""
    if message.text == "Назад":
        # Возврат к выбору типа заявки
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("Подтвержденная"))
        keyboard.add(KeyboardButton("Не готовая"))
        await message.answer(
            "Выберите тип заявки:",
            reply_markup=keyboard
        )
        await state.finish()
        return

    await state.update_data(language=message.text)
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Да"))
    keyboard.add(KeyboardButton("Возражение"))
    keyboard.add(KeyboardButton("Назад"))

    if message.text == "Русский":
        clarification_text = (
            "Я вижу, что вы интересовались нашей услугой, но запись не была завершена. "
            "Возможно, у вас появились вопросы или сомнения? Буду рад(а) помочь."
        )
    else:  # Казахский
        clarification_text = (
            "Сіздің біздің қызметімізге қызығушылық танытқаныңызды, "
            "бірақ жазба аяқталмағанын көріп тұрмын. Мүмкін сізде сұрақтар немесе күмәндар бар шығар? "
            "Көмектесуге қуаныштымын."
        )

    await message.answer(
        f"💡 Скрипт для клиента:\n\n{clarification_text}",
        reply_markup=keyboard
    )
    await UnconfirmedRequestStates.WAITING_FOR_INITIAL_RESPONSE.set()

async def process_initial_response(message: types.Message, state: FSMContext):
    """Обработка первичного ответа клиента"""
    if message.text == "Назад":
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("Русский"), KeyboardButton("Қазақша"))
        keyboard.add(KeyboardButton("Назад"))
        await message.answer(
            "Выберите язык клиента:",
            reply_markup=keyboard
        )
        await UnconfirmedRequestStates.WAITING_FOR_LANGUAGE_CHOICE.set()
        return

    data = await state.get_data()
    language = data.get('language')
    
    if message.text == "Да": 
        if language == "Русский":
            response = (
                "Прекрасно! Это будет возможность познакомиться с нашим спа и увидеть, "
                "как наша уникальная методика ухода за кожей работает именно для вас."
            )
        else:
            response = (
                "Керемет! Бұл біздің спамен танысу және біздің теріге күтім жасаудың бірегей "
                "әдістемесі сіз үшін қалай жұмыс істейтінін көру мүмкіндігі болады."
            )

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("Да"))
        keyboard.add(KeyboardButton("Нет"))
        keyboard.add(KeyboardButton("Назад"))
        
        await message.answer(
            f"💡 Скрипт для клиента:\n\n{response}",
            reply_markup=keyboard
        )
        await UnconfirmedRequestStates.WAITING_FOR_FINAL_CONFIRMATION.set()
        
    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("Вопросы о бесплатности"))
        keyboard.add(KeyboardButton("Отказ из-за времени"))
        keyboard.add(KeyboardButton("Скепсис или недоверие"))
        keyboard.add(KeyboardButton("Записать причину отказа"))
        keyboard.add(KeyboardButton("Назад"))
        
        await message.answer( 
            "❗ Выберите тип возражения клиента:",
            reply_markup=keyboard
        )
        await UnconfirmedRequestStates.WAITING_FOR_OBJECTION_RESPONSE.set()

async def process_objection_response(message: types.Message, state: FSMContext):
    """Обработка возражений клиента"""
    if message.text == "Назад":
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("Да"))
        keyboard.add(KeyboardButton("Возражение"))
        keyboard.add(KeyboardButton("Назад"))
        
        data = await state.get_data()
        language = data.get('language')
        
        if language == "Русский":
            clarification_text = (
                "Я вижу, что вы интересовались нашей услугой, но запись не была завершена. "
                "Возможно, у вас появились вопросы или сомнения? Буду рад(а) помочь."
            )
        else:
            clarification_text = (
                "Сіздің біздің қызметімізге қызығушылық танытқаныңызды, "
                "бірақ жазба аяқталмағанын көріп тұрмын. Мүмкін сізде сұрақтар немесе күмәндар бар шығар? "
                "Көмектесуге қуаныштымын."
            )
            
        await message.answer(
            f"💡 Скрипт для клиента:\n\n{clarification_text}",
            reply_markup=keyboard
        )
        await UnconfirmedRequestStates.WAITING_FOR_INITIAL_RESPONSE.set()
        return

    data = await state.get_data()
    language = data.get('language')

    if message.text == "Записать причину отказа": 
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("Назад"))
        await message.answer(
            "Опишите причину отказа клиента:",
            reply_markup=keyboard
        )
        await UnconfirmedRequestStates.WAITING_FOR_REJECTION_REASON.set()
        return

    response = ""
    if language == "Русский":
        if message.text == "Вопросы о бесплатности":
            response = (
                "Да, эта процедура действительно полностью бесплатна. "
                "Мы хотим познакомить вас с нашими услугами и показать, "
                "как мы заботимся о наших клиентах."
            )
        elif message.text == "Отказ из-за времени":
            response = (
                "Я понимаю, что ваше время ценно. Мы можем предложить "
                "несколько альтернативных вариантов. Как насчет [Дата/время]?"
            )
        elif message.text == "Скепсис или недоверие":
            response = (
                "Наш спа – это премиум-бренд, работающий по всему миру. "
                "Мы уверены в качестве наших услуг и приглашаем вас убедиться "
                "в этом совершенно бесплатно."
            )
    else:  # Казахский язык
        # Здесь нужно добавить казахские версии скриптов
        pass

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Да"))
    keyboard.add(KeyboardButton("Нет"))
    keyboard.add(KeyboardButton("Назад"))
    
    await message.answer(
        f"💡 Скрипт ответа на возражение:\n\n{response}",
        reply_markup=keyboard
    )
    await UnconfirmedRequestStates.WAITING_FOR_FINAL_CONFIRMATION.set()

# ========================================================================
# == Обработка финального ответа ==
async def process_final_confirmation(message: types.Message, state: FSMContext, db: DatabaseManager):
    """Обработка финального ответа клиента"""
    if message.text == "Назад":
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("Вопросы о бесплатности"))
        keyboard.add(KeyboardButton("Отказ из-за времени"))
        keyboard.add(KeyboardButton("Скепсис или недоверие"))
        keyboard.add(KeyboardButton("Записать причину отказа"))
        keyboard.add(KeyboardButton("Назад"))
        
        await message.answer(
            "❗ Выберите тип возражения клиента:",
            reply_markup=keyboard
        )
        await UnconfirmedRequestStates.WAITING_FOR_OBJECTION_RESPONSE.set()
        return

    data = await state.get_data()
    language = data.get('language')
    procedure_date = data.get('procedure_date')
    procedure_time = data.get('procedure_time')

    if message.text == "Да":
        if language == "Русский":
            response = (
                f"Буду рад(а) вас видеть! Вы записаны на {procedure_date} в {procedure_time}. "
                "Не забудьте, что наша процедура подарит вам первые результаты и полное расслабление. "
                "Ждем вас в Kedma Luxury Spa!"
            )
        else:
            # Казахская версия
            pass


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
            f"✅ Скрипт для клиента:\n\n{response}",
            reply_markup=keyboard
        )
        await state.finish()
    elif message.text == 'Нет':
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("Вопросы о бесплатности"))
        keyboard.add(KeyboardButton("Отказ из-за времени"))
        keyboard.add(KeyboardButton("Скепсис или недоверие"))
        keyboard.add(KeyboardButton("Записать причину отказа"))
        keyboard.add(KeyboardButton("Назад"))
        
        await message.answer(
            "Выберите новый тип возражения клиента:",
            reply_markup=keyboard
        )
        await UnconfirmedRequestStates.WAITING_FOR_OBJECTION_RESPONSE.set()


# ========================================================================
# == Неподтвержденная заявка ==
async def process_rejection_reason(message: types.Message, state: FSMContext, db: DatabaseManager):
    """Сохранение причины отказа"""
    if message.text == "Назад":
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("Вопросы о бесплатности"))
        keyboard.add(KeyboardButton("Отказ из-за времени"))
        keyboard.add(KeyboardButton("Скепсис или недоверие"))
        keyboard.add(KeyboardButton("Записать причину отказа"))
        keyboard.add(KeyboardButton("Назад"))
        
        await message.answer(
            "❗ Выберите тип возражения клиента:",
            reply_markup=keyboard
        )
        await UnconfirmedRequestStates.WAITING_FOR_OBJECTION_RESPONSE.set()
        return

    rejection_reason = message.text
    await state.update_data(rejection_reason=rejection_reason)
    

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
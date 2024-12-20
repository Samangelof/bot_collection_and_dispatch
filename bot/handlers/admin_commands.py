from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from database.sqlite_db import DatabaseManager
from bot.states.all_states import AdminStates

from aiogram import types
from aiogram.dispatcher import FSMContext
from bot.states.all_states import AdminStates
from bot.utils.logger import log_info


ALLOWED_TELEGRAM_IDS = [783067394, 987654321]

async def admin_command(message: types.Message, state: FSMContext):
    """Обработчик команды /admin."""
    log_info(message)
    log_info(message.from_user.first_name)
    name = message.from_user.first_name
    if message.from_user.id not in ALLOWED_TELEGRAM_IDS:
        await message.answer("❌У вас нет прав для выполнения этой команды.")
        return

    # Переход в режим администратора
    await message.answer(
        f"Вы вошли в режим администратора, {name}.\nВыберите действие:",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton("Добавить имя")],
                [types.KeyboardButton("Удалить имя")],
                [types.KeyboardButton("Выйти из режима")]
            ],
            resize_keyboard=True
        )
    )
    await AdminStates.WAITING_FOR_ADMIN_ACTION.set()


async def process_admin_action(message: types.Message, state: FSMContext, db: DatabaseManager):
    """Обработка выбора действия администратора."""
    if message.text == "Добавить имя":
        # Убираем клавиатуру, чтобы предотвратить случайный ввод кнопки
        await message.answer("Введите имя нового пользователя:", reply_markup=ReplyKeyboardRemove())
        await AdminStates.WAITING_FOR_NEW_USER_NAME.set()
    elif message.text == "Удалить имя":
        # Создаем кнопки для выбора имени
        users = db.get_managers()
        if not users:
            await message.answer("Список пользователей пуст. Удалять некого.")
            return

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for user in users:
            keyboard.add(KeyboardButton(user["name"]))
        keyboard.add(KeyboardButton("Отмена"))

        await message.answer("Выберите пользователя для удаления:", reply_markup=keyboard)
        await AdminStates.WAITING_FOR_DELETE_USER_NAME.set()
    elif message.text == "Выйти из режима":
        await message.answer("Вы вышли из режима администратора.", reply_markup=ReplyKeyboardRemove())
        await state.finish()
    else:
        await message.answer("Пожалуйста, выберите действие из меню.")


async def process_new_user_name(message: types.Message, state: FSMContext, db: DatabaseManager):
    """Обработка введенного имени нового пользователя для добавления."""
    user_name = message.text
    await state.update_data(name=user_name)

    # Добавление пользователя в базу данных
    success = db.add_person(name=user_name)

    if success:
        await message.answer(f"✅ Пользователь {user_name} успешно добавлен!")
    else:
        await message.answer(f"❌ Произошла ошибка при добавлении пользователя {user_name}.")

    # Возврат в меню действий администратора
    await message.answer(
        "Выберите следующее действие:",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton("Добавить имя")],
                [types.KeyboardButton("Удалить имя")],
                [types.KeyboardButton("Выйти из режима")]
            ],
            resize_keyboard=True
        )
    )
    await AdminStates.WAITING_FOR_ADMIN_ACTION.set()


async def process_delete_user_name(message: types.Message, state: FSMContext, db: DatabaseManager):
    """Обработка выбора имени пользователя для удаления."""
    user_name = message.text

    if user_name == "Отмена":
        await message.answer(
            "Выберите следующее действие:",
            reply_markup=types.ReplyKeyboardMarkup(
                keyboard=[
                    [types.KeyboardButton("Добавить имя")],
                    [types.KeyboardButton("Удалить имя")],
                    [types.KeyboardButton("Выйти из режима")]
                ],
                resize_keyboard=True
            )
        )
        await AdminStates.WAITING_FOR_ADMIN_ACTION.set()
        return

    success = db.delete_person_by_name(name=user_name)

    if success:
        await message.answer(f"✅ Пользователь {user_name} успешно удален!")
    else:
        await message.answer(f"❌ Пользователь с именем {user_name} не найден.")

    # Возврат в меню действий администратора
    await message.answer(
        "Выберите следующее действие:",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton("Добавить имя")],
                [types.KeyboardButton("Удалить имя")],
                [types.KeyboardButton("Выйти из режима")]
            ],
            resize_keyboard=True
        )
    )
    await AdminStates.WAITING_FOR_ADMIN_ACTION.set()
from aiogram import Dispatcher
from database.sqlite_db import DatabaseManager
from bot.states.all_states import (
    AdminStates,
    GeneralStates,
    ConfirmedRequestStates,
    UnconfirmedRequestStates
)
from bot.handlers.admin_commands import (
    admin_command,
    process_admin_action,
    process_new_user_name,
    process_delete_user_name
)
from bot.handlers.main_handler import (
    start_command,
    process_manager_name,
    process_salon_selection,
    process_request_type_selection,
    process_client_name,
    process_client_age,
    process_procedure_name,
    process_procedure_date,
    process_procedure_time,
    process_client_phone,
    restart_command
)
from bot.handlers.confirmed_handler import (
    process_clarification,
    process_confirmation_answer,
    process_final_decision,
    process_rejection_reason
)
from bot.handlers.unconfirmed_handler import (
    process_language_choice,
    process_initial_response,
    process_objection_response,
    process_final_confirmation
)
from functools import partial


def register_handlers(dp: Dispatcher, db: DatabaseManager):
    # == Общие ==
    dp.register_message_handler(admin_command, commands=['admin'], state="*")
    dp.register_message_handler(lambda message, state, db=db: start_command(
        message, state, db), commands=['start'])
    dp.register_message_handler(lambda message, state, db=db: process_manager_name(
        message, state, db), state=GeneralStates.WAITING_FOR_SELECT_NAME)
    dp.register_message_handler(lambda message, state, db=db: process_salon_selection(
        message, state, db), state=GeneralStates.WAITING_FOR_SELECT_SALON)
    dp.register_message_handler(lambda message, state, db=db: process_request_type_selection(
        message, state, db), state=GeneralStates.WAITING_FOR_SELECT_REQUEST_TYPE)
    dp.register_message_handler(lambda message, state, db=db: process_client_name(
        message, state, db), state=GeneralStates.WAITING_FOR_CLIENT_NAME)
    dp.register_message_handler(lambda message, state, db=db: process_client_age(
        message, state, db), state=GeneralStates.WAITING_FOR_CLIENT_AGE)
    dp.register_message_handler(lambda message, state, db=db: process_procedure_name(
        message, state, db), state=GeneralStates.WAITING_FOR_PROCEDURE_NAME)
    dp.register_message_handler(lambda message, state, db=db: process_procedure_date(
        message, state, db), state=GeneralStates.WAITING_FOR_PROCEDURE_DATE)
    dp.register_message_handler(lambda message, state, db=db: process_procedure_time(
        message, state, db), state=GeneralStates.WAITING_FOR_PROCEDURE_TIME)
    dp.register_message_handler(lambda message, state, db=db: process_client_phone(
        message, state, db), state=GeneralStates.WAITING_FOR_CLIENT_PHONE)

    dp.register_message_handler(
        partial(restart_command, db=db),
        lambda message: message.text == 'Новая заявка',
        state='*'
    )

    # == Подтвержденные заявки ==
    dp.register_message_handler(lambda message, state, db=db: process_confirmation_answer(
        message, state, db), state=ConfirmedRequestStates.WAITING_FOR_CONFIRMATION_ANSWER)

    dp.register_message_handler(lambda message, state: process_clarification(
        message, state), state=ConfirmedRequestStates.WAITING_FOR_CLARIFICATION)

    dp.register_message_handler(lambda message, state: process_final_decision(
        message, state), state=ConfirmedRequestStates.WAITING_FOR_FINAL_DECISION)

    dp.register_message_handler(lambda message, state, db=db: process_rejection_reason(
        message, state, db), state=ConfirmedRequestStates.WAITING_FOR_REJECTION_REASON)

    # == Неподтвержденные заявки == 
    dp.register_message_handler(lambda message, state, db=db: process_language_choice(
        message, state, db), state=UnconfirmedRequestStates.WAITING_FOR_LANGUAGE_CHOICE)
    
    dp.register_message_handler(lambda message, state: process_initial_response(
        message, state), state=UnconfirmedRequestStates.WAITING_FOR_INITIAL_RESPONSE)
    
    dp.register_message_handler(lambda message, state: process_objection_response(
        message, state), state=UnconfirmedRequestStates.WAITING_FOR_OBJECTION_RESPONSE)
    
    dp.register_message_handler(lambda message, state, db=db: process_final_confirmation(
        message, state, db), state=UnconfirmedRequestStates.WAITING_FOR_FINAL_CONFIRMATION)
    
    dp.register_message_handler(lambda message, state, db=db: process_rejection_reason(
        message, state, db), state=UnconfirmedRequestStates.WAITING_FOR_REJECTION_REASON)

    # == Админ ==
    dp.register_message_handler(lambda message, state, db=db: process_admin_action(
        message, state, db), state=AdminStates.WAITING_FOR_ADMIN_ACTION)
    dp.register_message_handler(lambda message, state, db=db: process_new_user_name(
        message, state, db), state=AdminStates.WAITING_FOR_NEW_USER_NAME, content_types=['text'])
    dp.register_message_handler(lambda message, state, db=db: process_delete_user_name(
        message, state, db), state=AdminStates.WAITING_FOR_DELETE_USER_NAME, content_types=['text'])

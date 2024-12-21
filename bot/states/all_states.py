from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup


# State for manager
class GeneralStates(StatesGroup):
    """Состояния для конечного автомата регистрации участника"""
    WAITING_FOR_SELECT_NAME = State()
    WAITING_FOR_SELECT_SALON = State()
    WAITING_FOR_SELECT_REQUEST_TYPE = State()
    WAITING_FOR_CLIENT_NAME = State()
    WAITING_FOR_CLIENT_AGE = State()
    WAITING_FOR_PROCEDURE_NAME = State()
    WAITING_FOR_PROCEDURE_DATE = State()
    WAITING_FOR_PROCEDURE_TIME = State()
    WAITING_FOR_CLIENT_PHONE = State()


class ConfirmedRequestStates(StatesGroup):
    """Состояния для подтвержденной заявки"""
    WAITING_FOR_CONFIRMATION_ANSWER = State()
    WAITING_FOR_CLARIFICATION = State()
    WAITING_FOR_FINAL_DECISION = State()
    WAITING_FOR_REJECTION_REASON = State()


class UnconfirmedRequestStates(StatesGroup):
    """Состояния для неподтвержденной заявки"""
    WAITING_FOR_LANGUAGE_CHOICE = State()
    WAITING_FOR_INITIAL_RESPONSE = State()
    WAITING_FOR_OBJECTION_RESPONSE = State()
    WAITING_FOR_FINAL_CONFIRMATION = State()
    WAITING_FOR_REJECTION_REASON = State()

# State for admin
class AdminStates(StatesGroup):
    WAITING_FOR_ADMIN_ACTION = State()
    WAITING_FOR_NEW_USER_NAME = State()
    WAITING_FOR_DELETE_USER_NAME = State()

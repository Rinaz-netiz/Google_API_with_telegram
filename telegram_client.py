from telethon.sync import TelegramClient
from telethon import functions
from functools import wraps

from telethon.tl.types import InputUser
import os
from main import load_env

load_env()

api_id = os.getenv('API_ID_TELEGRAM')
api_hash = os.getenv('API_HASH_TELEGRAM')

client = TelegramClient(session='name', api_id=api_id, api_hash=api_hash)


def connect_to_client(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        client.start()
        client.connect()
        func(*args, **kwargs)
        client.disconnect()

    return wrapper


@connect_to_client
def _create_chat(name_chat: str, people_numbers: list) -> None:
    """Функция создает группу в telegarm"""
    users_to_chat = []
    for number in people_numbers:
        participant = client.get_entity(number).to_dict()
        users_to_chat.append(InputUser(user_id=participant['id'], access_hash=participant['access_hash']))

    # Создает чат
    client(functions.messages.CreateChatRequest(
        users=users_to_chat,
        title=name_chat
    ))

    print(f'Chat "{name_chat}" created')


@connect_to_client
def _add_user_to_chat(participant_number: str, name_chat: str) -> None:
    """Добавляет пользователя в чат"""
    participant_info = client.get_entity(participant_number).to_dict()
    chat_id = client.get_entity(name_chat).to_dict()

    client(functions.messages.AddChatUserRequest(chat_id=chat_id['id'], user_id=participant_info['id'],
                                                 fwd_limit=10))  # fwd_limit кол-во сообщений видных пользователю при входе
    print(f'{participant_number} user added in "{name_chat}" chat')


def _get_chats_data():
    """Функция забирает имена частов, где мы админ и участников меньше 10"""
    all_chats = client(functions.messages.GetAllChatsRequest(except_ids=[]))
    for dialog in all_chats.chats:
        chat = dialog.to_dict()
        if chat['_'] == 'Chat' and chat['creator'] and chat['participants_count'] < 10:
            yield chat['title']


@connect_to_client
def create_chat_and_add_users_telegram(chat_title: str, people_nums: list) -> None:
    """Функция добавляет в чат, если чат с таким именем существует или создает его"""
    for chat in _get_chats_data():
        if chat == chat_title:
            for people in people_nums:
                from telethon.errors.rpcerrorlist import UserAlreadyParticipantError
                try:
                    _add_user_to_chat(participant_number=people, name_chat=chat)
                except UserAlreadyParticipantError:
                    print(f'User: {people} already in the chat: {chat}')
                except Exception:
                    import traceback
                    client.send_message('me', f'{traceback.format_exc()} \n\n'
                                              f'number: {people} \nchat: {chat} ')
                    print(f'Number: {people} chat: {chat} \nNot added!!!', end='\n')
            break
    else:
        _create_chat(name_chat=chat_title, people_numbers=people_nums)

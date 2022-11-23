import datetime

from telethon.sync import TelegramClient
from telethon import functions
from functools import wraps
from telethon.errors.rpcerrorlist import UserAlreadyParticipantError, UserPrivacyRestrictedError
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
def _create_chat(name_chat: str, users_numbers: list) -> None:
    """Функция создает группу в telegarm"""
    users_to_chat = []
    for number in users_numbers:
        participant = client.get_entity(number).to_dict()
        users_to_chat.append(InputUser(user_id=participant['id'], access_hash=participant['access_hash']))

    # Создает чат
    client(functions.messages.CreateChatRequest(
        users=users_to_chat,
        title=name_chat
    ))

    # Добавление в чат фото
    chat_id = client.get_entity(name_chat).to_dict()['id']
    if not '_' == 'Chat':
        for chat in _get_chats_data():
            if chat['title'] == name_chat:
                chat_id = chat['chat_id']
    photo_load = client.upload_file('./photo/long_dark.jpg')
    client(functions.messages.EditChatPhotoRequest(
        chat_id=chat_id,
        photo=photo_load  # Фото, устанавливаемая в чат
    ))

    print(f'Chat "{name_chat}" created')


@connect_to_client
def _add_user_to_chat(chat_id: int, user_number: str) -> None:
    """Добавляет пользователя в чат"""
    participant_info = client.get_entity(user_number)
    client(functions.messages.AddChatUserRequest(chat_id=chat_id, user_id=participant_info.id,
                                                 fwd_limit=10))  # fwd_limit кол-во сообщений видных пользователю при входе


def _get_chats_data():
    """Функция забирает имена частов, где мы админ и участников меньше 10"""
    all_chats = client(functions.messages.GetAllChatsRequest(except_ids=[]))
    for dialog in all_chats.chats:
        chat = dialog.to_dict()
        if chat['_'] == 'Chat' and chat['creator']:
            yield {'title': chat['title'], 'chat_id': chat['id']}


@connect_to_client
def create_chat_and_add_users_telegram(chat_title: str, users_numbers: list) -> None:
    """Функция добавляет в чат, если чат с таким именем существует или создает его"""
    for chat in _get_chats_data():
        if chat['title'] == chat_title:
            for user in users_numbers:
                try:
                    _add_user_to_chat(chat_id=chat['chat_id'], user_number=user)
                    print(f'{user} user added in "{chat["title"]}" chat')
                except UserAlreadyParticipantError:
                    print(f'User: {user} already in the chat: {chat["title"]}')
                except UserPrivacyRestrictedError:
                    _create_invite_link(chat_id=chat['chat_id'], user_number=user)
                except Exception:
                    import traceback
                    client.send_message('@Rinaz0', f'{traceback.format_exc()} \n\n'
                                                   f'number: {user} \nchat: {chat} ')
                    client.send_message('me', f'number: {user} \nchat: {chat}')

                    print(f'Number: {user} chat: {chat["title"]} \nNot added!!!', end='\n')
            break
    else:
        _create_chat(name_chat=chat_title, users_numbers=users_numbers)


@connect_to_client
def _create_invite_link(chat_id, user_number: str) -> None:
    """Функция принемают id чата и создает инвайт сообщение"""
    today = str(datetime.date.today())
    invite_live = int(today[-2:].replace('0', '')) + 3
    invite_ink = client(functions.messages.ExportChatInviteRequest(
        peer=chat_id,
        legacy_revoke_permanent=None,
        request_needed=None,
        expire_date=datetime.datetime(2022, 11, invite_live, 0, 0, 0),
        usage_limit=50,
        title='My awesome title'
    ))
    client.send_message(user_number,
                        f'Мы не можем вас добавить в группу, поэтому вот ссылка: \n{invite_ink.link}')  # Лучше поменять сообщение

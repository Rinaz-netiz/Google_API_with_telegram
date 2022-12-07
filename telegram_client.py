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


def _get_entity_user(number: str, name_chat: str) -> InputUser:
    try:
        participant = client.get_entity(number).to_dict()
    except ValueError:
        send_traceback(user_number=number, chat_title=name_chat)
    else:
        return InputUser(user_id=participant['id'], access_hash=participant['access_hash'])


def _create_chat(name_chat: str, users_numbers: [list, str]) -> [dict, None]:
    """Функция создает группу в telegarm"""
    users_to_chat = []
    if isinstance(users_numbers, list):
        for number in users_numbers:
            users_to_chat.append(_get_entity_user(number=number, name_chat=name_chat))
    else:
        users_to_chat.append(_get_entity_user(number=users_numbers, name_chat=name_chat))

    if not users_to_chat:
        return None

    # Создает чат
    try:
        client(functions.messages.CreateChatRequest(
            users=users_to_chat,
            title=name_chat
        ))
    except TypeError:
        send_traceback(user_number=users_numbers, chat_title=name_chat)
    else:
        # Добавление в чат фото
        chat = _get_chats_data(chat_title=name_chat)
        chat_id = chat[name_chat]['chat_id']

        photo_load = client.upload_file('./photo/long_dark.jpg')
        client(functions.messages.EditChatPhotoRequest(
            chat_id=chat_id,
            photo=photo_load  # Фото, устанавливаемая в чат
        ))

        print(f'Chat "{name_chat}" created')

        return chat


def _add_user_to_chat(chat_id: int, chat_title: str, user_number: str) -> None:
    """Добавляет пользователя в чат"""
    try:
        participant_info = client.get_entity(user_number)
    except Exception:
        client.send_message('me', f"User '{user_number}' didn't add to chat: {chat_title}")
    else:
        try:
            client(functions.messages.AddChatUserRequest(chat_id=chat_id, user_id=participant_info.id,
                                                         fwd_limit=10))  # fwd_limit кол-во сообщений видных пользователю при входе
        except UserAlreadyParticipantError:
            pass
        except UserPrivacyRestrictedError:
            _create_invite_link(chat_id=chat_id, chat_title=chat_title, user_number=user_number)
        except Exception:
            send_traceback(user_number=user_number, chat_title=chat_title)


def _get_chats_data(chat_title=None) -> dict:
    """Функция забирает имена частов, где мы админ и участников меньше 10"""
    chats_data = {}
    all_chats = client(functions.messages.GetAllChatsRequest(except_ids=[]))

    if chat_title is None:
        for dialog in all_chats.chats:
            chat = dialog.to_dict()
            if chat['_'] == 'Chat' and chat['creator']:
                chats_data[chat['title']] = {'chat_id': chat['id'], 'participants_count': chat['participants_count']}
        return chats_data
    else:
        for dialog in all_chats.chats:
            chat = dialog.to_dict()
            if chat['_'] == 'Chat' and chat['creator'] and chat['title'] == chat_title:
                return {chat['title']: {'chat_id': chat['id'], 'participants_count': chat['participants_count']}}


@connect_to_client
def telegram_routing(data) -> None:
    """Вся логика происходит тут"""
    chat_data = {} | _get_chats_data()

    for information in data:
        if isinstance(information[0], str):
            if information[0] in chat_data.keys():
                for user in information[1]:
                    _add_user_to_chat(chat_id=chat_data[information[0]]['chat_id'], chat_title=information[0],
                                      user_number=user)
                    chat_data[information[0]]['participants_count'] += 1
            else:
                chat = _create_chat(name_chat=information[0], users_numbers=information[1])
                chat_data[information[0]] = chat[information[0]]  # Добавляет словарь забирая по названию чата
        else:
            chats = {}
            for chat in chat_data:
                if chat in information[0]:
                    chats[chat_data[chat]['participants_count']] = (chat_data[chat]['chat_id'], chat)

            if not chats:
                chat = _create_chat(name_chat=information[0][1], users_numbers=information[1])
                if chat:
                    chat_data[information[0][1]] = chat[information[0][1]]

            try:
                minn = min(chats.keys())
            except ValueError:
                client.send_message('me', f'User: {information[1]} do not add to {information[0]} (min() arg is an empty sequence)')
            else:
                _add_user_to_chat(chat_id=chats[minn][0], chat_title=chats[minn][1], user_number=information[1])
                chat_data[chats[minn][1]]['participants_count'] += 1

        for k, v in chat_data.items():
            if v['participants_count'] > 10:
                client.send_message('me', f'"{k}" chat is full (participants_count={v["participants_count"]})')

    client.send_message('Rinaz0', f'Success(day: {datetime.date.today()})')
    print(datetime.date.today(), end='\n\n')


def _create_invite_link(chat_id: int, chat_title: str, user_number: str) -> None:
    """Функция принемают id чата и создает инвайт сообщение"""
    today = str(datetime.date.today())
    year = int(today.split('-')[0])
    month = int(today.split('-')[1])
    day = int(today[-2:].replace('0', '')) + 3

    if day in [29, 30, 31]:
        month += 1
        day = 1
    try:
        invite_ink = client(functions.messages.ExportChatInviteRequest(
            peer=chat_id,
            legacy_revoke_permanent=None,
            request_needed=None,
            expire_date=datetime.datetime(year, month, day, 0, 0, 0),
            usage_limit=50,
            title='My awesome title'  # change this element
        ))
    except Exception:
        send_traceback(user_number=user_number, chat_title=chat_title)
    else:
        client.send_message(user_number,
                            f'Мы не можем вас добавить в группу, поэтому вот ссылка: '
                            f'\n{invite_ink.link}')  # Лучше поменять сообщение


def send_traceback(user_number: str, chat_title: str) -> None:
    import traceback

    try:
        client.send_message('@Rinaz0', f'{traceback.format_exc()} \n\n'
                                       f'number: {user_number} \nchat: {chat_title} ')
        client.send_message('me', f'number: {user_number} \nchat: {chat_title}')
    except ConnectionError:
        pass

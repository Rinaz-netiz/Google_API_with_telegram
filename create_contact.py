from __future__ import print_function
import os
from pprint import pprint
from typing import Dict

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from main import load_env

load_env()
CLIENT_SECRET_FILE = os.getenv('CLIENT_SECRET_FILE_CONTACT')
SCOPES_CONTACTS = ['https://www.googleapis.com/auth/contacts']


def _connection_test():
    """Проверяет токен подключение, при первом подключении создает файл подключения"""
    creds = None
    if os.path.exists(CLIENT_SECRET_FILE):
        creds = Credentials.from_authorized_user_file(CLIENT_SECRET_FILE, SCOPES_CONTACTS)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials/people_client_API.json', SCOPES_CONTACTS)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(CLIENT_SECRET_FILE, 'w') as token:
            token.write(creds.to_json())


def _connect_to_people_api(token_file: str):
    """Подключение к API"""
    try:
        creds = Credentials.from_authorized_user_file(token_file, SCOPES_CONTACTS)
        return build('people', 'v1', credentials=creds)
    except HttpError as err:
        print(err)


def create_batch_contacts(names_and_numbers: list) -> None:
    """Отправляет контакты все за нескоько запросов"""
    run_multiple_times(data_in_list=names_and_numbers)


def run_multiple_times(data_in_list: list) -> None:
    """Делает запрос определенное кол-во раз, по 200 контактов за раз"""
    range_list = len(data_in_list)
    if range_list > 200:
        import math
        how_many_times = math.ceil(range_list / 200)
        start_range = 0
        end_range = range_list - ((how_many_times - 1) * 200)
        while how_many_times != 0:
            _create_contacts(names_and_numbers=data_in_list[start_range:end_range])
            start_range = end_range
            end_range += 200
            how_many_times -= 1
    else:
        _create_contacts(names_and_numbers=data_in_list)


def _create_contacts(names_and_numbers: list) -> None:
    """Функция создает несколько контаков за раз"""
    service = _connect_to_people_api(CLIENT_SECRET_FILE)

    ready_persons = []
    for person in names_and_numbers:
        ready_persons.append(preparation_contact(person))

    service.people().batchCreateContacts(body={"contacts": ready_persons}).execute()
    print('Контакты добавлены')


def preparation_contact(name_and_numbers: dict) -> Dict:
    return {
            "contactPerson": {
                'names': [{
                    "givenName": name_and_numbers['name']
                }],
                "phoneNumbers": name_and_numbers['numbers'],
            }
        }


def create_contact(name: str, number: [list, str]) -> None:
    """Функция подключается к google и созает контакт"""
    service = _connect_to_people_api(CLIENT_SECRET_FILE)

    if isinstance(number, list):
        contacts = []
        for i in number:
            contacts.insert(-1, {
                'type': 'numbers_in_API',
                'value': i
            })
    else:
        contacts = {
                'type': 'numbers_in_API',
                'value': number
            }

    service.people().createContact(body={
        "names": [
            {
                "givenName": name
            }
        ],
        "phoneNumbers": contacts,

    }).execute()
    print('Контакт создан')

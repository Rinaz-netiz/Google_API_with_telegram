import json
from typing import List
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
from main import load_env
import os
from collections import defaultdict

load_env()
CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE_SHEETS')
SCOPES_SHEETS = ['https://www.googleapis.com/auth/spreadsheets',
                 'https://www.googleapis.com/auth/drive']


def _connect_to_sheets():
    cred = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPES_SHEETS)
    httpAuth = cred.authorize(httplib2.Http())
    return build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API


def _get_values(start: str, end: str, spreadsheetId: str) -> List:
    """Функция получает значение из таблицы"""
    service = _connect_to_sheets()
    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId,
        range=f'{start.upper()}:{end.upper()}',
        majorDimension='ROWS'
    ).execute()

    _data = values['values'][1:]
    try:
        #  Сравнивание последней строки с новыми строками из таблиц
        with open('last_element.json', encoding='utf-8') as file:
            connect_to_products = json.loads(file.read())

        if connect_to_products['data'] == values['values'][-1] and\
                connect_to_products['spreadsheetId'] == spreadsheetId:

            _data = values["values"][connect_to_products['count'] + 1:]
    except FileNotFoundError:
        pass

    # Запись последней строк
    for_write_last_element = {'count': len(values["values"][1:]),
                              'data': values['values'][-1],
                              'spreadsheetId': spreadsheetId}
    with open('last_element.json', 'w', encoding='utf-8') as f:
        json.dump(for_write_last_element, f, ensure_ascii=False, indent=4)

    return _data


def _clean_number(_number: str) -> str:
    """Производится привод номеров в правильный вид"""
    if _number[0] in '0123456789' and _number[0] != '+':
        if _number[0] == '8':
            _number = '+7' + _number[1:]
        elif _number[0] == '9':
            _number = '+7' + _number
        elif _number[0] == '7':
            _number = '+' + _number
        elif _number[0] != '+':
            _number = '+' + _number[1:]

    if _number[0] == '+':
        if ' ' in _number:
            _number = _number.replace(' ', '')
        if '-' in _number:
            _number = _number.replace('-', '')
        if '(' in _number or ')' in _number:
            _number = _number.replace('(', '').replace(')', '')
    return _number


def _clean_data(content: list) -> List:
    """Преобразование данных в словарь"""
    data_in_sheets = []
    for data in content:
        school = data[1].split(' ')[0]
        if school == 'Клуб':
            school = data[1].split('(')[-1].replace(')', '')  # можно переделать, чтоб к-с не было
        name = data[2]
        class_at_school = data[3] + data[4]
        number = _clean_number(_number=data[5])
        try:
            if data[6] != '':
                number = [number, _clean_number(_number=data[6])]
        except IndexError:
            pass
        numbers = number

        ###########################
        week_days = data[9]
        hours = data[10]
        ###########################

        data_in_sheets.append({
            'school': f'№{school}',
            'name': name,
            'class_at_school': class_at_school,
            'numbers': numbers,
            'sorted_for_school_week_hours': f'№{school} {week_days} {hours}'
        })
    return data_in_sheets


def sheets_get_data(start: str, end: str, spreadsheetId: str) -> List:
    """Основная функция, получающая и отдающая данные"""
    data = _get_values(start=start, end=end, spreadsheetId=spreadsheetId)
    return _clean_data(content=data)


def sorted_data_from_sheets(data):
    """Функция сортирует данные и собирает их в список"""
    school_number_and_phones = defaultdict(list)
    for i in data:
        if isinstance(i['numbers'], list):
            school_number_and_phones[i["sorted_for_school_week_hours"]].append(i['numbers'][-1])
        else:
            school_number_and_phones[i["sorted_for_school_week_hours"]].append(i['numbers'])
    return school_number_and_phones.items()

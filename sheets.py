import json
from pprint import pprint
from typing import List

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
from main import load_env
import os

load_env()
CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE_SHEETS')
SCOPES_SHEETS = ['https://www.googleapis.com/auth/spreadsheets',
                 'https://www.googleapis.com/auth/drive']


def _connect_to_sheets():
    cred = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPES_SHEETS)
    httpAuth = cred.authorize(httplib2.Http())
    return build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API


def get_values(start: str, end: str, spreadsheetId: str) -> List:
    """Функция получает значение из таблицы"""
    service = _connect_to_sheets()
    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId,
        range=f'{start.upper()}:{end.upper()}',
        majorDimension='ROWS'
    ).execute()
    pprint(values)
    # pprint(values)
    return values['values']


if __name__ == '__main__':
     # Имя файла с закрытым ключом, вы должны подставить свое
    spreadsheetId = os.getenv('SPREAD_SHEET_ID')

    get_values('a1', 'e18', spreadsheetId)

# with open('data.json', 'w', encoding='utf-8') as file:
#     json.dump(values['values'], file, ensure_ascii=False, indent=4)



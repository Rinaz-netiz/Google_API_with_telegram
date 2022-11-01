from create_contact import create_contact
from sheets import get_values
from telegram_client import create_chat_and_add_users_telegram

from main import load_env
import os

load_env()
spreadsheetId = os.getenv('SPREAD_SHEET_ID')


def main():
    table_data = get_values(start='A1', end='E18', spreadsheetId=spreadsheetId)
    create_contact(name=table_data[-1][1], number=f'+{table_data[-1][3]}')
    create_chat_and_add_users_telegram('Testing create chat', people_numbers=[f'+{table_data[-1][3]}'])
    print('Успех')


if __name__ == '__main__':
    ...

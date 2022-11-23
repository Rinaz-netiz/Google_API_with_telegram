from create_contact import create_batch_contacts
from sheets import sheets_get_data, sorted_data_from_sheets
from telegram_client import create_chat_and_add_users_telegram
import os
from main import load_env
import schedule

load_env()
spreadsheetId = os.getenv('SPREAD_SHEET_ID')


def main() -> None:
    """Делается запрос в таблицы, сохранение в контакты и создыние чатов телеграм"""
    table_data = sheets_get_data(start='A1', end='k2000', spreadsheetId=spreadsheetId)  # end='' можно не менять
    create_batch_contacts(names_and_numbers=table_data)

    for i in sorted_data_from_sheets(table_data):
        chat_name, people = i
        create_chat_and_add_users_telegram(chat_name, people)


schedule.every().day.at("00:00").do(main)


if __name__ == '__main__':
    while True:
        schedule.run_pending()

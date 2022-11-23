from pprint import pprint
from create_contact import create_batch_contacts
from sheets import sheets_get_data, sorted_data_from_sheets
from telegram_client import create_chat_and_add_users_telegram

from main import load_env
import schedule

load_env()
spreadsheetId = '1LBtslCJOdLCIDr8Cd2U1atAncJpsOhL4koP270-twTk'


def main() -> None:
    """Делается запрос в таблицы, сохранение в контакты и создыние чатов телеграм"""
    table_data = sheets_get_data(start='A1', end='k2000', spreadsheetId=spreadsheetId)  # end='' можно не менять
    create_batch_contacts(names_and_numbers=table_data)

    for i in sorted_data_from_sheets(table_data):
        chat_name, people = i
        # print(f'Chat name: {chat_name} and people: {people}')
        create_chat_and_add_users_telegram(chat_name, people)

    # print('Успех')


schedule.every().day.at("00:00").do(main)


if __name__ == '__main__':
    # sorted_data_from_sheets(sheets_get_data(start='A1', end='g6', spreadsheetId=spreadsheetId))
    # sorted_data_from_sheets(sheets_get_data(start='A1', end='k2000', spreadsheetId=spreadsheetId))  # i856
    while True:
        schedule.run_pending()

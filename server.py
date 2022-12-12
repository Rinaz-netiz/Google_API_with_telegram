import time
from create_contact import create_batch_contacts
from sheets import sheets_get_data, sorted_data_from_sheets
from telegram_client import telegram_routing
import os
from main import load_env
import schedule

load_env()
spreadsheetId = os.getenv('SPREAD_SHEET_ID')


def main() -> None:
    """Делается запрос в таблицы, сохранение в контакты и создыние чатов телеграм"""
    table_data = sheets_get_data(start='A1', end='av2000', spreadsheetId=spreadsheetId)  # end='' можно не менять
    print(table_data)

    if table_data:
        create_batch_contacts(names_and_numbers=table_data)
        telegram_routing(data=sorted_data_from_sheets(table_data))


schedule.every().day.at("00:00").do(main)


if __name__ == '__main__':
    main()
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

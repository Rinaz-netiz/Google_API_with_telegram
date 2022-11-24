Этот скрипт позволяет загружать данные из google sheets и сохранять их в
google contacts и параллельно создавать группы в телеграмме

Что нужно для начала испльзования этого скрипта:
1) Создать .env файл и поместить туда следующее:
    # Ключи telegram_client
    API_ID_TELEGRAM=  --api_id телеграма
    
    API_HASH_TELEGRAM=  --api_hash телеграма

    # Ключи sheets
    SPREAD_SHEET_ID=  -- здесь должен быть id google sheets
    
    CREDENTIALS_FILE_SHEETS=  --ключи от google в .json

    # Ключи create_contact
    CLIENT_SECRET_FILE_CONTACT=  --ключи от google в .json
2) Запустить
Каждые 24 часа он будет срабатывать(по умолчанию в 00:00(можно изменить))

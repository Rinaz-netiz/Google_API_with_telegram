def load_env() -> None:
    """Функция проверят и поключает ключи из .env"""
    from dotenv import load_dotenv
    import os

    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

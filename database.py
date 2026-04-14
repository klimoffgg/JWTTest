import pickle
import os
from typing import Any


class Database:
    """
    Простая база данных на основе словаря с сохранением в файл через pickle
    """

    def __init__(self, filename: str = "database.pkl"):
        """
        Инициализация базы данных

        Args:
            filename: имя файла для хранения данных
        """
        self.filename = filename
        self.data: dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Загружает данные из файла"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'rb') as f:
                    self.data = pickle.load(f)
                print(f"[OK] Данные загружены из {self.filename}")
            except (EOFError, pickle.PickleError) as e:
                print(f"[ERROR] Ошибка загрузки данных: {e}")
                self.data = {}
        else:
            print(f"[INFO] Файл {self.filename} не найден, создана новая БД")
            self.data = {}

    def save(self) -> None:
        """Сохраняет данные в файл"""
        try:
            with open(self.filename, 'wb') as f:
                pickle.dump(self.data, f)
            print(f"[OK] Данные сохранены в {self.filename}")
        except Exception as e:
            print(f"[ERROR] Ошибка сохранения: {e}")

    def set(self, key: str, value: Any) -> None:
        """
        Добавляет или обновляет значение по ключу

        Args:
            key: ключ
            value: значение
        """
        self.data[key] = value
        self.save()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Получает значение по ключу

        Args:
            key: ключ
            default: значение по умолчанию, если ключ не найден

        Returns:
            значение или default
        """
        return self.data.get(key, default)

    def delete(self, key: str) -> bool:
        """
        Удаляет ключ из базы данных

        Args:
            key: ключ для удаления

        Returns:
            True если удалено, False если ключ не найден
        """
        if key in self.data:
            del self.data[key]
            self.save()
            return True
        return False

    def exists(self, key: str) -> bool:
        """Проверяет существует ли ключ"""
        return key in self.data

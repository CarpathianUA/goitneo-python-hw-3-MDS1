import os
import pickle
from collections import UserDict, defaultdict
from datetime import datetime

from modules.bot_assistant.constants.file_paths import ADDRESS_BOOK_FILE
from modules.bot_assistant.constants.weekend_days import WEEKEND_DAYS
from modules.bot_assistant.models.exceptions import (
    InvalidPhoneError,
    InvalidBirthdayFormatError,
)
from modules.bot_assistant.utils.birthdays import is_valid_birth_date
from modules.bot_assistant.utils.phone_numbers import is_valid_phone


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not self._validate_phone(value):
            raise InvalidPhoneError
        self._value = value

    @staticmethod
    def _validate_phone(phone):
        return is_valid_phone(phone)


class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value is not None and not self._validate_birthday(value):
            raise InvalidBirthdayFormatError
        self._value = value

    @staticmethod
    def _validate_birthday(birthday):
        return is_valid_birth_date(birthday)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = list()
        self.birthday = Birthday(None)

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, phone, new_phone):
        for p in self.phones:
            if p.value == phone:
                p.value = new_phone

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def get_birthday(self):
        if self.birthday and self.birthday.value:
            return self.birthday.value

    def __str__(self):
        phones_str = (
            "; ".join(p.value for p in self.phones)
            if self.phones
            else "No phones available"
        )
        birthday_str = (
            self.birthday.value
            if self.birthday and self.birthday.value
            else "No birthday available"
        )
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {birthday_str}"


class AddressBook(UserDict):
    def __is_key_exist(self, key):
        return key in self.data

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        if not self.__is_key_exist(name):
            raise ValueError(f"Contact '{name}' doesn't exist.")
        return self.data[name]

    def delete(self, name):
        if not self.__is_key_exist(name):
            raise ValueError(f"Contact '{name}' doesn't exist.")
        self.data.pop(name, None)
        return f"Contact '{name}' has been deleted."

    def get_birthdays_per_week(self):
        today = datetime.today().date()
        birthdays = defaultdict(list)

        for record in self.data.values():
            self.process_record_for_birthday(record, today, birthdays)

        return birthdays

    def process_record_for_birthday(self, record, today, birthdays):
        name = record.name.value
        birthday_date = self.get_upcoming_birthday(record, today)
        if birthday_date is None:
            return

        delta_days = (birthday_date - today).days

        if delta_days < 7:
            day_to_say_happy_birthday = self.get_birthday_wish_day(today, birthday_date)
            birthdays[day_to_say_happy_birthday].append(name)

    @staticmethod
    def get_upcoming_birthday(record, today):
        if not record.birthday or not record.birthday.value:
            return None

        # Assuming birthday date is stored as a string in 'DD.MM.YYYY' format
        birthday_str = record.birthday.value

        # Convert the birthday string to a datetime object
        # Adjust the format if necessary
        birthday_date = datetime.strptime(
            birthday_str, "%d.%m.%Y"
        ).date()  # Convert to date here

        # Set the time to midnight (not necessary since it's already a date object)
        # birthday_date = birthday_date.replace(hour=0, minute=0, second=0, microsecond=0)

        birthday_this_year = birthday_date.replace(year=today.year)
        if birthday_this_year < today:
            birthday_this_year = birthday_date.replace(year=today.year + 1)

        return birthday_this_year

    @staticmethod
    def get_birthday_wish_day(today, birthday_date):
        print("today", today.weekday())
        print("birthday", birthday_date.weekday())
        if birthday_date.weekday() in WEEKEND_DAYS:
            return "Monday"
        elif birthday_date.weekday() == today.weekday():
            return "Today"
        else:
            return birthday_date.strftime("%A")

    def save_to_file(self):
        with open(ADDRESS_BOOK_FILE, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load_from_file(cls):
        if os.path.exists(ADDRESS_BOOK_FILE):
            with open(ADDRESS_BOOK_FILE, "rb") as f:
                return pickle.load(f)
        return cls()

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())

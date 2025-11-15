from __future__ import annotations

from datetime import datetime
from typing import Final

from app.model.errors import PhoneFormatError, EmailFormatError

DATE_FORMAT: Final[str] = '%d.%m.%Y'

class Field:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other: Field) -> bool:
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value: str):
        super().__init__(value)

class Address(Field):
    def __init__(self, value: str):
        super().__init__(value)

class Birthday(Field):
    def __init__(self, date: str):
        try:
            super().__init__(datetime.strptime(date, DATE_FORMAT).date())
        except ValueError:
            raise ValueError("❌ Invalid date format! Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime(DATE_FORMAT)

class Phone(Field):
    def __init__(self, value: str):
        self.__validate_phone(value)
        super().__init__(value)

    def __validate_phone(self, phone):
        if not phone.isdigit():
            raise PhoneFormatError("❌ Phone number should contain digits only!")
        if len(phone) != 10:
            raise PhoneFormatError("❌ Phone number should contain exactly 10 digits!")

class Email(Field):
    def __init__(self, value: str):
        self.__validate_email(value)
        super().__init__(value)

    def __validate_email(self, email):
        if '@' not in email or '.' not in email.split('@')[-1]:
            raise EmailFormatError("❌ Invalid email format! Email should contain '@' and domain with '.'")
        if email.count('@') != 1:
            raise EmailFormatError("❌ Invalid email format! Email should contain exactly one '@' symbol")

class Note(Field):
    def __init__(self, value: str):
        super().__init__(value)




from app.model.record_fields import *


class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.address = None
        self.birthday = None
        self.phones = []
        self.emails = []
        self.note = None

    def add_address(self, address: str) -> None:
        self.address = Address(address)

    def edit_address(self, new_address: str) -> None:
        self.address = Address(new_address)

    def remove_address(self) -> None:
        self.address = None

    def add_birthday(self, date: str) -> None:
        self.birthday = Birthday(date)

    def add_phone(self, phone: str) -> None:
        self.phones.append(Phone(phone))

    def add_email(self, email: str) -> None:
        self.emails.append(Email(email))

    def find_email(self, email_str: str) -> Email | None:
        for email in self.emails:
            if email.value == email_str:
                return email
        return None

    def edit_email(self, old_email_str: str, new_email_str: str) -> None:
        for i, email in enumerate(self.emails):
            if email.value == old_email_str:
                self.emails[i] = Email(new_email_str)

    def remove_email(self, email_str: str) -> None:
        self.emails.remove(Email(email_str))

    def find_phone(self, phone_str: str) -> Phone | None:
        for phone in self.phones:
            if phone.value == phone_str:
                return phone
        return None

    def edit_phone(self, old_phone_str: str, new_phone_str: str) -> None:
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone_str:
                self.phones[i] = Phone(new_phone_str)

    def remove_phone(self, phone_str: str) -> None:
        self.phones.remove(Phone(phone_str))

    def __str__(self):
        result_str = f"Contact name: {self.name.value}, phone(s): {', '.join(p.value for p in self.phones)}"
        if self.emails:
            result_str += f", email(s): {', '.join(e.value for e in self.emails)}"
        if self.birthday:
            result_str += f", birthday: {self.birthday}"
        if self.address:
            result_str += f", address: {self.address}"
        return result_str
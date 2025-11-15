from collections import UserDict

from app.model.record import Record


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str) -> Record:
        return self.get(name)

    def delete(self, name):
        del self.data[name]
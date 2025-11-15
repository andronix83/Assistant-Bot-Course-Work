import json

from app.model.address_book import AddressBook

JSON_FILE_NAME = "data/address_book.json"
JSON_FILE_ENCODING = "utf-8"


def save_address_book(address_book: AddressBook) -> None:
    with open(JSON_FILE_NAME, 'w', encoding=JSON_FILE_ENCODING) as f:
        json.dump(address_book.to_dict(), f, ensure_ascii=False, indent=2)

def load_address_book() -> AddressBook:
    try:
        with open(JSON_FILE_NAME, 'r', encoding=JSON_FILE_ENCODING) as f:
            data = json.load(f)
            return AddressBook.from_dict(data)
    except FileNotFoundError:
        # when open for the first time or file is missing
        return AddressBook()

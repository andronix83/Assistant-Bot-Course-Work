from collections import UserDict
from typing import Dict, Any

from app.model.record import Record
from app.model.record_fields import Note, DATE_FORMAT


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str) -> Record:
        return self.get(name)

    def delete(self, name):
        del self.data[name]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert AddressBook to a dictionary for JSON serialization."""
        result = {"records": []}
        for name, record in self.data.items():
            record_dict = {
                "name": record.name.value,
                "phones": [phone.value for phone in record.phones],
                "emails": [email.value for email in record.emails],
            }
            
            if record.address:
                record_dict["address"] = record.address.value
                
            if record.birthday:
                record_dict["birthday"] = record.birthday.value.strftime(DATE_FORMAT)
                
            if record.note:
                record_dict["note"] = record.note.value
                
            result["records"].append(record_dict)
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AddressBook':
        """Restore saved AddressBook from a dictionary."""
        address_book = cls()
        for record_data in data.get("records", []):
            name = record_data.get("name")
            if not name:
                continue  # Skip records without a name
                
            record = Record(name)
            
            # Add phones
            if "phones" in record_data:
                for phone in record_data["phones"]:
                    record.add_phone(phone)
            
            # Add emails
            if "emails" in record_data:
                for email in record_data["emails"]:
                    record.add_email(email)
            
            # Add address
            if "address" in record_data and record_data["address"]:
                record.add_address(record_data["address"])
            
            # Add birthday
            if "birthday" in record_data and record_data["birthday"]:
                record.add_birthday(record_data["birthday"])
            
            # Add note
            if "note" in record_data and record_data["note"]:
                record.note = Note(record_data["note"])
            
            address_book.add_record(record)
        return address_book

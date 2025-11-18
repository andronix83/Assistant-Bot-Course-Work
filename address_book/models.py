"""
Data models for the address book application using Pydantic.
"""

import re
from datetime import date, datetime
from typing import List, Optional, Dict

from pydantic import BaseModel, Field, field_validator, ConfigDict, EmailStr


class Record(BaseModel):
    """
    Represents a contact record in the address book.
    """
    model_config = ConfigDict(
        json_encoders={
            date: lambda v: v.strftime("%d.%m.%Y")
        }
    )
    
    name: str = Field(..., description="Unique name of the contact")
    address: Optional[str] = Field(None, description="Contact address")
    birthday: Optional[date] = Field(None, description="Contact birthday in date format")
    phones: List[str] = Field(default_factory=list, description="List of phone numbers")
    emails: List[EmailStr] = Field(default_factory=list, description="List of email addresses")
    note: Optional[str] = Field(None, description="Notes about the contact, can contain tags starting with @")

    @field_validator('phones')
    @classmethod
    def validate_phones(cls, v):
        """Validate phone numbers."""
        for phone in v:
            if not re.match(r'^\d{10,15}$', phone):
                raise ValueError(f"Invalid phone number format: {phone}")
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate name is not empty."""
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class AddressBook(BaseModel):
    """
    Represents the address book containing multiple records.
    """
    records: Dict[str, Record] = Field(default_factory=dict, description="Dictionary of records with name as key")

    def add_record(self, record: Record) -> None:
        """Add a record to the address book."""
        self.records[record.name] = record

    def delete_record(self, name: str) -> bool:
        """Delete a record by name. Returns True if deleted, False if not found."""
        if name in self.records:
            del self.records[name]
            return True
        return False

    def find_record(self, name: str) -> Optional[Record]:
        """Find a record by name."""
        return self.records.get(name)

    def get_all_records(self) -> List[Record]:
        """Get all records as a list."""
        return list(self.records.values())

    def find_by_tag(self, tag: str) -> List[Record]:
        """Find records that contain a specific tag in their notes."""
        # Ensure tag starts with @
        if not tag.startswith('@'):
            tag = f'@{tag}'
        
        results = []
        for record in self.records.values():
            if record.note and tag in record.note:
                results.append(record)
        return results

    def find_any(self, text: str) -> List[Record]:
        """Find records that contain the text in any field."""
        text = text.lower()
        results = []
        
        for record in self.records.values():
            # Check name
            if text in record.name.lower():
                results.append(record)
                continue
                
            # Check address
            if record.address and text in record.address.lower():
                results.append(record)
                continue
                
            # Check note
            if record.note and text in record.note.lower():
                results.append(record)
                continue
                
            # Check phones
            for phone in record.phones:
                if text in phone:
                    results.append(record)
                    break
            else:
                # Check emails
                for email in record.emails:
                    if text in email.lower():
                        results.append(record)
                        break
        
        return results

    def get_upcoming_birthdays(self, days: int = 7) -> List[tuple]:
        """Get records with birthdays in the next N days."""
        today = date.today()
        results = []
        
        for record in self.records.values():
            if record.birthday:
                # Create birthday for current year
                birthday_this_year = record.birthday.replace(year=today.year)
                
                # If birthday has passed this year, check next year
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                
                # Calculate days until birthday
                days_until = (birthday_this_year - today).days
                
                if 0 <= days_until <= days:
                    results.append((record, days_until))
        
        # Sort by days until birthday
        results.sort(key=lambda x: x[1])
        return results

    @classmethod
    def from_json(cls, data: dict) -> 'AddressBook':
        """Create AddressBook from JSON data."""
        records_data = data.get("records", [])
        records = {}
        
        for record_data in records_data:
            # Parse birthday if present
            if "birthday" in record_data and record_data["birthday"]:
                try:
                    record_data["birthday"] = datetime.strptime(record_data["birthday"], "%d.%m.%Y").date()
                except ValueError:
                    record_data["birthday"] = None
            
            # Create record
            record = Record(**record_data)
            records[record.name] = record
        
        return cls(records=records)

    def to_json(self) -> dict:
        """Convert AddressBook to JSON-serializable dict."""
        records_data = []
        
        for record in self.records.values():
            record_dict = record.model_dump()
            # Format birthday as string if present
            if record_dict.get("birthday"):
                record_dict["birthday"] = record.birthday.strftime("%d.%m.%Y")
            records_data.append(record_dict)
        
        return {"records": records_data}


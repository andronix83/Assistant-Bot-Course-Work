"""
Command handlers for the address book application.
Implements all the required CLI commands.
"""

import random
from datetime import datetime
from typing import List, Tuple, Optional

from .file_operations import save_address_book
from .models import AddressBook, Record
from .settings import Settings


def handle_hello(settings: Settings) -> str:
    """
    Handle the hello command.
    
    Args:
        settings: Application settings
        
    Returns:
        Random greeting message
    """
    return random.choice(settings.greetings)


def handle_all(address_book: AddressBook) -> List[Record]:
    """
    Handle the all command.
    
    Args:
        address_book: The address book
        
    Returns:
        List of all records
    """
    return address_book.get_all_records()


def handle_add(address_book: AddressBook, name: str, **kwargs) -> Tuple[bool, str]:
    """
    Handle the add command.
    
    Args:
        address_book: The address book
        name: Name of the contact (required)
        **kwargs: Optional fields (address, birthday, phone, email, note)
        
    Returns:
        Tuple of (success, message)
    """
    # Check if record with this name already exists
    if address_book.find_record(name):
        return False, f"Contact with name '{name}' already exists."
    
    # Process phones
    phones = []
    if 'phone' in kwargs:
        if isinstance(kwargs['phone'], list):
            phones = kwargs['phone']
        else:
            phones = [kwargs['phone']]
    
    # Process emails
    emails = []
    if 'email' in kwargs:
        if isinstance(kwargs['email'], list):
            emails = kwargs['email']
        else:
            emails = [kwargs['email']]
    
    # Process birthday
    birthday = None
    if 'birthday' in kwargs:
        try:
            birthday = datetime.strptime(kwargs['birthday'], "%d.%m.%Y").date()
        except ValueError:
            return False, f"Invalid birthday format. Use DD.MM.YYYY format."
    
    # Create new record
    try:
        record = Record(
            name=name,
            address=kwargs.get('address'),
            birthday=birthday,
            phones=phones,
            emails=emails,
            note=kwargs.get('note')
        )
        
        address_book.add_record(record)
        return True, f"Contact '{name}' added successfully."
    except Exception as e:
        return False, f"Error adding contact: {str(e)}"


def handle_delete(address_book: AddressBook, name: str) -> Tuple[bool, str]:
    """
    Handle the delete command.
    
    Args:
        address_book: The address book
        name: Name of the contact to delete
        
    Returns:
        Tuple of (success, message)
    """
    if address_book.delete_record(name):
        return True, f"Contact '{name}' deleted successfully."
    else:
        return False, f"Contact '{name}' not found."


def handle_edit(address_book: AddressBook, name: str, **kwargs) -> Tuple[bool, str]:
    """
    Handle the edit command.
    
    Args:
        address_book: The address book
        name: Name of the contact to edit
        **kwargs: Edit operations
        
    Returns:
        Tuple of (success, message)
    """
    record = address_book.find_record(name)
    if not record:
        return False, f"Contact '{name}' not found."
    
    try:
        # Handle address operations
        if 'set-address' in kwargs:
            record.address = kwargs['set-address']
        
        # Handle birthday operations
        if 'set-birthday' in kwargs:
            try:
                record.birthday = datetime.strptime(kwargs['set-birthday'], "%d.%m.%Y").date()
            except ValueError:
                return False, f"Invalid birthday format. Use DD.MM.YYYY format."
        
        # Handle note operations
        if 'set-note' in kwargs:
            record.note = kwargs['set-note']
        
        # Handle phone operations
        if 'add-phone' in kwargs:
            phones_to_add = kwargs['add-phone']
            if isinstance(phones_to_add, list):
                record.phones.extend(phones_to_add)
            else:
                record.phones.append(phones_to_add)
        
        if 'delete-phone' in kwargs:
            phones_to_delete = kwargs['delete-phone']
            if isinstance(phones_to_delete, list):
                for phone in phones_to_delete:
                    if phone in record.phones:
                        record.phones.remove(phone)
            else:
                if phones_to_delete in record.phones:
                    record.phones.remove(phones_to_delete)
        
        # Handle email operations
        if 'add-email' in kwargs:
            emails_to_add = kwargs['add-email']
            if isinstance(emails_to_add, list):
                record.emails.extend(emails_to_add)
            else:
                record.emails.append(emails_to_add)
        
        if 'delete-email' in kwargs:
            emails_to_delete = kwargs['delete-email']
            if isinstance(emails_to_delete, list):
                for email in emails_to_delete:
                    if email in record.emails:
                        record.emails.remove(email)
            else:
                if emails_to_delete in record.emails:
                    record.emails.remove(emails_to_delete)
        
        return True, f"Contact '{name}' updated successfully."
    except Exception as e:
        return False, f"Error updating contact: {str(e)}"


def handle_find(address_book: AddressBook, name: str) -> Optional[Record]:
    """
    Handle the find command.
    
    Args:
        address_book: The address book
        name: Name of the contact to find
        
    Returns:
        Record if found, None otherwise
    """
    return address_book.find_record(name)


def handle_find_tag(address_book: AddressBook, tag: str) -> List[Record]:
    """
    Handle the find-tag command.
    
    Args:
        address_book: The address book
        tag: Tag to search for
        
    Returns:
        List of records containing the tag
    """
    return address_book.find_by_tag(tag)


def handle_find_any(address_book: AddressBook, text: str) -> List[Record]:
    """
    Handle the find-any command.
    
    Args:
        address_book: The address book
        text: Text to search for
        
    Returns:
        List of records containing the text
    """
    return address_book.find_any(text)


def handle_birthdays(address_book: AddressBook, days: int = 7) -> List[Tuple[Record, int]]:
    """
    Handle the birthdays command.
    
    Args:
        address_book: The address book
        days: Number of days ahead to check
        
    Returns:
        List of tuples (record, days_until_birthday)
    """
    return address_book.get_upcoming_birthdays(days)


def handle_help(command: Optional[str] = None) -> str:
    """
    Handle the help command.
    
    Args:
        command: Optional specific command to get help for
        
    Returns:
        Help message
    """
    help_text = {
        None: """
Available commands:
- hello, hi: Greet the user with a random message
- all: Display all saved contacts
- add <name> [options]: Add a new contact
- delete <name>: Delete a contact
- edit <name> [options]: Edit a contact
- find <name>: Find a specific contact
- find-tag <tag>: Find contacts with a specific tag
- find-any <text>: Find contacts containing any text
- birthdays [days]: Show upcoming birthdays (default: 7 days)
- help [command]: Show help for commands
- exit, close: Exit the application

Use 'help <command>' for more information on a specific command.
        """,
        "add": """
Add a new contact:
add <name> [options]

Options:
- -address <address>: Set the address
- -phone <phone>: Add a phone number (can be used multiple times)
- -email <email>: Add an email address (can be used multiple times)
- -birthday <DD.MM.YYYY>: Set the birthday
- -note <note>: Add a note with optional tags (@tag)

Examples:
- add John_Doe -address '125 Main St, City' -phone 1234567890 -phone 1234567899 -email john1@example.com -birthday 30.12.1983
- add "Jane Smith" -phone 9876543210 -note "She is my @schoolmate"
- add 'Bill James' -email bjames1@thecompany.com -birthday 08.11.1992 -email bjames2@thecompany.com
        """,
        "delete": """
Delete a contact:
delete <name>

Example:
- delete John_Doe
        """,
        "edit": """
Edit a contact:
edit <name> [options]

Options:
- -set-address <address>: Set the address
- -set-birthday <DD.MM.YYYY>: Set the birthday
- -set-note <note>: Set the note
- -add-phone <phone>: Add a phone number (can be used multiple times)
- -delete-phone <phone>: Delete a phone number (can be used multiple times)
- -add-email <email>: Add an email address (can be used multiple times)
- -delete-email <email>: Delete an email address (can be used multiple times)

Examples:
- edit John_Doe -delete-phone 1234567890 -add-phone 1234567899
- edit 'Jane Smith' -set-address '125 Main St, City' -set-birthday 30.12.1983 -delete-email jane@home.com -delete-phone 0123456789
- edit "Lucy Atkins" -set-note "She is an @awesome person!"
        """,
        "find": """
Find a specific contact:
find <name>

Example:
- find John_Doe
        """,
        "find-tag": """
Find contacts with a specific tag:
find-tag <tag>

The tag can be specified with or without the @ symbol.

Example:
- find-tag schoolmate
- find-tag @schoolmate
        """,
        "find-any": """
Find contacts containing any text:
find-any <text>

Searches across all fields including name, address, note, phones, and emails.

Example:
- find-any john
- find-any 123456
- find-any @good
        """,
        "birthdays": """
Show upcoming birthdays:
birthdays [days]

Shows contacts with birthdays in the next N days (default: 7).

Examples:
- birthdays
- birthdays 14
        """
    }
    
    return help_text.get(command, f"No help available for command: {command}")


def handle_exit(address_book: AddressBook, settings: Settings) -> str:
    """
    Handle the exit command.
    
    Args:
        address_book: The address book
        settings: Application settings
        
    Returns:
        Farewell message
    """
    # Save data before exiting
    if save_address_book(address_book, settings):
        return random.choice(settings.farewells)
    else:
        return "Error saving data. Data may be lost."
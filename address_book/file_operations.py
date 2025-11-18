"""
File operations for the address book application.
Handles loading and saving data to/from JSON files.
"""

import json
import os

from .models import AddressBook
from .settings import Settings


def load_address_book(settings: Settings) -> AddressBook:
    """
    Load address book from JSON file.
    
    Args:
        settings: Application settings containing the data file path
        
    Returns:
        AddressBook instance with loaded data or empty if file doesn't exist
    """
    if not os.path.exists(settings.data_file):
        # Create empty address book if file doesn't exist
        return AddressBook()
    
    try:
        with open(settings.data_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return AddressBook.from_json(data)
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error loading data file: {e}")
        return AddressBook()


def save_address_book(address_book: AddressBook, settings: Settings) -> bool:
    """
    Save address book to JSON file.
    
    Args:
        address_book: The address book to save
        settings: Application settings containing the data file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(settings.data_file)), exist_ok=True)
        
        with open(settings.data_file, 'w', encoding='utf-8') as file:
            json.dump(address_book.to_json(), file, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving data file: {e}")
        return False


def backup_address_book(address_book: AddressBook, settings: Settings) -> bool:
    """
    Create a backup of the address book.
    
    Args:
        address_book: The address book to backup
        settings: Application settings containing the data file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create backup filename with timestamp
        base_name = os.path.splitext(settings.data_file)[0]
        backup_file = f"{base_name}_backup.json"
        
        with open(backup_file, 'w', encoding='utf-8') as file:
            json.dump(address_book.to_json(), file, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False
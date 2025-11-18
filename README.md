# Address Book CLI Application

A command-line application for managing contacts with an interactive interface. This application allows you to add, view, edit, and delete contacts, with all data stored in a JSON file.

## Features

- Interactive CLI with auto-completion
- Contact management (add, edit, delete, find)
- Tag-based search in notes
- Birthday reminders
- Data persistence in JSON format
- Rich, colorful output with tables and panels
- Graceful error handling

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```
python main.py
```

## Commands

### Greeting
- `hello` or `hi` - Greets the user with a random message

### Viewing Contacts
- `all` - Displays all saved contacts in a table format

### Adding Contacts
- `add <name> [options]` - Adds a new contact

Options:
- `-address <address>` - Set the address
- `-phone <phone>` - Add a phone number (can be used multiple times)
- `-email <email>` - Add an email address (can be used multiple times)
- `-birthday <DD.MM.YYYY>` - Set the birthday
- `-note <note>` - Add a note with optional tags (@tag)

Examples:
```
add John_Doe -address '125 Main St, City' -phone 1234567890 -phone 1234567899 -email john1@example.com -birthday 30.12.1983
add "Jane Smith" -phone 9876543210 -note "She is my @schoolmate"
add 'Bill James' -email bjames1@thecompany.com -birthday 08.11.1992 -email bjames2@thecompany.com
```

### Deleting Contacts
- `delete <name>` - Deletes a contact

Example:
```
delete John_Doe
```

### Editing Contacts
- `edit <name> [options]` - Edits a contact

Options:
- `-set-address <address>` - Set the address
- `-set-birthday <DD.MM.YYYY>` - Set the birthday
- `-set-note <note>` - Set the note
- `-add-phone <phone>` - Add a phone number (can be used multiple times)
- `-delete-phone <phone>` - Delete a phone number (can be used multiple times)
- `-add-email <email>` - Add an email address (can be used multiple times)
- `-delete-email <email>` - Delete an email address (can be used multiple times)

Examples:
```
edit John_Doe -delete-phone 1234567890 -add-phone 1234567899
edit 'Jane Smith' -set-address '125 Main St, City' -set-birthday 30.12.1983 -delete-email jane@home.com -delete-phone 0123456789
edit "Lucy Atkins" -set-note "She is an @awesome person!"
```

### Finding Contacts
- `find <name>` - Finds a specific contact by name

Example:
```
find John_Doe
```

### Tag-based Search
- `find-tag <tag>` - Finds contacts with a specific tag in their notes

The tag can be specified with or without the @ symbol.

Examples:
```
find-tag schoolmate
find-tag @schoolmate
```

### General Search
- `find-any <text>` - Finds contacts containing any text in any field

Searches across name, address, note, phones, and emails.

Examples:
```
find-any john
find-any 123456
find-any @good
```

### Birthday Reminders
- `birthdays [days]` - Shows upcoming birthdays

Shows contacts with birthdays in the next N days (default: 7).

Examples:
```
birthdays
birthdays 14
```

### Help
- `help [command]` - Shows help for commands

Without arguments, shows a list of all commands. With a command name, shows detailed help for that command.

Examples:
```
help
help add
help edit
```

### Exiting
- `exit` or `close` - Exits the application and saves data

## Data Format

Contacts are stored in a JSON file with the following structure:

```json
{
  "records": [
    {
      "name": "John_Doe",
      "phones": ["1234567890"],
      "emails": ["john1@example.com", "john2@example.com"],
      "address": "123 Main St, City",
      "birthday": "15.11.1990",
      "note": "John is a very @good person! He has a @cat"
    },
    {
      "name": "Jane_Smith",
      "phones": ["0987654321", "0987654322"],
      "emails": ["jane@example.com"],
      "address": "125 Main St, City"
    }
  ]
}
```

## Notes

- Contact names must be unique
- Names with spaces should be enclosed in quotes (single or double)
- Phone numbers must be 10-15 digits
- Email addresses are validated for proper format
- Birthdays should be in DD.MM.YYYY format
- Tags in notes start with the @ symbol
- Data is automatically saved when exiting the application
- The application creates a new data file if one doesn't exist

## Error Handling

The application provides clear error messages for:
- Invalid command syntax
- Missing required parameters
- Invalid data formats
- Contacts not found
- Duplicate names when adding

## Dependencies

- pydantic - Data validation and settings management
- rich - Rich text and beautiful formatting in the terminal
- prompt_toolkit - Library for building powerful interactive command lines
- email-validator - Email validation for pydantic
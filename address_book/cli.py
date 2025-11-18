"""
CLI interface for the address book application.
Uses prompt_toolkit for input handling and rich for output formatting.
"""

import shlex
import signal
import sys
from typing import Dict, List, Tuple, Any

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .commands import (
    handle_hello, handle_all, handle_add, handle_delete, handle_edit,
    handle_find, handle_find_tag, handle_find_any, handle_birthdays,
    handle_help, handle_exit
)
from .file_operations import load_address_book
from .models import Record
from .settings import Settings
from .terminal_detection import TerminalDetector


def highlight_tags(text: str) -> str:
    """
    Highlight tags in text with a separate color.
    
    Args:
        text: The text containing tags
        
    Returns:
        Text with tags highlighted using Rich markup
    """
    if not text:
        return text
    
    import re
    # Pattern to match @tag (alphanumeric and underscore characters after @)
    tag_pattern = r'(@\w+)'
    
    # Replace each tag with highlighted version using Rich markup
    highlighted_text = re.sub(tag_pattern, r'[bold cyan]\1[/bold cyan]', text)
    
    return highlighted_text


class AddressBookCLI:
    """
    CLI interface for the address book application.
    """
    
    def __init__(self):
        self.console = Console(force_terminal=True)
        self.settings = Settings()
        self.address_book = load_address_book(self.settings)
        self.history = InMemoryHistory()
        self.running = True
        
        # Setup command completer
        self.commands = [
            "hello", "hi", "all", "add", "delete", "edit", "find",
            "find-tag", "find-any", "birthdays", "help", "exit", "close"
        ]
        self.completer = WordCompleter(self.commands, ignore_case=True)
        
        # Setup key bindings
        self.key_bindings = KeyBindings()
        
        # Register signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C for graceful shutdown."""
        self.console.print("\n[yellow]Interrupt received. Saving data and exiting...[/yellow]")
        message = handle_exit(self.address_book, self.settings)
        self.console.print(f"[green]{message}[/green]")
        sys.exit(0)
    
    def _parse_command(self, input_str: str) -> Tuple[str, List[str], Dict[str, Any]]:
        """
        Parse command input into command, args, and kwargs.
        
        Args:
            input_str: The raw input string
            
        Returns:
            Tuple of (command, args, kwargs)
        """
        # Handle empty input
        if not input_str.strip():
            return "", [], {}
        
        # Split the input using shlex to handle quoted strings
        parts = shlex.split(input_str)
        
        if not parts:
            return "", [], {}
        
        command = parts[0].lower()
        args = []
        kwargs = {}
        
        i = 1
        while i < len(parts):
            part = parts[i]
            
            # Handle flags with values
            if part.startswith('-'):
                key = part[1:]  # Remove the leading dash
                
                # Check if there's a value for this flag
                if i + 1 < len(parts) and not parts[i + 1].startswith('-'):
                    value = parts[i + 1]
                    
                    # Convert to appropriate type if possible, but keep phone numbers as strings
                    if value.isdigit() and not key.startswith('phone') and not key.startswith('email'):
                        value = int(value)
                    
                    # Handle multiple values for the same key
                    if key in kwargs:
                        if isinstance(kwargs[key], list):
                            kwargs[key].append(value)
                        else:
                            kwargs[key] = [kwargs[key], value]
                    else:
                        kwargs[key] = value
                    
                    i += 2
                else:
                    # Flag without value, treat as boolean True
                    kwargs[key] = True
                    i += 1
            else:
                # Regular argument
                args.append(part)
                i += 1
        
        return command, args, kwargs
    
    def _format_record(self, record: Record) -> Table:
        """
        Format a record as a rich table.
        
        Args:
            record: The record to format
            
        Returns:
            Rich table with record data
        """
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Field", style="bold magenta", width=12)
        table.add_column("Value", style="white", width=40)
        
        table.add_row("[bold cyan]Name[/bold cyan]", f"[bold cyan]{record.name}[/bold cyan]")
        
        if record.address:
            table.add_row("[yellow]Address[/yellow]", f"[yellow]{record.address}[/yellow]")
        else:
            table.add_row("[yellow]Address[/yellow]", "[dim]N/A[/dim]")
        
        if record.birthday:
            table.add_row("[red]Birthday[/red]", f"[red]{record.birthday.strftime('%d.%m.%Y')}[/red]")
        else:
            table.add_row("[red]Birthday[/red]", "[dim]N/A[/dim]")
        
        if record.phones:
            table.add_row("[green]Phones[/green]", "\n".join([f"[green]{phone}[/green]" for phone in record.phones]))
        else:
            table.add_row("[green]Phones[/green]", "[dim]N/A[/dim]")
        
        if record.emails:
            table.add_row("[blue]Emails[/blue]", "\n".join([f"[blue]{email}[/blue]" for email in record.emails]))
        else:
            table.add_row("[blue]Emails[/blue]", "[dim]N/A[/dim]")
        
        if record.note:
            highlighted_note = highlight_tags(record.note)
            table.add_row("[magenta]Note[/magenta]", f"[magenta]{highlighted_note}[/magenta]")
        else:
            table.add_row("[magenta]Note[/magenta]", "[dim]N/A[/dim]")
        
        return table
    
    def _format_records_list(self, records: List[Record]) -> Table:
        """
        Format a list of records as a rich table.
        
        Args:
            records: The records to format
            
        Returns:
            Rich table with records data
        """
        table = Table(title="Contacts", box=None, show_header=True, header_style="bold magenta")
        table.add_column("Name", style="bold cyan", width=20)
        table.add_column("Phones", style="green", width=15)
        table.add_column("Emails", style="blue", width=20)
        table.add_column("Address", style="yellow", width=25)
        table.add_column("Birthday", style="red", width=12)
        
        for record in records:
            phones = ", ".join(record.phones) if record.phones else "[dim]N/A[/dim]"
            emails = ", ".join(record.emails) if record.emails else "[dim]N/A[/dim]"
            address = record.address or "[dim]N/A[/dim]"
            birthday = record.birthday.strftime("%d.%m.%Y") if record.birthday else "[dim]N/A[/dim]"
            
            # Add row with styled content
            table.add_row(
                f"[bold cyan]{record.name}[/bold cyan]",
                phones,
                emails,
                address,
                birthday
            )
        
        return table
    
    def _format_birthdays_list(self, birthdays: List[Tuple[Record, int]]) -> Table:
        """
        Format a list of upcoming birthdays as a rich table.
        
        Args:
            birthdays: List of (record, days_until) tuples
            
        Returns:
            Rich table with birthdays data
        """
        table = Table(title="Upcoming Birthdays", box=None, show_header=True, header_style="bold magenta")
        table.add_column("Name", style="bold cyan", width=20)
        table.add_column("Birthday", style="green", width=12)
        table.add_column("Days Until", style="yellow", width=12)
        
        for record, days_until in birthdays:
            birthday_str = record.birthday.strftime("%d.%m.%Y")
            days_str = f"{days_until} day{'s' if days_until != 1 else ''}"
            
            # Add special styling for birthdays that are very soon
            days_style = "bold red" if days_until <= 3 else "yellow"
            
            table.add_row(
                f"[bold cyan]{record.name}[/bold cyan]",
                f"[green]{birthday_str}[/green]",
                f"[{days_style}]{days_str}[/{days_style}]"
            )
        
        return table
    
    def _execute_command(self, command: str, args: List[str], kwargs: Dict[str, Any]) -> bool:
        """
        Execute a command with the given arguments.
        
        Args:
            command: The command to execute
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            True if the application should continue running, False if it should exit
        """
        try:
            if command in ["hello", "hi"]:
                message = handle_hello(self.settings)
                self.console.print(Panel(message, title="Greeting", border_style="green"))
            
            elif command == "all":
                records = handle_all(self.address_book)
                if records:
                    table = self._format_records_list(records)
                    self.console.print(table)
                else:
                    self.console.print("[yellow]No contacts found.[/yellow]")
            
            elif command == "add":
                if not args:
                    self.console.print("[red]Error: Name is required for add command.[/red]")
                    self.console.print("[cyan]Usage: add <name> [options][/cyan]")
                    return True
                
                name = args[0]
                success, message = handle_add(self.address_book, name, **kwargs)
                
                if success:
                    self.console.print(f"[green]✓ {message}[/green]")
                else:
                    self.console.print(f"[red]✗ {message}[/red]")
            
            elif command == "delete":
                if not args:
                    self.console.print("[red]Error: Name is required for delete command.[/red]")
                    self.console.print("[cyan]Usage: delete <name>[/cyan]")
                    return True
                
                name = args[0]
                success, message = handle_delete(self.address_book, name)
                
                if success:
                    self.console.print(f"[green]✓ {message}[/green]")
                else:
                    self.console.print(f"[red]✗ {message}[/red]")
            
            elif command == "edit":
                if not args:
                    self.console.print("[red]Error: Name is required for edit command.[/red]")
                    self.console.print("[cyan]Usage: edit <name> [options][/cyan]")
                    return True
                
                name = args[0]
                success, message = handle_edit(self.address_book, name, **kwargs)
                
                if success:
                    self.console.print(f"[green]✓ {message}[/green]")
                else:
                    self.console.print(f"[red]✗ {message}[/red]")
            
            elif command == "find":
                if not args:
                    self.console.print("[red]Error: Name is required for find command.[/red]")
                    self.console.print("[cyan]Usage: find <name>[/cyan]")
                    return True
                
                name = args[0]
                record = handle_find(self.address_book, name)
                
                if record:
                    table = self._format_record(record)
                    self.console.print(Panel(table, title=f"Contact: {name}", border_style="blue"))
                else:
                    self.console.print(f"[red]Contact '{name}' not found.[/red]")
            
            elif command == "find-tag":
                if not args:
                    self.console.print("[red]Error: Tag is required for find-tag command.[/red]")
                    self.console.print("[cyan]Usage: find-tag <tag>[/cyan]")
                    return True
                
                tag = args[0]
                records = handle_find_tag(self.address_book, tag)
                
                if records:
                    table = self._format_records_list(records)
                    self.console.print(table)
                else:
                    self.console.print(f"[yellow]No contacts found with tag '{tag}'.[/yellow]")
            
            elif command == "find-any":
                if not args:
                    self.console.print("[red]Error: Text is required for find-any command.[/red]")
                    self.console.print("[cyan]Usage: find-any <text>[/cyan]")
                    return True
                
                text = args[0]
                records = handle_find_any(self.address_book, text)
                
                if records:
                    table = self._format_records_list(records)
                    self.console.print(table)
                else:
                    self.console.print(f"[yellow]No contacts found containing '{text}'.[/yellow]")
            
            elif command == "birthdays":
                days = 7  # Default value
                if args and args[0].isdigit():
                    days = int(args[0])
                
                birthdays = handle_birthdays(self.address_book, days)
                
                if birthdays:
                    table = self._format_birthdays_list(birthdays)
                    self.console.print(table)
                else:
                    self.console.print(f"[yellow]No birthdays in the next {days} days.[/yellow]")
            
            elif command == "help":
                command_name = args[0] if args else None
                help_text = handle_help(command_name)
                self.console.print(Panel(help_text, title="Help", border_style="blue"))
            
            elif command in ["exit", "close"]:
                message = handle_exit(self.address_book, self.settings)
                self.console.print(Panel(message, title="Farewell", border_style="green"))
                return False
            
            else:
                self.console.print(f"[red]Unknown command: {command}[/red]")
                self.console.print("[cyan]Type 'help' to see available commands.[/cyan]")
        
        except Exception as e:
            self.console.print(f"[red]Error executing command: {str(e)}[/red]")
        
        return True
    
    def _is_ide_terminal(self):
        """Check if running in an IDE terminal."""
        return TerminalDetector.is_ide_terminal()
    
    def _fallback_input(self):
        """Fallback input method for IDE terminals."""
        try:
            # Use basic input without prompt_toolkit features
            user_input = input("> ")
            return user_input
        except (EOFError, KeyboardInterrupt):
            # Return exit command instead of None to avoid infinite loops
            return "exit"
    
    def run(self):
        """Run the CLI application."""
        # Check if we're in an IDE terminal
        if self._is_ide_terminal():
            self.console.print(Panel.fit(
                "[bold red]IDE Terminal Detected[/bold red]\n\n"
                "[yellow]This application requires a native Windows console to run properly.\n"
                "Please run this application in a Windows PowerShell or Command Prompt terminal.[/yellow]\n\n"
                "[cyan]Instructions:[/cyan]\n"
                "1. Open Windows PowerShell or Command Prompt\n"
                "2. Navigate to the application directory\n"
                "3. Run: [green]python main.py[/green]\n\n"
                "[red]Running in this IDE terminal may result in errors or limited functionality.[/red]",
                title="Terminal Compatibility Warning",
                border_style="red"
            ))
            
            # Ask user if they want to continue with limited functionality
            try:
                continue_choice = input("Continue with limited functionality? (y/n): ").lower()
                if continue_choice not in ['y', 'yes']:
                    self.console.print("[yellow]Exiting application. Please run in a native terminal.[/yellow]")
                    return
                else:
                    self.console.print("[yellow]Continuing with limited functionality...[/yellow]")
            except (EOFError, KeyboardInterrupt):
                self.console.print("[yellow]Exiting application. Please run in a native terminal.[/yellow]")
                return
        
        self.console.print(Panel.fit(
            "[bold blue]Address Book CLI[/bold blue]\n"
            "[green]Type 'help' to see available commands[/green]",
            border_style="blue"
        ))
        
        while self.running:
            try:
                # Get user input
                if self._is_ide_terminal():
                    # Use fallback input for IDE terminals
                    user_input = self._fallback_input()
                    if user_input == "exit":
                        # Handle graceful exit from fallback input
                        self.running = False
                        continue
                else:
                    # Try to use prompt_toolkit for native terminals
                    # but fall back if it fails
                    try:
                        user_input = prompt(
                            "> ",
                            completer=self.completer,
                            history=self.history,
                            key_bindings=self.key_bindings
                        )
                    except Exception as e:
                        # If prompt_toolkit fails, check if it's the Windows console error
                        if "No Windows console found" in str(e):
                            # Fall back to basic input instead of showing an error
                            self.console.print("[yellow]Warning: Advanced input features not available. Using basic input mode.[/yellow]")
                            user_input = self._fallback_input()
                            if user_input is None:
                                self.console.print("\n[yellow]Use 'exit' or 'close' to quit.[/yellow]")
                                continue
                        else:
                            # For other errors, re-raise
                            raise
                
                # Parse and execute command
                command, args, kwargs = self._parse_command(user_input)
                
                if command:  # Skip empty commands
                    self.running = self._execute_command(command, args, kwargs)
            
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use 'exit' or 'close' to quit.[/yellow]")
            except EOFError:
                self.console.print("\n[yellow]Use 'exit' or 'close' to quit.[/yellow]")
            except Exception as e:
                # Check if it's the specific Windows console error
                if "No Windows console found" in str(e):
                    self.console.print("[yellow]Warning: Advanced input features not available. Using basic input mode.[/yellow]")
                    continue
                else:
                    self.console.print(f"[red]Unexpected error: {str(e)}[/red]")


def main():
    """Main entry point for the CLI application."""
    cli = AddressBookCLI()
    cli.run()


if __name__ == "__main__":
    main()
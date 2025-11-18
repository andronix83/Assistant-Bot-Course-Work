"""
Application settings using pydantic-settings.
"""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings.
    """
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }
    
    data_file: str = Field(default="data/address_book.json", description="Path to the data file")
    greetings: List[str] = Field(
        default=[
            "Hello! How can I help you today?",
            "Hi there! What can I do for you?",
            "Greetings! Ready to manage your contacts?",
            "Welcome! How may I assist you?",
            "Good day! Let's work with your address book."
        ],
        description="List of random greetings"
    )
    farewells: List[str] = Field(
        default=[
            "Goodbye! Have a great day!",
            "See you later! Take care!",
            "Farewell! Until next time!",
            "Bye! Come back soon!",
            "So long! Have a wonderful day!"
        ],
        description="List of random farewells"
    )
class PhoneFormatError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class EmailFormatError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
from modules.bot_assistant.models.exceptions import (
    InvalidPhoneError,
    InvalidBirthdayFormatError,
    InvalidArgsError,
)


def input_error(func):
    """
    Decorator for input errors.
    :param func:
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except InvalidArgsError:
            return "Invalid number of arguments."
        except InvalidPhoneError:
            return "Invalid phone number. Phone number must contain 10 digits, with or without '+' sign"
        except InvalidBirthdayFormatError:
            return "Invalid birthday format. Please use DD.MM.YYYY format."

    return wrapper

from enum import unique
from core.settings import BaseEnum


@unique
class ErrorEnum(BaseEnum):
    LANGUAGE_NOT_EXIST = "Language {0} does not exist."
    INVALID_CODE = "Invalid code."
    CHAT_BLOCKED_USER_NOT_ALWAYS = "You have been blocked due to a violation of the chat rules. Unblock date: {0}"
    NOT_ENOUGH_MONEY = "Not enough money."
    CHAT_MESSAGE_TOO_LONG = "Chat message longer than {0} chars."
    HAVE_NOT_ACTIVE_USERS_IN_CHAT = "Drop can’t be made. Not enough active players in chat. Try again later"
    LONG = (
        "You have been blocked. You have been blocked. You have been blocked. You have been blocked. You have been blo"
    )


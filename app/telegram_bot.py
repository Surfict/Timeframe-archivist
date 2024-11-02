import os
import telegram
from telegram.error import InvalidToken, BadRequest, Forbidden
import typing as ty

async def send_message_to_telegram_conversation(message: str) -> None:
    """
    Send a message to a telegram conversation using a telegram bot (specified in the env file)
    """
    
    # Chat_id can be :  ID of the user (then the conversation will be betwen the user and the bot) - ID of a telegram chat (then the message will be send in a group)
    chat_id = os.getenv("TELEGRAM_CHAT_ID") 
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    try: 
        await telegram.Bot(bot_token).sendMessage(chat_id=chat_id, text=message)
    except InvalidToken:
        raise ValueError("The bot token provided is invalid.")
    except Forbidden as e:
        raise ValueError(f"{e}")
    except BadRequest as e:
        if "Chat not found" in str(e):
            raise ValueError("The chat ID is incorrect or does not exist.")
        else:
            raise ValueError(f"Bad request: {e}")

def format_links_message(messages: ty.List[str]) -> str:
    """
    Return a list of video links into one formated string
    """
    return_string = ""
    for message in messages:
        return_string = return_string + message + " "
    
    return return_string[:-1]
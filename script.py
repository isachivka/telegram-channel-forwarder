import asyncio  # Importing asyncio for asynchronous operations
from telethon import TelegramClient  # Importing the TelegramClient from the Telethon library for interacting with Telegram API
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument  # Importing necessary Telegram types for handling media messages
import json  # Importing JSON module to handle reading and writing JSON files
import os  # Importing os module to interact with the operating system (e.g., file operations)
import random  # Importing random module to add random delays

def load_env(path: str = '.env') -> None:
    """
    Minimal .env loader to avoid extra dependencies.
    Supports KEY=VALUE lines, ignores empty lines and comments (# ...).
    """
    if not os.path.exists(path):
        return

    with open(path, 'r') as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith('#'):
                continue

            if '=' not in line:
                continue

            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def getenv_required(name: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == '':
        raise ValueError(f"Missing required environment variable: {name}")
    return value.strip()


def parse_int(value: str, name: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc


def parse_channel_id(value: str) -> str | int:
    stripped = value.strip()
    if stripped.lstrip('-').isdigit():
        return int(stripped)
    return stripped


load_env()

# Initial settings for Telegram API access
api_id = parse_int(getenv_required('APP_ID'), 'APP_ID')  # Your Telegram API ID
api_hash = getenv_required('API_HASH')  # Your Telegram API Hash
phone_number = getenv_required('PHONE_NUMBER')  # Your phone number with country code
session_name = getenv_required('SESSION_NAME')  # Session name for the Telegram client

# Channel IDs for the source and destination channels
source_channel_id = parse_channel_id(getenv_required('SOURCE_CHANNEL_ID'))  # Source channel ID
destination_channel_id = parse_channel_id(getenv_required('DESTINATION_CHANNEL_ID'))  # Destination channel ID

# File to store the ID of the last sent message
last_message_file = 'last_message.json'
MAX_CAPTION_LENGTH = 900


def trim_caption(text: str | None, max_length: int = MAX_CAPTION_LENGTH) -> str | None:
    if text is None:
        return None
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + '...'

async def handle_telegram_session(client):
    """
    Main function to handle fetching messages from the source channel and sending them to the destination channel.
    It keeps track of the last sent message to avoid duplicates.
    """
    # Retrieving the last sent message ID
    last_message = None
    if os.path.exists(last_message_file):
        with open(last_message_file, 'r') as f:
            try:
                last_message = json.load(f)
            except json.JSONDecodeError:
                last_message = None

    async def send_group(messages):
        if not messages:
            return

        media_items = []
        caption = None
        last_id = messages[-1].id

        for msg in messages:
            if caption is None and msg.text:
                caption = trim_caption(msg.text)
            if isinstance(msg.media, (MessageMediaPhoto, MessageMediaDocument)):
                media_items.append(msg.media)

        if media_items:
            await client.send_file(destination_channel_id, media_items, caption=caption)
        elif caption:
            await client.send_message(destination_channel_id, caption)

        with open(last_message_file, 'w') as f:
            json.dump({'id': last_id}, f)

        print(f"Message group up to {last_id} sent successfully")
        await asyncio.sleep(random.uniform(303, 310))

    # Fetching all messages from the source channel starting from the first message
    current_group_id = None
    current_group = []

    async for message in client.iter_messages(source_channel_id, reverse=True):
        if last_message and message.id <= last_message['id']:
            continue  # Skip messages that have already been sent

        if message.grouped_id:
            if current_group_id is None or message.grouped_id == current_group_id:
                current_group_id = message.grouped_id
                current_group.append(message)
                continue

            await send_group(current_group)
            current_group_id = message.grouped_id
            current_group = [message]
            continue

        if current_group:
            await send_group(current_group)
            current_group = []
            current_group_id = None

        # Sending text messages to the destination channel
        if message.text and not message.media:
            await client.send_message(destination_channel_id, trim_caption(message.text))
        # Sending media messages (photos or documents) to the destination channel
        if message.media and isinstance(message.media, (MessageMediaPhoto, MessageMediaDocument)):
            await client.send_file(destination_channel_id, message.media, caption=trim_caption(message.text))

        # Save the last sent message ID
        with open(last_message_file, 'w') as f:
            json.dump({'id': message.id}, f)

        print(f"Message {message.id} sent successfully")

        # Random delay between 3 to 10 seconds between each message to avoid being flagged by Telegram
        await asyncio.sleep(random.uniform(300, 310))

    if current_group:
        await send_group(current_group)

async def main():
    """
    Main function to initialize the Telegram client and manage user authorization.
    """
    try:
        # Creating the client and connecting to Telegram
        async with TelegramClient(session_name, api_id, api_hash) as client:
            # If the session file does not exist, request the login code
            if not await client.is_user_authorized():
                await client.send_code_request(phone_number)
                code = input('Enter the code you received: ')
                await client.sign_in(phone_number, code)

            # Execute the main session handling function
            await handle_telegram_session(client)
    except Exception as e:
        print(f"An error occurred: {e}")

# Running the main function
asyncio.run(main())

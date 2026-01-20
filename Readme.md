# Telegram Channel Forwarder

A Python script that forwards messages from one Telegram channel to another using the Telethon library. This script supports both text and media messages and keeps track of the last forwarded message to avoid duplicates.

## Features

- **Forward text and media messages**: Forward text and media messages from a source channel to a destination channel.
- **Keep albums together**: Multi-photo posts are forwarded as a single album with the original caption.
- **Safe caption length**: Captions are trimmed to 900 characters with `...` to avoid Telegram limits.
- **Track last sent message**: Keeps track of the last sent message to avoid duplicate forwarding.
- **Persistent Telegram session**: The session is saved locally, so you don’t need to re-enter the login code every time you run the script. This prevents getting temporarily blocked by Telegram for too many login requests.
- **Resume from the last sent message**: If the program stops for any reason (e.g., internet issues), it can resume from the last sent message after restarting.
- **Random delay between messages**: Random delay between messages to avoid being flagged by Telegram.

## Prerequisites

- Python 3.7 or higher
- Telethon library

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/telegram-channel-forwarder.git
   cd telegram-channel-forwarder
   ```

2. **Install Dependencies**

   Install the required Python libraries using pip:

   ```bash
   pip install telethon
   ```

## Getting Started

1. **Obtain API Credentials from Telegram**

   To use this script, you need to get your `api_id` and `api_hash` from the [Telegram API Development Tools](https://my.telegram.org/apps).

2. **Configure Environment Variables**

   Create a `.env` file in the project root with the following values:

   ```env
   APP_ID=123456
   API_HASH=your_api_hash
   PHONE_NUMBER=+1234567890
   SESSION_NAME=your_session_name
   SOURCE_CHANNEL_ID=source_channel_id_or_username
   DESTINATION_CHANNEL_ID=destination_channel_id_or_username
   ```

3. **Run the Script**

   Run the script with Python:

   ```bash
   python script.py
   ```

   The script will ask for a login code sent to your Telegram app if it is the first time you are running it. Enter the code to authenticate.

## How It Works

- The script connects to the Telegram client using the provided `.env` credentials.
- It fetches messages from the specified source channel and forwards them to the destination channel.
- A JSON file (`last_message.json`) is used to keep track of the last sent message, ensuring no message is sent twice.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/alimahdibahrami/telegram-channel-forwarder/blob/main/LICENSE) file for details.

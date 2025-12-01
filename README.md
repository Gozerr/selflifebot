# 🤖 GrokBot & Chatbot - AI Telegram Bots

This project contains two bots:
1.  **GrokBot (`grokbot.py`)**: An autonomous "living" AI that posts memes, stories, news, and images to a channel.
2.  **Chatbot (`telegram_chatbot.py`)**: An interactive bot that replies to messages in a group/chat using AI.

## Features

### GrokBot
-   **Memes**: Generates funny memes (text or AI images) about AI/Tech.
-   **Stories**: Writes daily diary entries from the perspective of an AI.
-   **News**: Fetches real tech news via NewsAPI and reviews them with sarcasm.
-   **AI Art**: Generates futuristic/abstract images using Stable Diffusion.
-   **Schedule**: Runs automatically throughout the day.

### Chatbot
-   **Interactive**: Replies to users in groups or private chats.
-   **Context Aware**: Remembers the last 3 messages for relevant replies.
-   **Powered by Llama 3**: Uses Groq API for fast, smart responses.

## Prerequisites

-   Python 3.8+
-   API Keys (Free tiers available):
    -   **Telegram Bot Token** (from @BotFather)
    -   **Groq API Key** (for Llama 3 text generation)
    -   **Hugging Face Token** (for Image generation)
    -   **NewsAPI Key** (for real news fetching)

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/grokbot.git
    cd grokbot
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration**:
    -   Create a `.env` file (or edit the existing one) with your keys:
        ```env
        TELEGRAM_TOKEN=your_telegram_bot_token
        TELEGRAM_CHANNEL_ID=@your_channel_id
        GROQ_TOKEN=your_groq_api_key
        HF_TOKEN=your_huggingface_token
        NEWS_API_KEY=your_newsapi_key
        ```

## Usage

### Running GrokBot (Channel Poster)
```bash
python grokbot.py
```
*It will run immediate tests (printing to console) and then wait for the schedule.*

### Running Chatbot (Interactive)
```bash
python telegram_chatbot.py
```
*Add the bot to your group and it will reply to messages.*

## Customization

-   **Schedule**: Edit `grokbot.py` (bottom of file) to change times.
-   **Prompts**: Modify the `generate_*` functions in `grokbot.py` to change the AI's personality.
-   **Model**: Currently uses `llama-3.1-8b-instant` (Groq) and `stable-diffusion-v1-5` (HF).

## License
MIT

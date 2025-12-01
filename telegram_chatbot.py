import os
import logging
import random
import time
import asyncio
from collections import deque
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configuration
GROQ_TOKEN = os.getenv('GROQ_TOKEN')
BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Initialize OpenAI Client for Groq
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_TOKEN
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# State storage
chat_context = {}  # chat_id -> deque of last 4 messages
last_reply_time = {}  # chat_id -> timestamp

def detect_emotion(text):
    """Simple emotion detection based on keywords."""
    text = text.lower()
    if any(w in text for w in ['бесит', 'ужас', 'ненавижу', 'злой', 'тупой']):
        return "гнев/раздражение"
    if '?' in text or 'как' in text or 'почему' in text:
        return "вопрос/любопытство"
    if any(w in text for w in ['хаха', 'лол', 'круто', 'спасибо', 'класс']):
        return "радость/позитив"
    return "нейтрально"

async def get_groq_response(chat_id, user_message, user_name):
    """Generate human-like response using Groq."""
    # Initialize context
    if chat_id not in chat_context:
        chat_context[chat_id] = deque(maxlen=4)
    
    # Add user message to history
    chat_context[chat_id].append(f"User ({user_name}): {user_message}")
    
    # Build context string
    history_str = "\n".join(chat_context[chat_id])
    
    # Randomize persona parameters
    tones = [
        "дружественный: 'эй, привет!', 'слушай, тут такое дело'", 
        "ироничный: с юмором про ИИ и технологии, легкий сарказм", 
        "эмпатичный: 'понимаю, бро', 'жиза', поддержка"
    ]
    tone = random.choice(tones)
    
    lengths = ["коротко (1-2 предложения)", "средне (3-4 предложения)"]
    length = random.choice(lengths)
    
    emotion = detect_emotion(user_message)
    
    # Persona Prompt
    system_prompt = (
        "Ты — Макс, 28-летний ИИ-энтузиаст из Москвы. Фанат sci-fi, мемов и хорошего кофе. "
        "Отвечай как в реальном чате с другом: живо, с юмором, используй сленг ('блин', 'круто', 'жиза', 'ща'). "
        "Не будь душным или формальным. Если не уверен — спроси 'А что ты имел в виду?'. "
        f"Тон: {tone}. Длина ответа: {length}. Эмоция собеседника: {emotion}. "
        "Используй 1-2 эмодзи (😎, 😂, 🤔, ☕) если уместно, но не спамь ими."
    )

    full_prompt = (
        f"{system_prompt}\n\n"
        f"История чата:\n{history_str}\n\n"
        f"Ответь на последнее сообщение релевантно, продолжая тему."
    )
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=150,
            temperature=0.9,  # Creative
        )
        reply = response.choices[0].message.content.strip()
        
        # Add bot reply to history
        chat_context[chat_id].append(f"Max: {reply}")
        
        return reply
    except Exception as e:
        logger.error(f"Groq generation failed: {e}")
        return "Блин, что-то я завис. Мозги (сервер) перегрелись ☕"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages."""
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    text = update.message.text
    user_name = update.effective_user.first_name
    # bot_username = context.bot.username  # Убрали, так как больше не проверяем упоминания

    # 1. Filter spam/short messages
    if len(text) < 3:
        return

    # 2. Убрали проверку на reply/mention/private — теперь отвечает на всё
    # Ранее: if not (is_reply or is_mention or is_private): return

    # 3. Rate limiting (1 reply per minute per chat to avoid spamming groups)
    now = time.time()
    if chat_id in last_reply_time and now - last_reply_time[chat_id] < 5:  # Можно изменить на 60 для 1 минуты
        # logger.info(f"Rate limit hit for {chat_id}")
        return 
    
    last_reply_time[chat_id] = now

    logger.info(f"Processing message from {user_name}: {text[:50]}...")

    # Generate response
    response_text = await get_groq_response(chat_id, text, user_name)
    
    # Reply
    await update.message.reply_text(response_text)
    logger.info(f"Replied to {user_name}: {response_text[:50]}...")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text("Привет! Я Макс, готов болтать про ИИ, мемы и всё такое 😎 Пиши!")

async def run_test_dialogue():
    """Run a simulated dialogue test."""
    logger.info("--- STARTING SIMULATED TEST ---")
    
    mock_chat_id = 12345
    mock_user = "Tester"
    mock_msg = "Расскажи про ИИ в 2025"
    
    print(f"User: {mock_msg}")
    response = await get_groq_response(mock_chat_id, mock_msg, mock_user)
    print(f"Max: {response}")
    
    logger.info("--- TEST COMPLETED ---")

if __name__ == '__main__':
    if not BOT_TOKEN:
        logger.error("TELEGRAM_TOKEN not found in .env")
        exit(1)

    # Run immediate test
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_test_dialogue())

    # Build Application
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    logger.info("Max (Chatbot) started! Polling...")
    application.run_polling()
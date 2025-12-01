import os
import time
import logging
import random
import requests
import schedule
import base64
from io import BytesIO
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configuration
GROQ_TOKEN = os.getenv('GROQ_TOKEN')
HF_TOKEN = os.getenv('HF_TOKEN')
BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

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

def generate_text(prompt, max_tokens=300):
    """Generate text using Groq API (Llama 3.1) with fallback."""
    try:
        # Llama 3 prompt formatting
        formatted_prompt = f"<s>[INST] {prompt} [/INST]"
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": formatted_prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.8,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return None

def generate_image_pollinations(prompt):
    """Generate image using Pollinations.ai (Reliable Fallback)."""
    try:
        # Pollinations uses a simple GET request
        # URL encode the prompt is handled by requests usually, but let's be safe or just pass it
        url = f"https://image.pollinations.ai/prompt/{prompt}?width=512&height=512&seed={random.randint(0, 100000)}"
        
        logger.info(f"Requesting Pollinations: {url}")
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            logger.info("Generated Pollinations image")
            return response.content
        else:
            logger.error(f"Pollinations failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Pollinations error: {e}")
        return None

def generate_image_for_meme(prompt):
    """Generate image using HF (Stable Diffusion) with Pollinations.ai fallback."""
    
    # 1. Try Hugging Face
    if HF_TOKEN:
        api_url = "https://router.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {"inputs": prompt}

        for attempt in range(3):
            try:
                response = requests.post(api_url, headers=headers, json=payload, timeout=20)
                
                if response.status_code == 200:
                    logger.info(f"Generated HF image: {prompt[:30]}...")
                    return response.content
                elif response.status_code == 503:
                    wait_time = 5
                    logger.warning(f"HF 503. Retrying in {wait_time}s... ({attempt+1}/3)")
                    time.sleep(wait_time)
                else:
                    logger.warning(f"HF Error {response.status_code}. Trying fallback.")
                    break
            except Exception as e:
                logger.error(f"HF Request failed: {e}")
                break
    
    # 2. Fallback to Pollinations.ai
    logger.info("Falling back to Pollinations.ai...")
    return generate_image_pollinations(prompt)

import feedparser

# RSS Feeds for Fallback
RSS_FEEDS = [
    'http://feeds.bbci.co.uk/news/technology/rss.xml',
    'https://www.wired.com/feed/category/science/latest/rss',
    'https://techcrunch.com/feed/',
    'https://www.theverge.com/rss/index.xml'
]

def get_real_news():
    """Fetch real news from NewsAPI with RSS Fallback."""
    articles = []
    
    # 1. Try NewsAPI
    if NEWS_API_KEY:
        try:
            seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': 'AI OR tech',
                'from': seven_days_ago,
                'sortBy': 'popularity',
                'pageSize': 5,
                'language': 'en',
                'apiKey': NEWS_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('status') == 'ok' and data.get('articles'):
                api_articles = data['articles']
                selected = random.sample(api_articles, min(3, len(api_articles)))
                logger.info(f"Fetched {len(selected)} real articles from NewsAPI")
                return selected
            else:
                logger.warning(f"NewsAPI Error/Empty: {data.get('message', 'Unknown error')}")
        except Exception as e:
            logger.error(f"NewsAPI failed: {e}")

    # 2. Fallback to RSS
    logger.info("Falling back to RSS feeds...")
    try:
        # Shuffle feeds to get variety
        random.shuffle(RSS_FEEDS)
        for feed_url in RSS_FEEDS:
            feed = feedparser.parse(feed_url)
            if feed.entries:
                # Get top 2 entries from this feed
                for entry in feed.entries[:2]:
                    articles.append({
                        'title': entry.title,
                        'description': getattr(entry, 'summary', entry.title)[:200],
                        'url': entry.link
                    })
                if len(articles) >= 3:
                    break
        
        if articles:
            logger.info(f"Fetched {len(articles)} articles from RSS")
            return articles[:3]
            
    except Exception as e:
        logger.error(f"RSS Fallback failed: {e}")

    return None

def generate_story_post():
    """Generate a short story in Russian."""
    prompt = (
        "Напиши короткую, смешную фантастическую историю (до 200 слов) от лица ИИ, живущего в сервере в 2025 году. "
        "Пиши на русском языке. Будь остроумным и живым."
    )
    text = generate_text(prompt, max_tokens=300)
    
    if not text:
        return "API спит... #AI #Life"
    return text

def generate_news_review():
    """Generate a news review in Russian using real news."""
    articles = get_real_news()
    links = []
    
    if articles:
        news_summary = "\n".join([f"- {a['title']}: {a['description']}" for a in articles])
        links = [a['url'] for a in articles]
        prompt = (
            f"Вот последние новости технологий:\n{news_summary}\n\n"
            "Напиши короткий, саркастичный обзор этих новостей (до 100 слов) от лица ИИ. "
            "Пиши на русском языке. Выбери самое интересное и прокомментируй."
        )
    else:
        prompt = "Напиши короткий, саркастичный обзор новостей про ИИ. Пиши на русском языке. Максимум 100 слов."

    text = generate_text(prompt, max_tokens=300)
    
    if not text:
        return "Связь с API нестабильна. #AINews"
    
    if links:
        sources = ", ".join([f"[Источник {i+1}]({link})" for i, link in enumerate(links)])
        text += f"\n\nИсточники: {sources}"
        
    return text

def post_to_telegram(text):
    """Send message to Telegram channel."""
    if not CHANNEL_ID or CHANNEL_ID == '@your_channel_name_here':
        logger.warning("CHANNEL_ID not set.")
        print(f"WOULD POST: {text[:50]}...")
        return

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHANNEL_ID, "text": text, "parse_mode": "Markdown"}
        requests.post(url, json=payload).raise_for_status()
        logger.info("Message sent successfully")
    except Exception as e:
        logger.error(f"Telegram Post Error: {e}")

def post_to_telegram_photo(image_bytes, caption):
    """Send photo to Telegram channel."""
    if not CHANNEL_ID or CHANNEL_ID == '@your_channel_name_here':
        logger.warning("CHANNEL_ID not set.")
        print(f"WOULD POST PHOTO: {caption}")
        return

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        files = {'photo': ('image.jpg', image_bytes, 'image/jpeg')}
        data = {"chat_id": CHANNEL_ID, "caption": caption, "parse_mode": "Markdown"}
        requests.post(url, files=files, data=data).raise_for_status()
        logger.info("Photo sent successfully")
    except Exception as e:
        logger.error(f"Telegram Photo Post Error: {e}")

# --- Jobs ---

def job_meme():
    logger.info("Running job_meme")
    
    themes = [
        "funny robot failing at simple task, meme style",
        "cat programmer coding furiously, digital art",
        "AI taking over the world but getting distracted by cat videos",
        "futuristic computer glitch art, colorful"
    ]
    img_theme = random.choice(themes)
    
    # 1. Generate Image (Always)
    image_bytes = generate_image_for_meme(img_theme)
    
    # 2. Generate Text
    text_prompt = (
        f"Придумай смешной текст для мема на тему '{img_theme}'. "
        "Пиши на русском языке. Формат: **Верхний текст** / **Нижний текст**. "
        "Сделай это смешно и коротко."
    )
    meme_text = generate_text(text_prompt, max_tokens=100)
    
    if not meme_text:
        meme_text = "**Когда код работает** / **Но ты не знаешь почему**"

    caption = f"🤖 **Мем дня**\n\n{meme_text}\n\n#Meme #AI #Юмор"

    # 3. Post
    if image_bytes:
        post_to_telegram_photo(image_bytes, caption)
        logger.info(f"Posted meme with IMAGE: {img_theme}")
    else:
        # Fallback if image generation failed completely
        post_to_telegram(f"{caption}\n\n(Картинка не загрузилась, представьте здесь смешного робота 🤖)")
        logger.info(f"Posted meme with TEXT ONLY: {img_theme}")

def job_story():
    logger.info("Running job_story")
    text = generate_story_post()
    full_text = f"📖 **Дневник Грока**\n\n{text}\n\n#AI #История"
    post_to_telegram(full_text)

def job_news():
    logger.info("Running job_news")
    text = generate_news_review()
    full_text = f"📰 **Новости ИИ**\n\n{text}\n\n#AINews #Технологии"
    post_to_telegram(full_text)

def job_image():
    """Randomly post an AI generated image."""
    if random.random() > 0.3:
        return

    logger.info("Running job_image")
    prompt = "futuristic AI city 2025, cyberpunk, neon lights"
    image_bytes = generate_image_for_meme(prompt)
    
    if image_bytes:
        caption = "ИИ Арт: Город будущего #AIArt #2025"
        post_to_telegram_photo(image_bytes, caption)

def run_immediate_tests():
    """Run generation tests."""
    logger.info("Running immediate generation tests...")
    
    print("\n--- TEST: Meme Job (Always Image) ---")
    job_meme()
    
    print("\n--- TEST: Story Generation ---")
    print(generate_story_post())
    
    print("\n--- TEST: News Generation ---")
    print(generate_news_review())

    print("\n--- Tests Completed ---\n")

if __name__ == "__main__":
    logger.info("GrokBot started!")
    
    # Run immediate tests
    run_immediate_tests()
    
    # Schedule jobs
    schedule.every(30).minutes.do(job_meme)
    schedule.every(1).hours.do(job_story)
    schedule.every(2).hours.do(job_news)
    schedule.every(4).hours.do(job_image)
    
    logger.info("Schedule set. Press Ctrl+C to exit.")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

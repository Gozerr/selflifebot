# Configuration for GrokBot

# Telegram Bot Token (from BotFather)
TELEGRAM_TOKEN = '8502002415:AAGjGU-Wm6eY3-aEb5sD60OgyyoP1LirAhQ'

# Hugging Face API Token
HF_TOKEN = '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'

# Imgflip API Credentials
IMGFLIP_USERNAME = 'Tuman199654'
IMGFLIP_PASSWORD = 'vtldtltd_1996'

# Telegram Channel ID (You need to add the bot to the channel as admin and get the ID)
# Format: '@your_channel_name' or integer ID like -1001234567890
TELEGRAM_CHANNEL_ID = '@ai_lifechannel'  # REPLACE THIS WITH YOUR CHANNEL ID

# Schedule Times (24h format)
TIME_MEME = "09:00"
TIME_STORY = "12:00"
TIME_NEWS = "18:00"

# RSS Feeds for News
RSS_FEEDS = [
    'http://feeds.bbci.co.uk/news/technology/rss.xml',
    'https://www.sciencedaily.com/rss/top/science.xml',
    'https://rss.nytimes.com/services/xml/rss/nyt/Arts.xml',
    'https://techcrunch.com/feed/',
    'https://www.wired.com/feed/category/science/latest/rss'
]

# Meme Templates (ID, Name)
MEME_TEMPLATES = [
    ('181913649', 'Drake Hotline Bling'),
    ('112126428', 'Distracted Boyfriend'),
    ('87743020', 'Two Buttons'),
    ('93895088', 'Expanding Brain'),
    ('129242436', 'Change My Mind'),
    ('438680', 'Batman Slapping Robin'),
    ('61544', 'Success Kid'),
    ('61579', 'One Does Not Simply'),
    ('102156234', 'Mocking Spongebob'),
    ('89370399', 'Roll Safe Think About It')
]

# Hugging Face Model
HF_MODEL_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"

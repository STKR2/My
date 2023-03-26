from os import getenv
from dotenv import load_dotenv

admins = {}
load_dotenv()

# client vars
API_ID = int(getenv("API_ID", "7452578")) #لا تغير هاذة القيمة
API_HASH = getenv("API_HASH", "061d67ee8eed9368c5cadabb4aa21efc")#لا تغير هاذة القيمة
BOT_TOKEN = getenv("BOT_TOKEN", "")
SESSION_NAME = getenv("SESSION_NAME", "")

# mandatory vars
OWNER_USERNAME = getenv("OWNER_USERNAME", "rr8r9") # @ هنا ضع يوزر حسابك بدون 
ALIVE_NAME = getenv("ALIVE_NAME", "sonng") # هنا ضع اسم حسابك
BOT_USERNAME = getenv("BOT_USERNAME", "") # @ هنا ضع يوزر البوت بدون 
UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/X02lx/RrRRR") 
UPSTREAM_BRANCH = getenv("UPSTREM_BRANCH", "main") #لا تغير هاذة القيمة
DURATION_LIMIT = int(getenv("DURATION_LIMIT", "60")) #لا تغير هاذة القيمة
GROUP_SUPPORT = getenv("GROUP_SUPPORT", "rr8r9") # @ هنا ضغ يوزر كروبك بدون 
UPDATES_CHANNEL = getenv("UPDATES_CHANNEL", "xl444") # @ هنا ضغ يوزر قناتك بدون

# database, decorators, handlers mandatory vars
MONGODB_URL = getenv("MONGODB_URL", "mongodb+srv://veez:mega@cluster0.heqnd.mongodb.net/veez?retryWrites=true&w=majority")
COMMAND_PREFIXES = list(getenv("COMMAND_PREFIXES", "/ ! . $").split())
OWNER_ID = list(map(int, getenv("OWNER_ID", "1854384004").split()))
                                             #هنا ضع ايدي المطور فوق و الاعلئ
SUDO_USERS = list(map(int, getenv("SUDO_USERS", "1854384004").split()))

# image resources vars
IMG_1 = getenv("IMG_1", "https://telegra.ph/file/f5b364ed9e94449dee565.jpg")
IMG_2 = getenv("IMG_2", "https://telegra.ph/file/f5b364ed9e94449dee565.jpg")
IMG_3 = getenv("IMG_3", "https://telegra.ph/file/f5b364ed9e94449dee565.jpg")
IMG_4 = getenv("IMG_4", "https://telegra.ph/file/f5b364ed9e94449dee565.jpg")
IMG_5 = getenv("IMG_5", "https://telegra.ph/file/f5b364ed9e94449dee565.jpg")
ALIVE_IMG = getenv("ALIVE_IMG", "https://telegra.ph/file/f5b364ed9e94449dee565.jpg")

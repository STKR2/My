# Copyright (C) 2021 By VeezMusicProject

import logging
import time


logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("PyTgCalls").setLevel(logging.WARNING)
logging.getLogger("youtube_dl").setLevel(logging.WARNING)

LOG = logging.getLogger(__name__)
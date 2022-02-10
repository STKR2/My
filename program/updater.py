# Copyright (C) 2022 Veez Music Project
# Updater Plugin by YukkiMusicBot

import os
import sys
import math
import random
import shutil
import asyncio
import dotenv
import heroku3
import requests
import urllib3

from datetime import datetime
from time import strftime, time
from pyrogram import Client, filters
from pyrogram.types import Message
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

from config import (
    HEROKU_API_KEY,
    HEROKU_APP_NAME,
    UPSTREAM_BRANCH,
    UPSTREAM_REPO,
    BOT_USERNAME as bname,
)

from driver.core import bot
from driver.filters import command
from driver.decorators import bot_creator
from driver.utils import is_heroku, user_input
from driver.paste import isPreviewUp, paste_queue
from driver.database.dbqueue import get_active_chats, remove_active_chat


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

XCB = [
    "/",
    "@",
    ".",
    "com",
    ":",
    "git",
    "heroku",
    "push",
    str(HEROKU_API_KEY),
    "https",
    str(HEROKU_APP_NAME),
    "HEAD",
    "main",
]


@Client.on_message(command(["update", f"update@{bname}"]) & ~filters.edited)
@bot_creator
async def update_bot(_, message: Message):
    if await is_heroku():
        if HEROKU_API_KEY == "" and HEROKU_APP_NAME == "":
            return await message.reply_text(
                "🚦 **<u>HEROKU APP DETECTED !</u>** 🚦\n\n» To receive update of your bot, please set up the `HEROKU_API_KEY` and `HEROKU_APP_NAME` vars correctly !"
            )
        elif HEROKU_API_KEY == "" or HEROKU_APP_NAME == "":
            return await message.reply_text(
                "🚦 **<u>HEROKU APP DETECTED !</u>** 🚦\n\n» To receive update, make sure both of `HEROKU_API_KEY` and `HEROKU_APP_NAME` vars has been set up correctly !"
            )
    response = await message.reply_text("❖ Checking for updates...")
    try:
        repo = Repo()
    except GitCommandError:
        return await response.edit("Git command error !")
    except InvalidGitRepositoryError:
        return await response.edit("Invalid git repository !")
    to_exc = f"git fetch origin {UPSTREAM_BRANCH} &> /dev/null"
    os.system(to_exc)
    await asyncio.sleep(7)
    verification = ""
    REPO_ = repo.remotes.origin.url.split(".git")[0]
    for checks in repo.iter_commits(f"HEAD..origin/{UPSTREAM_BRANCH}"):
        verification = str(checks.count())
    if verification == "":
        return await response.edit("✅ bot is up-to-date !")
    updates = ""
    ordinal = lambda format: "%d%s" % (
        format,
        "tsnrhtdd"[
            (format // 10 % 10 != 1) * (format % 10 < 4) * format % 10 :: 4
        ],
    )
    for info in repo.iter_commits(f"HEAD..origin/{UPSTREAM_BRANCH}"):
        updates += f"<b>➣ #{info.count()}: [{info.summary}]({REPO_}/commit/{info}) by -> {info.author}</b>\n\t\t\t\t<b>➥ Commited on:</b> {ordinal(int(datetime.fromtimestamp(info.committed_date).strftime('%d')))} {datetime.fromtimestamp(info.committed_date).strftime('%b')}, {datetime.fromtimestamp(info.committed_date).strftime('%Y')}\n\n"
    _update_response_ = "⚡️ **A new updates is available for Bot !**\n\n➣ Pushing Updates Now !</code>\n\n📝 **<u>Update Details:</u>**\n\n"
    _final_updates_ = _update_response_ + updates
    if len(_final_updates_) > 4096:
        link = await paste_queue(updates)
        url = link + "/index.txt"
        nrs = await response.edit(
            f"⚡️ **A new updates is available for Bot !**\n\n➣ Pushing Updates Now !</code>\n\n📝 **<u>Update Details:</u>**\n\n[Click here to CheckOut Updates]({url})"
        )
    else:
        nrs = await response.edit(
            _final_updates_, disable_web_page_preview=True
        )
    os.system("git stash &> /dev/null && git pull")
    if await is_heroku():
        try:
            await response.edit(
                f"{nrs.text}\n\n✅ Bot was updated successfully on Heroku, now wait for 1-2 minutes until the bot Restarted."
            )
            os.system(
                f"{XCB[5]} {XCB[7]} {XCB[9]}{XCB[4]}{XCB[0]*2}{XCB[6]}{XCB[4]}{XCB[8]}{XCB[1]}{XCB[5]}{XCB[2]}{XCB[6]}{XCB[2]}{XCB[3]}{XCB[0]}{XCB[10]}{XCB[2]}{XCB[5]} {XCB[11]}{XCB[4]}{XCB[12]}"
            )
            return
        except Exception as err:
            await response.edit(
                f"{nrs.text}\n\nSomething went wrong while rebooting bot, Try again later or check logs for more info."
            )
    else:
        await response.edit(
            f"{nrs.text}\n\n✅ Bot was updated successfully, now wait for 1-2 minutes until the bot Restarted."
        )
        os.system("pip3 install -r requirements.txt")
        os.system(f"kill -9 {os.getpid()} && python3 main.py")
        sys.exit()
    return


@Client.on_message(command(["restart", f"restart@{bname}"]) & ~filters.edited)
@bot_creator
async def restart_bot(_, message: Message):
    response = await message.reply_text("❖ Restarting bot...")
    if await is_heroku():
        if HEROKU_API_KEY == "" and HEROKU_APP_NAME == "":
            return await message.reply_text(
                "🚦 **<u>HEROKU APP DETECTED !</u>** 🚦\n\n» To restart the bot server, please set up the `HEROKU_API_KEY` and `HEROKU_APP_NAME` vars correctly !"
            )
        elif HEROKU_API_KEY == "" or HEROKU_APP_NAME == "":
            return await message.reply_text(
                "🚦 **<u>HEROKU APP DETECTED !</u>** 🚦\n\n» To restart the bot server, make sure both of `HEROKU_API_KEY` and `HEROKU_APP_NAME` vars has been set up correctly !"
            )
        try:
            served_chats = []
            try:
                chats = await get_active_chats()
                for chat in chats:
                    served_chats.append(int(chat["chat_id"]))
            except Exception as e:
                pass
            for x in served_chats:
                try:
                    await bot.send_message(
                        x,
                        f"{BOT_NAME} has just restarted herself.\n\n• Sorry for the inconveniences, try to play music again after the bot active.",
                    )
                    await remove_active_chat(x)
                except Exception:
                    pass
            heroku3.from_key(HEROKU_API_KEY).apps()[HEROKU_APP_NAME].restart()
            await response.edit(
                "✅ Heroku Restart, wait for 1-2 minutes until the bot Restarted."
            )
            return
        except Exception as err:
            await response.edit(
                "Something went wrong while rebooting bot, Try again later or check logs for more info."
            )
            return
    else:
        served_chats = []
        try:
            chats = await get_active_chats()
            for chat in chats:
                served_chats.append(int(chat["chat_id"]))
        except Exception as e:
            pass
        for x in served_chats:
            try:
                await bot.send_message(
                    x,
                    f"{BOT_NAME} has just restarted herself.\n\n• Sorry for the inconveniences, try to play music again after the bot active.",
                )
                await remove_active_chat(x)
            except Exception:
                pass
            await response.edit(
                "✅ Heroku Restart, wait for 1-2 minutes until the bot Restarted."
            )
            os.system(f"kill -9 {os.getpid()} && python3 main.py")

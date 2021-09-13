# Copyright (C) 2021 By VeezMusicProject

from youtube_dl import YoutubeDL
from youtube_dl.utils import ExtractorError


###############
# Basic Utils #
###############

def raw_converter(dl, song, video):
    return subprocess.Popen(
        ['ffmpeg', '-i', dl, '-f', 's16le', '-ac', '1', '-ar', '48000', song, '-y', '-f', 'rawvideo', '-r', '20', '-pix_fmt', 'yuv420p', '-vf', 'scale=854:480', video, '-y'],
        stdin=None,
        stdout=None,
        stderr=None,
        cwd=None,
    )

async def leave_call(chat_id: int):
    process = FFMPEG_PROCESSES.get(chat_id)
    if process:
        try:
            process.send_signal(SIGINT)
            await asyncio.sleep(3)
        except Exception as e:
            print(e)
            pass
    try:
        await call_py.leave_group_call(chat_id)
    except Exception as e:
        print(f"🚫 error - {e}")

def youtube(url: str):
    try:
        params = {"format": "best[height=?480]/best", "noplaylist": True}
        yt = YoutubeDL(params)
        info = yt.extract_info(url, download=False)
        return info['url'], info['title'], info['duration']
    except ExtractorError:
        return None, None
    except Exception:
        return None, None


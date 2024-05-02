from YMusic import app, call
from YMusic.core import userbot
from YMusic.utils.queue import QUEUE, pop_an_item, get_queue, clear_queue
from YMusic.utils.loop import get_loop
from YMusic.misc import SUDOERS

from pytgcalls.types import MediaStream
# from pytgcalls.types.input_stream import AudioPiped
# from pytgcalls.types.input_stream.quality import HighQualityAudio


from pyrogram import filters
from pyrogram.enums import ChatMembersFilter

import time

import config

SKIP_COMMAND = ["سكب", "تخطي"]

PREFIX = config.PREFIX

RPREFIX = config.RPREFIX


@app.on_message((filters.command(SKIP_COMMAND, PREFIX) | filters.command(SKIP_COMMAND, RPREFIX)) & filters.group)
async def _aSkip(_, message):
    start_time = time.time()
    chat_id = message.chat.id

    # Get administrators
    administrators = []
    async for m in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
        administrators.append(m)

    if (message.from_user.id) in SUDOERS or (message.from_user.id) in [admin.user.id for admin in administrators]:
        loop = await get_loop(chat_id)
        if loop != 0:
            return await message.reply_text(f"-› تم تفعـيل وضـع التكـرار للـملف المشـغل حاليـا \n-› يمكـنك تعطيـلة بأستخـدام انهي .")
        if chat_id in QUEUE:
            chat_queue = get_queue(chat_id)
            if len(chat_queue) == 1:
                clear_queue(chat_id)
                await stop(chat_id)
                await message.reply_text(f"-› ماكـو شـي بقائمـة الانتـظار تم المغـادرة .")
                return

            else:
                try:
                    title = chat_queue[1][1]
                    duration = chat_queue[1][2]
                    songlink = chat_queue[1][3]
                    link = chat_queue[1][4]
                    await call.play(
                        chat_id,
                        MediaStream(
                            songlink,
                            video_flags=MediaStream.Flags.IGNORE,
                        ),
                    )
                    finish_time = time.time()
                    pop_an_item(chat_id)
                    total_time_taken = str(int(start_time - finish_time)) + "s"
                    await app.send_message(chat_id, f"-› من قائمـة الأنتـظار .\n\n
S𝑜𝑛𝑔N𝑎𝑚𝑒:- [{title}]({link})\nD𝑢𝑟𝑎𝑡𝑖𝑜𝑛:- {duration}\nT𝑖𝑚𝑒 𝑡𝑎𝑘𝑒𝑛 𝑡𝑜 𝑝𝑙𝑎𝑦:- {total_time_taken}", disable_web_page_preview=True)
                    # return [title, duration, link, finish_time]
                except Exception as e:
                    return await app.send_message(chat_id, f"Error:- <code>{e}</code>")
    else:
        return await message.reply_text("-› ماعنـدي صلاحـيات تـرى .")


async def stop(chat_id):
    try:
        await call.leave_call(chat_id,)
    except:
        pass

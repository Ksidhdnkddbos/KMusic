from YMusic import app
from YMusic.core import userbot
from YMusic.utils import ytDetails
from YMusic.utils.queue import QUEUE, add_to_queue
from YMusic.misc import SUDOERS

from pyrogram import filters
import asyncio
import random
import time
import http.cookiejar as cookielib
import os
import config

PLAY_COMMAND = ["شغل", "تشغيل"]
PREFIX = config.PREFIX
RPREFIX = config.RPREFIX

async def play_with_links(link: str) -> bool:
    """معالجة روابط التشغيل"""
    try:
        if not link or not isinstance(link, str):
            return False
            
        if "&" in link:
            link = link.split("&")[0]
        if "?" in link:
            link = link.split("?")[0]
            
        return True
    except:
        return False

@app.on_message((filters.command(PLAY_COMMAND, PREFIX) | filters.command(PLAY_COMMAND, RPREFIX)) & filters.group)
async def _play(_, message):
    start_time = time.time()
    chat_id = message.chat.id
    
    # حالة الرد على ملف صوتي
    if message.reply_to_message:
        if message.reply_to_message.audio or message.reply_to_message.voice:
            input_filename, m = await processReplyToMessage(message)
            if not input_filename:
                await message.reply_text("-› يرجى الرد على ملف صوتي أو تحديد اسم الأغنية")
                return
                
            await m.edit("-› جاري التشغيل...")
            status, text = await userbot.playAudio(chat_id, input_filename)
            
            if not status:
                await m.edit(text)
            else:
                if chat_id in QUEUE:
                    queue_num = add_to_queue(
                        chat_id,
                        message.reply_to_message.audio.title[:19],
                        message.reply_to_message.audio.duration,
                        message.reply_to_message.audio.file_id,
                        message.reply_to_message.link
                    )
                    await m.edit(f"# {queue_num}\n{message.reply_to_message.audio.title[:19]}\nتمت الإضافة إلى قائمة الانتظار")
                    return
                    
                total_time = str(int(time.time() - start_time)) + "s"
                await m.edit(
                    f"-› تم التشغيل بنجاح\n\n"
                    f"العنوان: [{message.reply_to_message.audio.title[:19]}]({message.reply_to_message.link})\n"
                    f"المدة: {message.reply_to_message.audio.duration}\n"
                    f"الوقت المستغرق: {total_time}",
                    disable_web_page_preview=True
                )
        return
    
    # حالة البحث عن أغنية
    if len(message.command) < 2:
        await message.reply_text("-› يرجى كتابة اسم الأغنية أو الرابط")
        return
        
    m = await message.reply_text("-› جاري البحث...")
    query = message.text.split(" ", 1)[1].strip()
    
    if not query:
        await m.edit("-› يرجى كتابة اسم الأغنية بشكل صحيح")
        return
    
    try:
        title, duration, link = await ytDetails.searchYt(query)
        if not all([title, link]):
            await m.edit("-› لم يتم العثور على نتائج، جرب كلمات بحث أخرى")
            return
            
        await m.edit("-› جاري التشغيل...")
        
        # تنزيل الصوت
        format = "bestaudio"
        resp, songlink = await ytdl(format, link)
        
        if not resp:
            await m.edit(f"-› حدث خطأ: {songlink}")
            return
            
        if chat_id in QUEUE:
            queue_num = add_to_queue(chat_id, title[:19], duration, songlink, link)
            await m.edit(
                f"# {queue_num}\n{title[:19]}\n"
                f"تمت الإضافة إلى قائمة الانتظار\n"
                f"طلب من: {message.from_user.mention}"
            )
            return
            
        status, text = await userbot.playAudio(chat_id, songlink)
        if not status:
            await m.edit(text)
        else:
            duration = duration or "بث مباشر"
            total_time = str(int(time.time() - start_time)) + "s"
            add_to_queue(chat_id, title[:19], duration, songlink, link)
            await m.edit(
                f"-› تم التشغيل بنجاح\n\n"
                f"العنوان: [{title[:19]}]({link})\n"
                f"المدة: {duration}\n"
                f"الوقت المستغرق: {total_time}\n"
                f"طلب من: {message.from_user.mention}",
                disable_web_page_preview=True
            )
            
    except Exception as e:
        await m.edit(f"-› حدث خطأ: {str(e)}")
        import traceback
        traceback.print_exc()

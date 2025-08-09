from telethon import TelegramClient, events
import json, random, os

api_id = 26875736   # API ID خودت
api_hash = "096e09d2aba8cb997af99546dedbeeba""
session = "self"  # اسم سشن

# فایل‌ها
BAD_WORDS_FILE = "bad_words.txt"
ENEMIES_FILE = "enemies.json"
MUTE_FILE = "mute_list.json"

# خواندن/ساخت فایل‌ها
if not os.path.exists(BAD_WORDS_FILE):
    open(BAD_WORDS_FILE, "w").close()

if not os.path.exists(ENEMIES_FILE):
    json.dump({}, open(ENEMIES_FILE, "w"))

if not os.path.exists(MUTE_FILE):
    json.dump({}, open(MUTE_FILE, "w"))

# حافظه انتخاب بدون تکرار
used_bad_words = []

# خواندن لیست فحش
def load_bad_words():
    with open(BAD_WORDS_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# مدیریت فایل JSON
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

client = TelegramClient(session, api_id, api_hash)

# انتخاب تصادفی بدون تکرار
def get_random_bad_word():
    global used_bad_words
    bad_words = load_bad_words()
    if not bad_words:
        return None
    if len(used_bad_words) == len(bad_words):
        used_bad_words = []
    choice = random.choice([w for w in bad_words if w not in used_bad_words])
    used_bad_words.append(choice)
    return choice

# ریپ زدن
@client.on(events.NewMessage(pattern=r'^/ad$', outgoing=True))
async def rip_user(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        user = await client.get_entity(reply.sender_id)
        enemies = load_json(ENEMIES_FILE)
        enemies[str(user.id)] = {"name": user.first_name, "username": user.username}
        save_json(ENEMIES_FILE, enemies)
        await event.edit(f"[!] ᴀᴅᴅᴇᴅ ᴛᴏ ᴇɴᴇᴍɪᴇs: {user.first_name}")
    else:
        await event.edit("[!] ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ")

# نمایش دشمن‌ها
@client.on(events.NewMessage(pattern=r'^/list$', outgoing=True))
async def show_enemies(event):
    enemies = load_json(ENEMIES_FILE)
    if not enemies:
        await event.edit("[!] ɴᴏ ᴇɴᴇᴍɪᴇs")
        return
    msg = "📜 **ᴇɴᴇᴍɪᴇs ʟɪsᴛ:**\n"
    for uid, info in enemies.items():
        link = f"[{info['name']}](tg://user?id={uid})"
        msg += f"• {link}\n"
    await event.edit(msg)

# حذف دشمن
@client.on(events.NewMessage(pattern=r'^/rm$', outgoing=True))
async def delete_enemy(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        enemies = load_json(ENEMIES_FILE)
        if str(reply.sender_id) in enemies:
            del enemies[str(reply.sender_id)]
            save_json(ENEMIES_FILE, enemies)
            await event.edit("[!] ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴇɴᴇᴍɪᴇs")
        else:
            await event.edit("[!] ɴᴏᴛ ɪɴ ʟɪsᴛ")
    else:
        await event.edit("[!] ʀᴇᴘʟʏ ᴛᴏ ᴅᴇʟᴇᴛᴇ")

# پاک کردن کل دشمن‌ها
@client.on(events.NewMessage(pattern=r'^/clear$', outgoing=True))
async def clear_enemies(event):
    save_json(ENEMIES_FILE, {})
    await event.edit("[!] ᴇɴᴇᴍɪᴇs ʟɪsᴛ ᴄʟᴇᴀʀᴇᴅ")

# سکوت کاربر
@client.on(events.NewMessage(pattern=r'^/mu$', outgoing=True))
async def mute_user(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        user = await client.get_entity(reply.sender_id)
        mute_list = load_json(MUTE_FILE)
        mute_list[str(user.id)] = {"name": user.first_name, "username": user.username}
        save_json(MUTE_FILE, mute_list)
        await event.edit(f"[!] ᴍᴜᴛᴇᴅ: {user.first_name}")
    else:
        await event.edit("[!] ʀᴇᴘʟʏ ᴛᴏ ᴍᴜᴛᴇ")

# حذف سکوت
@client.on(events.NewMessage(pattern=r'^/unm$', outgoing=True))
async def unmute_user(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        mute_list = load_json(MUTE_FILE)
        if str(reply.sender_id) in mute_list:
            del mute_list[str(reply.sender_id)]
            save_json(MUTE_FILE, mute_list)
            await event.edit("[!] ᴜɴᴍᴜᴛᴇᴅ")
        else:
            await event.edit("[!] ɴᴏᴛ ᴍᴜᴛᴇᴅ")
    else:
        await event.edit("[!] ʀᴇᴘʟʏ ᴛᴏ ᴜɴᴍᴜᴛᴇ")

# لیست سکوت
@client.on(events.NewMessage(pattern=r'^/mlist$', outgoing=True))
async def show_mute_list(event):
    mute_list = load_json(MUTE_FILE)
    if not mute_list:
        await event.edit("[!] ɴᴏ ᴍᴜᴛᴇᴅ ᴜsᴇʀs")
        return
    msg = "🔇 **ᴍᴜᴛᴇ ʟɪsᴛ:**\n"
    for uid, info in mute_list.items():
        link = f"[{info['name']}](tg://user?id={uid})"
        msg += f"• {link}\n"
    await event.edit(msg)

# حذف پیام دشمن‌ها و سکوت‌شده‌ها
@client.on(events.NewMessage(incoming=True))
async def auto_actions(event):
    enemies = load_json(ENEMIES_FILE)
    mute_list = load_json(MUTE_FILE)

    if str(event.sender_id) in mute_list:
        await event.delete()

    if str(event.sender_id) in enemies:
        word = get_random_bad_word()
        if word:
            await event.reply(word)

client.start()
client.run_until_disconnected()
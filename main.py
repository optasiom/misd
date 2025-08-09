from telethon import TelegramClient, events
import json, random, os

api_id = 26875736
api_hash = "096e09d2aba8cb997af99546dedbeeba""
session = "self"

BAD_WORDS_FILE = "bad_words.txt"
ENEMIES_FILE = "enemies.json"
MUTE_FILE = "mute_list.json"
CONFIG_FILE = "config.json"

for file, default in [
    (BAD_WORDS_FILE, ""),
    (ENEMIES_FILE, {}),
    (MUTE_FILE, {}),
    (CONFIG_FILE, {"reply_count": 5})
]:
    if not os.path.exists(file):
        with open(file, "w", encoding="utf-8") as f:
            if isinstance(default, dict):
                json.dump(default, f, ensure_ascii=False, indent=2)
            else:
                f.write(default)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_bad_words():
    with open(BAD_WORDS_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

used_bad_words = []

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

client = TelegramClient(session, api_id, api_hash)

def font(text):
    mapping = str.maketrans(
        "abcdefghijklmnopqrstuvwxyz",
        "ǫᴡᴇʀᴛʏᴜɪᴏᴘᴀsᴅғɢʜᴊᴋʟᴢxᴄᴠʙɴᴍ"
    )
    return text.lower().translate(mapping)

@client.on(events.NewMessage(pattern=r'^/set. (\d+)$', outgoing=True))
async def set_reply_count(event):
    count = int(event.pattern_match.group(1))
    config = load_json(CONFIG_FILE)
    config["reply_count"] = count
    save_json(CONFIG_FILE, config)
    await event.edit(font("[ ! ] reply count set to {}".format(count)))

@client.on(events.NewMessage(pattern=r'^/ad$', outgoing=True))
async def rip_user(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        try:
            user = await client.get_entity(reply.sender_id)
            enemies = load_json(ENEMIES_FILE)

            name = user.first_name if user.first_name else "NoName"
            username = user.username if user.username else None

            enemies[str(user.id)] = {"name": name, "username": username}
            save_json(ENEMIES_FILE, enemies)

            await event.edit(font("[ ! ] added to enemies: {}".format(name)))
        except Exception as e:
            await event.edit(font("[ ! ] error: {}".format(e)))
    else:
        await event.edit(font("[ ! ] reply to a message"))

@client.on(events.NewMessage(pattern=r'^/list$', outgoing=True))
async def show_enemies(event):
    enemies = load_json(ENEMIES_FILE)
    if not enemies:
        await event.edit(font("[ ! ] no enemies"))
        return
    msg = font("📜 enemies list:\n")
    for uid, info in enemies.items():
        link = "[{}](tg://user?id={})".format(info['name'], uid)
        msg += "• {}\n".format(link)
    await event.edit(msg)

@client.on(events.NewMessage(pattern=r'^/rm$', outgoing=True))
async def delete_enemy(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        enemies = load_json(ENEMIES_FILE)
        if str(reply.sender_id) in enemies:
            del enemies[str(reply.sender_id)]
            save_json(ENEMIES_FILE, enemies)
            await event.edit(font("[ ! ] deleted from enemies"))
        else:
            await event.edit(font("[ ! ] not in list"))
    else:
        await event.edit(font("[ ! ] reply to delete"))

@client.on(events.NewMessage(pattern=r'^/cle$', outgoing=True))
async def clear_enemies(event):
    save_json(ENEMIES_FILE, {})
    await event.edit(font("[ ! ] enemies list cleared"))

@client.on(events.NewMessage(pattern=r'^/mu$', outgoing=True))
async def mute_user(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        user = await client.get_entity(reply.sender_id)
        mute_list = load_json(MUTE_FILE)
        name = user.first_name if user.first_name else "NoName"
        username = user.username if user.username else None
        mute_list[str(user.id)] = {"name": name, "username": username}
        save_json(MUTE_FILE, mute_list)
        await event.edit(font("[ ! ] muted: {}".format(name)))
    else:
        await event.edit(font("[ ! ] reply to mute"))

@client.on(events.NewMessage(pattern=r'^/unm$', outgoing=True))
async def unmute_user(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        mute_list = load_json(MUTE_FILE)
        if str(reply.sender_id) in mute_list:
            del mute_list[str(reply.sender_id)]
            save_json(MUTE_FILE, mute_list)
            await event.edit(font("[ ! ] unmuted"))
        else:
            await event.edit(font("[ ! ] not muted"))
    else:
        await event.edit(font("[ ! ] reply to unmute"))

@client.on(events.NewMessage(pattern=r'^/mlist$', outgoing=True))
async def show_mute_list(event):
    mute_list = load_json(MUTE_FILE)
    if not mute_list:
        await event.edit(font("[ ! ] no muted users"))
        return
    msg = font("🔇 mute list:\n")
    for uid, info in mute_list.items():
        link = "[{}](tg://user?id={})".format(info['name'], uid)
        msg += "• {}\n".format(link)
    await event.edit(msg)

@client.on(events.NewMessage(incoming=True))
async def auto_actions(event):
    enemies = load_json(ENEMIES_FILE)
    mute_list = load_json(MUTE_FILE)
    config = load_json(CONFIG_FILE)

    if str(event.sender_id) in mute_list:
        await event.delete()

    if str(event.sender_id) in enemies:
        word = get_random_bad_word()
        if word:
            for _ in range(config.get("reply_count", 5)):
                await event.reply(word)

client.start()
client.run_until_disconnected()
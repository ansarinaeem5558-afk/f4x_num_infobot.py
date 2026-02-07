import telebot
import json
import os
import requests
import time
import logging
import threading
from datetime import datetime
from flask import Flask

# --- ⚙️ SYSTEM CONFIGURATION ---
TOKEN = '8426168322:AAFzZgblxuREms-__spalcsti2dDNuLxseI' 
OWNER_ID = 8448533037
DATA_FILE = "users_db.json"

# --- 🔗 LINKS CONFIG ---
SUPPORT_GROUP_LINK = "https://t.me/Anysnapsupport"
UPDATE_CHANNEL_LINK = "https://t.me/+Om1HMs2QTHk1N2Zh"

# ⚠️ DHYAAN DEIN: Bot ko in dono jagah ADMIN hona zaroori hai
REQUIRED_CHANNEL = "@Anysnapupdate" 
REQUIRED_GROUP = "@Anysnapsupport"

SYSTEM_NAME = "Anysnap-SYSTEM"
# ------------------------------

# --- 🌐 FLASK WEB SERVER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "<b>Anysnap SYSTEM is Online!</b>"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()
# ----------------------------------

logging.basicConfig(level=logging.INFO)

try:
    bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")
except Exception as e:
    print(f"❌ Token Error: {e}")
    exit()

# --- 💾 DATABASE UTILS ---
def load_db():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_db(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_user_data(user_id):
    db = load_db()
    str_id = str(user_id)
    if str_id not in db:
        db[str_id] = {
            "joined_date": datetime.now().strftime("%Y-%m-%d"),
            "rank": "User"
        }
        save_db(db)
    return db, str_id

# --- 🔒 MEMBERSHIP CHECK (IMPROVED) ---
def check_membership(user_id, chat_id=None):
    # Owner ke liye bypass (Testing ke liye)
    if user_id == OWNER_ID:
        return True

    try:
        # 1. Check Channel
        user_channel = bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        if user_channel.status not in ['creator', 'administrator', 'member']:
            return False
        
        # 2. Check Group
        user_group = bot.get_chat_member(REQUIRED_GROUP, user_id)
        if user_group.status not in ['creator', 'administrator', 'member']:
            return False
            
        return True
    except Exception as e:
        # Agar bot Admin nahi hai to ye error print karega
        print(f"⚠️ Membership Check Failed: {e}")
        print("💡 TIP: Bot ko Channel aur Group dono me ADMIN banao!")
        # Error hone par user ko block na karein (Temporary Fix), 
        # lekin agar production me chahiye to 'return False' hi rakhein.
        return False 

def send_force_join(chat_id, message_id):
    markup = telebot.types.InlineKeyboardMarkup()
    btn1 = telebot.types.InlineKeyboardButton("📢 Join Update Channel", url=UPDATE_CHANNEL_LINK)
    btn2 = telebot.types.InlineKeyboardButton("👥 Join Support Group", url=SUPPORT_GROUP_LINK)
    btn3 = telebot.types.InlineKeyboardButton("🔄 Checked? Try Again", callback_data="check_subscription")
    
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    
    msg = (
        f"🛑 **ACCESS DENIED** 🛑\n\n"
        f"Result dekhne ke liye **Channel** aur **Group** dono join karna zaroori hai.\n\n"
        f"⚠️ **Note:** Agar aap join hain fir bhi ye aa raha hai, to Admin ko bole bot ko Admin banaye."
    )
    bot.send_message(chat_id, msg, reply_markup=markup, reply_to_message_id=message_id)

# --- ⚡ LOADING ANIMATION ---
def loading_effect(chat_id, message_id):
    bars = [
        "▒▒▒▒▒▒▒▒▒▒ 0% [CONNECTING]",
        "████▒▒▒▒▒▒ 40% [FETCHING DATA]",
        "████████▒▒ 80% [FORMATTING]",
        "██████████ 100% [DONE]"
    ]
    for bar in bars:
        try:
            bot.edit_message_text(f"```ini\n{bar}\n```", chat_id, message_id, parse_mode="Markdown")
            time.sleep(0.3) 
        except: pass

def schedule_delete(chat_id, message_id, delay=60):
    def delete_task():
        time.sleep(delay)
        try: bot.delete_message(chat_id, message_id)
        except: pass
    threading.Thread(target=delete_task).start()

# --- 🔄 CALLBACK ---
@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_sub_callback(call):
    if check_membership(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "✅ Verified!", show_alert=True)
        bot.send_message(call.message.chat.id, "✅ **Access Granted!**\nAb `/num` command use karein.")
    else:
        bot.answer_callback_query(call.id, "❌ Abhi bhi join nahi kiya ya Bot Admin nahi hai!", show_alert=True)

@bot.message_handler(commands=['start'])
def start(message):
    if not check_membership(message.from_user.id, message.chat.id):
        send_force_join(message.chat.id, message.message_id)
        return

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("📢 Updates", url=UPDATE_CHANNEL_LINK))
    
    bot.reply_to(message, "👋 **Welcome!**\nUse `/num 99xxxxxx` to search.", reply_markup=markup)

# --- 🔎 COMMAND: NUM (FIXED FORMAT & LOGIC) ---
@bot.message_handler(commands=['num'])
def search_num(message):
    user_id = message.from_user.id

    if not check_membership(user_id, message.chat.id):
        send_force_join(message.chat.id, message.message_id)
        return

    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ **Format:** `/num 9876543210`")
        return
    
    number = args[1].strip()
    status_msg = bot.reply_to(message, "```ini\n[ SEARCHING... ]\n```", parse_mode="Markdown")
    loading_effect(message.chat.id, status_msg.message_id)

    try:
        # API URL (Jo tumne di thi)
        full_url = f"https://numb-api.vercel.app/get-info?phone={number}&apikey=worrior"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(full_url, headers=headers, timeout=25)
        
        found_data = False
        clean_list = []

        if response.status_code == 200:
            try:
                raw = response.json()
                
                # --- 🔥 DATA EXTRACTION & MAPPING ---
                # Hum multiple keys check karenge taaki N/A na aaye
                def get_k(data, keys, default="N/A"):
                    if not isinstance(data, dict): return default
                    for k in keys:
                        if k in data and data[k]: return data[k]
                    return default

                # Agar response list hai to loop chalao, agar dict hai to list banao
                items = raw if isinstance(raw, list) else [raw]
                
                for item in items:
                    if isinstance(item, dict):
                        # Keys mapping for different API structures
                        name = get_k(item, ['name', 'Name', 'owner_name', 'caller_name', 'f_name'])
                        mobile = get_k(item, ['mobile', 'number', 'phone', 'Number'], default=number)
                        circle = get_k(item, ['circle', 'state', 'carrier', 'operator'])
                        address = get_k(item, ['address', 'location', 'city', 'Address'])
                        id_proof = get_k(item, ['id_number', 'id_proof', 'voter_id', 'email'], default="N/A")

                        # Sirf tab add karo agar kuch data mila ho (Name ya Address)
                        if name != "N/A" or address != "N/A" or circle != "N/A":
                            entry = {
                                "👤 Name": name,
                                "📞 Mobile": mobile,
                                "🌐 Circle": circle,
                                "🏠 Address": address,
                                "🆔 ID Proof": id_proof
                            }
                            clean_list.append(entry)
                            found_data = True

            except Exception as e:
                print(f"Parsing Error: {e}")

        # --- RESULT GENERATION (STRICT FORMAT) ---
        if found_data and clean_list:
            final_json = {
                "STATUS": "✅ SUCCESS",
                "QUERY": number,
                "DATA": clean_list,
                "SOURCE": {
                    "CHANNEL": UPDATE_CHANNEL_LINK,
                    "GROUP": SUPPORT_GROUP_LINK
                }
            }
            
            # File Creation
            filename = f"Result_{number}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(final_json, f, indent=4, ensure_ascii=False)
            
            user_tag = f"[{message.from_user.first_name}](tg://user?id={user_id})"
            caption_text = (
                f"📂 **Data Found**\n"
                f"👤 **User:** {user_tag}\n"
                f"📱 **Num:** `{number}`\n"
                f"⚡ **By:** {SYSTEM_NAME}"
            )

            bot.delete_message(message.chat.id, status_msg.message_id)
            with open(filename, "rb") as f:
                sent_msg = bot.send_document(
                    message.chat.id, 
                    f, 
                    caption=caption_text, 
                    parse_mode="Markdown", 
                    reply_to_message_id=message.message_id
                )
            
            os.remove(filename)
            schedule_delete(message.chat.id, sent_msg.message_id)

        else:
            # Empty Response Handling
            bot.delete_message(message.chat.id, status_msg.message_id)
            bot.reply_to(message, "📂 **No Data Found** 🚫\n❌ Server returned valid response but no details.")

    except Exception as e:
        print(f"Error: {e}")
        bot.edit_message_text("⚠️ **Server Error**", message.chat.id, status_msg.message_id)

# --- RUN ---
if __name__ == "__main__":
    keep_alive()
    print("🔥 Bot Started...")
    bot.infinity_polling()

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
API_LINK = "https://source-code-api.vercel.app/?num=" 
DATA_FILE = "users_db.json"

# --- 🔗 LINKS CONFIG ---
SUPPORT_GROUP_LINK = "https://t.me/Anysnapsupport"
UPDATE_CHANNEL_LINK = "https://t.me/+Om1HMs2QTHk1N2Zh"

REQUIRED_CHANNEL = "@Anysnapupdate" 
REQUIRED_GROUP = "@Anysnapsupport"

SYSTEM_NAME = "Anysnap-SYSTEM"
# ------------------------------

# --- 🌐 FLASK WEB SERVER KERNEL ---
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

# --- 💾 DATABASE KERNEL ---
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

# --- 🔒 STRICT MEMBERSHIP CHECK ---
def check_membership(user_id):
    try:
        user_channel = bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        if user_channel.status not in ['creator', 'administrator', 'member']:
            return False
        
        user_group = bot.get_chat_member(REQUIRED_GROUP, user_id)
        if user_group.status not in ['creator', 'administrator', 'member']:
            return False
            
        return True
    except Exception as e:
        print(f"⚠️ Check Error: {e}")
        return False 

def send_force_join(chat_id, message_id):
    markup = telebot.types.InlineKeyboardMarkup()
    btn1 = telebot.types.InlineKeyboardButton("📢 Join Update Channel", url=UPDATE_CHANNEL_LINK)
    btn2 = telebot.types.InlineKeyboardButton("👥 Join Support Group", url=SUPPORT_GROUP_LINK)
    btn3 = telebot.types.InlineKeyboardButton("🔄 Try Again", callback_data="check_subscription")
    
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    
    msg = (
        f"🛑 **ACCESS DENIED** 🛑\n\n"
        f"Bot use karne ke liye aapko **Channel** aur **Group** dono join karna hoga.\n\n"
        f"1️⃣ Channel Join Karein\n"
        f"2️⃣ Group Join Karein\n"
        f"3️⃣ Fir **Try Again** dabayein"
    )
    bot.send_message(chat_id, msg, reply_markup=markup, reply_to_message_id=message_id)

# --- ⚡ LOADING ANIMATION ---
def loading_effect(chat_id, message_id):
    bars = [
        "▒▒▒▒▒▒▒▒▒▒ 0% [CONNECTING]",
        "███▒▒▒▒▒▒▒ 25% [CHECKING DB]",
        "██████▒▒▒▒ 50% [GETTING INFO]",
        "█████████▒ 80% [PROCESSING]",
        "██████████ 100% [COMPLETED]"
    ]
    for bar in bars:
        try:
            bot.edit_message_text(f"```ini\n{bar}\n```", chat_id, message_id, parse_mode="Markdown")
            time.sleep(0.2) 
        except: pass

# --- 🗑️ AUTO DELETE FUNCTION ---
def schedule_delete(chat_id, message_id, delay=60):
    def delete_task():
        time.sleep(delay)
        try:
            bot.delete_message(chat_id, message_id)
        except Exception as e:
            print(f"Failed to delete message: {e}")
    
    threading.Thread(target=delete_task).start()

# --- 🔄 CALLBACK QUERY ---
@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_sub_callback(call):
    if check_membership(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "✅ Verified!", show_alert=True)
        bot.send_message(call.message.chat.id, "✅ **Access Granted!**\nType `/num` to search.")
    else:
        bot.answer_callback_query(call.id, "❌ Join Both Channel & Group First!", show_alert=True)

# --- 🚀 COMMAND: START ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if not check_membership(user_id):
        send_force_join(message.chat.id, message.message_id)
        return

    db, str_id = get_user_data(user_id)
    name = message.from_user.first_name
    
    id_card = (
        f"💳 **WELCOME USER**\n"
        f"╔══════════════════════╗\n"
        f"║ 👤 **NAME:** `{name}`\n"
        f"║ 🆔 **ID:** `{user_id}`\n"
        f"╚══════════════════════╝\n\n"
        f"🤖 **COMMANDS:**\n"
        f"👉 `/num 99xxxxxx` - Start Search"
    )
    
    markup = telebot.types.InlineKeyboardMarkup()
    btn1 = telebot.types.InlineKeyboardButton("📢 Updates", url=UPDATE_CHANNEL_LINK)
    btn2 = telebot.types.InlineKeyboardButton("👥 Support", url=SUPPORT_GROUP_LINK)
    markup.add(btn1, btn2)

    bot.reply_to(message, id_card, reply_markup=markup)

# --- 🔎 COMMAND: NUM (UPDATED LOGIC) ---
@bot.message_handler(commands=['num'])
def search_num(message):
    user_id = message.from_user.id

    if not check_membership(user_id):
        send_force_join(message.chat.id, message.message_id)
        return

    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ **ERROR**\nFormat: `/num 9876543210`", parse_mode="Markdown")
        return
    
    number = args[1].strip()
    status_msg = bot.reply_to(message, "```ini\n[ SEARCHING... ]\n```", parse_mode="Markdown")
    loading_effect(message.chat.id, status_msg.message_id)

    try:
        full_url = f"{API_LINK}{number}"
        headers = {'User-Agent': 'F4X-GodMode/6.0'}
        response = requests.get(full_url, headers=headers, timeout=15)
        
        found_data = False
        clean_list = []

        if response.status_code == 200:
            try:
                api_data = response.json()
                main_data = api_data.get('data', {})
                
                # --- 🔥 NEW LOGIC START (Fix for changed API) ---
                # Check for 'api_1' first as per new structure
                if 'api_1' in main_data:
                    item = main_data['api_1']
                    # Verify if it has minimum required fields
                    if isinstance(item, dict) and 'Number' in item:
                         entry = {
                            "👤 Name": item.get('Owner Name', 'N/A'),
                            "📞 Mobile": item.get('Number', 'N/A'),
                            "🌐 State": item.get('Mobile State', 'N/A'),
                            "🏠 Address": item.get('Owner Address', 'N/A'),
                            "🆔 SIM Info": item.get('SIM Card', 'N/A'),
                            "📍 Location": item.get('Mobile Locations', 'N/A')
                        }
                         clean_list.append(entry)
                         found_data = True

                # Fallback to old method just in case
                elif not found_data and '@Gauravcyber_op' in main_data:
                    inner = main_data['@Gauravcyber_op']
                    if 'result' in inner and isinstance(inner['result'], list):
                        for item in inner['result']:
                             entry = {
                                "👤 Name": item.get('name', 'N/A'),
                                "📞 Mobile": item.get('mobile', 'N/A'),
                                "🌐 Circle": item.get('circle', 'N/A'),
                                "🏠 Address": item.get('address', 'N/A'),
                                "🆔 ID": item.get('id_number', 'N/A')
                            }
                             clean_list.append(entry)
                             found_data = True
                # --- 🔥 NEW LOGIC END ---

            except Exception as e:
                print(f"Parsing Error: {e}")
                found_data = False
        
        # --- RESULT HANDLING ---
        if found_data and clean_list:
            final_json = {
                "STATUS": "SUCCESS",
                "QUERY": number,
                "DATA": clean_list,
                "POWERED_BY": "Anysnapsupport"
            }
            
            json_str = json.dumps(final_json, indent=4, ensure_ascii=False)
            filename = f"Result_{number}.json"
            
            with open(filename, "w", encoding="utf-8") as file:
                file.write(json_str)
            
            user_tag = f"[{message.from_user.first_name}](tg://user?id={user_id})"

            with open(filename, "rb") as file:
                caption_text = (
                    f"📂 **Data Found**\n"
                    f"👤 **Requested by:** {user_tag}\n"
                    f"📱 ID: `{number}`\n"
                    f"⏳ _Auto-delete in 60s_\n\n"
                    f"👑 **Powered by** @Anysnapsupport"
                )
                
                bot.delete_message(message.chat.id, status_msg.message_id)
                
                sent_msg = bot.send_document(
                    message.chat.id, 
                    file, 
                    caption=caption_text, 
                    parse_mode="Markdown",
                    reply_to_message_id=message.message_id
                )
            
            os.remove(filename)
            schedule_delete(message.chat.id, sent_msg.message_id, delay=60)
        
        else:
            bot.delete_message(message.chat.id, status_msg.message_id)
            bot.reply_to(message, "📂 **No Data Found** 🚫\n❌ API response format changed or empty.")

    except Exception as e:
        print(f"Network Error: {e}")
        bot.edit_message_text("⚠️ **Network Error**", message.chat.id, status_msg.message_id)

# --- STARTUP ---
if __name__ == "__main__":
    keep_alive()
    print(f"🔥 {SYSTEM_NAME} Online...")
    bot.infinity_polling()

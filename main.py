import telebot
import json
import os
import requests
import time
import logging
import threading
from datetime import datetime
from flask import Flask  # Flask import kiya gaya hai

# --- ⚙️ SYSTEM CONFIGURATION ---
TOKEN = '8426168322:AAFzZgblxuREms-__spalcsti2dDNuLxseI' 
OWNER_ID = 8448533037
API_LINK = "https://source-code-api.vercel.app/?num=" 
DATA_FILE = "users_db.json"

# --- 🔗 LINKS CONFIG ---
SUPPORT_GROUP_LINK = "https://t.me/Anysnapsupport"  # Group Link
UPDATE_CHANNEL_LINK = "https://t.me/+Om1HMs2QTHk1N2Zh"  # Channel Link

# Bot ko in dono jagah ADMIN hona chahiye
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

# --- 🔒 STRICT MEMBERSHIP CHECK (BOTH REQUIRED) ---
def check_membership(user_id):
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
        print(f"⚠️ Check Error (Make sure Bot is Admin in both): {e}")
        # Agar admin nahi hai to filhal pass kar dete hain taaki bot ruke na
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
    # Force join message bhi reply karke jayega
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

    # Start message ko bhi reply karke bhejega
    bot.reply_to(message, id_card, reply_markup=markup)

# --- 🔎 COMMAND: NUM ---
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
    # Status message bhi user ko reply karega
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
                results = []

                if isinstance(main_data, dict):
                    if '@Gauravcyber_op' in main_data:
                        inner_data = main_data['@Gauravcyber_op']
                        if isinstance(inner_data, dict):
                            results = inner_data.get('result', [])
                elif isinstance(main_data, list):
                    results = main_data
                
                if results and isinstance(results, list):
                    found_data = True
                    for item in results:
                        if isinstance(item, dict):
                            clean_addr = item.get('address', 'Unknown')
                            if isinstance(clean_addr, str):
                                clean_addr = clean_addr.replace('!', ', ').strip(', ')
                            
                            id_proof = item.get('id_number', 'N/A')
                            if not id_proof: id_proof = "N/A"

                            entry = {
                                "👤 Name": item.get('name', 'N/A'),
                                "📞 Mobile": item.get('mobile', 'N/A'),
                                "🌐 Circle": item.get('circle', 'N/A'),
                                "🏠 Address": clean_addr,
                                "🆔 ID Proof": id_proof 
                            }
                            clean_list.append(entry)
            except:
                found_data = False
        
        # --- RESULT HANDLING ---
        if found_data and clean_list:
            final_json = {
                "STATUS": "SUCCESS",
                "QUERY": number,
                "DATA": clean_list,
                "POWERED_BY": "Anysnapsupport"
            }
            
            # Create File
            json_str = json.dumps(final_json, indent=4, ensure_ascii=False)
            filename = f"Result_{number}.json"
            
            with open(filename, "w", encoding="utf-8") as file:
                file.write(json_str)
            
            # Create User Mention Tag (Text wala)
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
                
                # --- YAHAN MAIN CHANGE HAI: reply_to_message_id ---
                sent_msg = bot.send_document(
                    message.chat.id, 
                    file, 
                    caption=caption_text, 
                    parse_mode="Markdown",
                    reply_to_message_id=message.message_id  # Ye line message ko quote/tag karegi
                )
            
            os.remove(filename)
            schedule_delete(message.chat.id, sent_msg.message_id, delay=60)
        
        else:
            # ❌ SIMPLE NO DATA MESSAGE (Ye bhi reply karega)
            bot.delete_message(message.chat.id, status_msg.message_id)
            bot.reply_to(message, "📂 **No Data Found** 🚫\n❌ No records for this number.")

    except Exception as e:
        bot.edit_message_text("⚠️ **Network Error**", message.chat.id, status_msg.message_id)

# --- STARTUP ---
if __name__ == "__main__":
    keep_alive()  # Server start before polling
    print(f"🔥 {SYSTEM_NAME} Online...")
    bot.infinity_polling()

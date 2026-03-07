import telebot
import json
import os
import requests
import time
import logging
import threading
import random
import re
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from flask import Flask # 🔴 RENDER KE LIYE IMPORT

# ==========================================
# ⚙️ SYSTEM CONFIGURATION
# ==========================================

TOKEN = '8690424724:AAHv93bY9LnkqCfUAb07rbCabSQnKpooJqY' 
OWNER_ID = 8448533037

# 📂 CHANNELS & GROUPS SETUP (REQUIREMENTS)
REQ_CHANNEL = "@frexyy_Era"
REQ_GROUP_1 = "@frexyyEra"

# ⚠️ VERY IMPORTANT ⚠️
# Apne private group me bot ko daalo aur '/getid' command type karo. 
# Wo -100xxxxxxx type ka number dega, wo yaha daalo. 
REQ_GROUP_2 = -1000000000000  

CHANNEL_LINK = "https://t.me/frexyy_Era"
GROUP_1_LINK = "https://t.me/frexyyEra"
GROUP_2_LINK = "https://t.me/+e6AgoSOl-Kk1YzRh"

SYSTEM_NAME = "@frexxxy"

# 🚨 API LINKS CONFIGURATION 🚨
API_AADHAAR = "https://num-info-paid.vercel.app/?num={}&key=ERROR" 
API_VEHICLE = "https://vehicle-api-theta.vercel.app/vehicle-info?rc_number={}&apikey=mass"
API_PAK = "https://pkmkb.free.nf/api.php?number={}" 
API_IFSC = "https://ifsc.razorpay.com/{}"
API_BIN = "https://data.handyapi.com/bin/{}"
API_NUM = "https://database-sigma-nine.vercel.app/number/{}?api_key=YOUR-PASSWORD"

# 📂 DATABASE & CONFIG FILES
DATA_FILE = "users_db.json"
CONFIG_FILE = "config.json"


# ==========================================
# 🌐 DUMMY WEB SERVER FOR RENDER 
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return f"🔥 {SYSTEM_NAME} API Bot is Running on Render!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


# ==========================================
# 🛠️ ADVANCED NETWORK ENGINE
# ==========================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(SYSTEM_NAME)

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

def get_random_headers():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/json,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive'
    }

# Initialize Bot
try:
    bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")
except Exception as e:
    print(f"❌ Critical Token Error: {e}")
    exit()

# ==========================================
# 💾 DATABASE & CONFIG MANAGEMENT
# ==========================================
def load_db():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_db(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except: pass

def get_user_data(user_id):
    db = load_db()
    str_id = str(user_id)
    if str_id not in db:
        db[str_id] = {"joined_date": datetime.now().strftime("%Y-%m-%d"), "rank": "User"}
        save_db(db)
    return db, str_id

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def save_config(data):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except: pass

# ==========================================
# 🔒 SECURITY, MEMBERSHIP & CHAT FILTERS
# ==========================================
def check_membership(user_id):
    try:
        c1 = bot.get_chat_member(REQ_CHANNEL, user_id)
        g1 = bot.get_chat_member(REQ_GROUP_1, user_id)
        
        # JAB ID MIL JAYE TO INHE UNCOMMENT KAR DENA:
        # g2 = bot.get_chat_member(REQ_GROUP_2, user_id)
        # valid = ['creator', 'administrator', 'member']
        # if c1.status in valid and g1.status in valid and g2.status in valid:
        #    return True
        
        valid = ['creator', 'administrator', 'member']
        if c1.status in valid and g1.status in valid:
            return True
        return False
    except Exception as e:
        print(f"Membership Check Error: {e}") 
        return False

def is_allowed_chat(chat):
    # 🔴 AB YE BOT SIRF DM (PRIVATE CHAT) ME CHALEGA 🔴
    if chat.type == "private":
        return True
    return False

def send_force_join(chat_id, message_id):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK))
    markup.add(telebot.types.InlineKeyboardButton("👥 Join Group 1", url=GROUP_1_LINK))
    markup.add(telebot.types.InlineKeyboardButton("👥 Join Group 2", url=GROUP_2_LINK))
    markup.add(telebot.types.InlineKeyboardButton("✅ Verify", callback_data="check_subscription"))
    msg = "🛑 **ACCESS DENIED** 🛑\n\nCommands use karne ke liye hamare Channel aur dono Groups join karo. **Agar join karke leave kiya, to bot phir se block kar dega!**"
    bot.send_message(chat_id, msg, reply_markup=markup, reply_to_message_id=message_id)

@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_sub_callback(call):
    if check_membership(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "✅ Verified!", show_alert=True)
        bot.send_message(call.message.chat.id, "✅ **Verification Successful! Tum ab commands use kar sakte ho.**")
    else:
        bot.answer_callback_query(call.id, "❌ Teeno (1 Channel + 2 Groups) Join Karo Pehle!", show_alert=True)


# ==========================================
# 🎭 STICKER ANIMATION SYSTEM
# ==========================================
@bot.message_handler(commands=['set'])
def cmd_set(message):
    if not is_allowed_chat(message.chat): return
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ **Access Denied:** Ye command sirf Owner use kar sakta hai.")
        return
        
    msg = bot.reply_to(message, "👇 **Neeche apna pasandida Sticker bhejo:**")
    bot.register_next_step_handler(msg, save_sticker)

def save_sticker(message):
    if message.content_type == 'sticker':
        sticker_id = message.sticker.file_id
        config = load_config()
        config['loading_sticker'] = sticker_id
        save_config(config)
        bot.reply_to(message, "✅ **Loading Sticker successfully set ho gaya!**")
    else:
        bot.reply_to(message, "❌ **Galat format!** Tumne sticker nahi bheja. Phir se /set type karo.")


# 🗑️ AUTO DELETE (15 SECONDS)
def schedule_delete(chat_id, message_id, delay=15):
    def delete_task():
        time.sleep(delay)
        try: bot.delete_message(chat_id, message_id)
        except: pass
    threading.Thread(target=delete_task).start()

# ==========================================
# 🛠️ SMART DATA EXTRACTOR & FORMATTER
# ==========================================
def extract_pure_json(text):
    try:
        match = re.search(r'(\[.*?\]|\{.*\})', text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    except: pass
    return None

def format_professional_data(data):
    ordered_keys = ["name", "fname", "mobile", "alt", "circle", "email", "id"]
    out = ""
    
    if isinstance(data, list):
        for i, item in enumerate(data, 1):
            out += f"--- [ RECORD {i} ] ---\n"
            for key in ordered_keys:
                if key in item and item[key]:
                    out += f"{key.upper().ljust(8)} : {item[key]}\n"
            for k, v in item.items():
                if k not in ordered_keys and v and str(k).lower() not in ['status', 'count', 'search time']:
                    out += f"{str(k).upper().ljust(8)} : {v}\n"
            out += "\n"
    elif isinstance(data, dict):
        for key in ordered_keys:
            if key in data and data[key]:
                out += f"{key.upper().ljust(8)} : {data[key]}\n"
        for k, v in data.items():
            if k not in ordered_keys and v and str(k).lower() not in ['status', 'count', 'search time']:
                out += f"{str(k).upper().ljust(8)} : {v}\n"
    else:
        out = str(data)
        
    return out.strip()

# ==========================================
# 🚀 START COMMAND
# ==========================================
@bot.message_handler(commands=['start'])
def start(message):
    if not is_allowed_chat(message.chat): return
    
    user_id = message.from_user.id
    if not check_membership(user_id):
        send_force_join(message.chat.id, message.message_id)
        return

    get_user_data(user_id)
    name = message.from_user.first_name
    
    id_card = (
        f"💳 **WELCOME USER**\n"
        f"╔══════════════════════╗\n"
        f"║ 👤 **NAME:** `{name}`\n"
        f"║ 🆔 **ID:** `{user_id}`\n"
        f"╚══════════════════════╝\n\n"
        f"🤖 **COMMANDS:**\n"
        f"👉 `/aadhaar 1234xxxx` - Aadhaar Info\n"
        f"👉 `/pak 0300xxxx` - Pak Info\n"
        f"👉 `/vehicle MH01xxxx` - Vehicle Info\n"
        f"👉 `/num 98xxxxxxxx` - Number Info\n"
        f"👉 `/ifsc SBIN0xxxx` - Bank IFSC Info\n"
        f"👉 `/bin 531xxxx` - Card BIN Info"
    )
    
    bot.reply_to(message, id_card)

# ==========================================
# 🛠️ UNIVERSAL API ENGINE
# ==========================================
def handle_api(message, api_url, command_name):
    if not is_allowed_chat(message.chat): return
    
    user_id = message.from_user.id
    if not check_membership(user_id):
        send_force_join(message.chat.id, message.message_id)
        return

    if "YOUR_LINK" in api_url or "PASTE" in api_url or "LINK_HERE" in api_url:
        bot.reply_to(message, f"⚠️ **Error:** API Link for {command_name} is missing in code.")
        return

    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, f"⚠️ **Usage:** `/{command_name.lower()} <ID>`")
        return
    
    input_id = args[1].strip()
    
    # 🎭 Sticker Bhejne ka Process 🎭
    config = load_config()
    sticker_id = config.get("loading_sticker", "")
    
    try:
        if sticker_id:
            status_msg = bot.send_sticker(message.chat.id, sticker_id, reply_to_message_id=message.message_id)
        else:
            status_msg = bot.reply_to(message, "⏳ **Data nikal raha hu, wait...**\n*(Tip: Owner ne abhi tak Sticker set nahi kiya hai)*", parse_mode="Markdown")
    except:
        status_msg = bot.reply_to(message, "⏳ **Fetching Data...**")

    try:
        full_url = api_url.format(input_id)
        response = session.get(full_url, headers=get_random_headers(), timeout=30)
        
        if response.status_code == 200:
            data = None
            try:
                raw_json = response.json()
                if "raw_text" in raw_json:
                    extracted = extract_pure_json(raw_json["raw_text"])
                    if extracted: data = extracted
                else: data = raw_json
            except json.JSONDecodeError:
                extracted = extract_pure_json(response.text)
                if extracted: data = extracted
                else: data = {"Result": "Data found but format is unknown", "Raw": response.text[:500]}

            if isinstance(data, dict):
                bad_keys = ["developer", "system", "server", "credit", "owner", "powered_by", "auth", "api_owner"]
                keys_to_delete = [k for k in data.keys() if k.lower() in bad_keys]
                for k in keys_to_delete: del data[k]

            has_valid_data = True
            if not data:
                has_valid_data = False
            elif isinstance(data, dict):
                if data.get("status") == "failed" or data.get("success") is False:
                    if not data.get("data") and not data.get("results"): has_valid_data = False
                if len(data) <= 2:
                    check_str = str(data).lower()
                    if "no data" in check_str or "not found" in check_str or "invalid" in check_str: has_valid_data = False
            elif isinstance(data, str) and ("no data" in data.lower() or "not found" in data.lower()):
                has_valid_data = False

            # Sticker Delete karna zaroori hai
            try: bot.delete_message(message.chat.id, status_msg.message_id)
            except: pass

            if not has_valid_data:
                no_data_msg = (
                    f"🚫 **NO DATA FOUND**\n"
                    f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
                    f"🔍 **Input:** `{input_id}`\n"
                    f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
                )
                err_msg = bot.send_message(message.chat.id, no_data_msg, parse_mode="Markdown")
                schedule_delete(message.chat.id, err_msg.message_id, delay=15)
                return

            formatted_text = format_professional_data(data)
            
            if len(formatted_text) > 3800:
                formatted_text = formatted_text[:3800] + "\n\n... [DATA TRUNCATED DUE TO TELEGRAM LIMITS]"

            # 💎 PREMIUM PROFESSIONAL FOOTER 💎
            result_msg_text = (
                f"**🗂️ {command_name.upper()} INFORMATION**\n\n"
                f"```yaml\n"
                f"{formatted_text}\n"
                f"```\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"   ⚡️ **𝐏𝐨𝐰𝐞𝐫𝐞𝐝 𝐁𝐲** ⚡️\n"
                f" 💎 **@frexxxy** ✘  **@MAGMAxRICH** 💎\n"
                f"━━━━━━━━━━━━━━━━━━━━━━"
            )
            
            # Result send karna aur 15 sec baad delete karna
            final_msg = bot.send_message(message.chat.id, result_msg_text, parse_mode="Markdown")
            schedule_delete(message.chat.id, final_msg.message_id, delay=15)

        else:
            try: bot.delete_message(message.chat.id, status_msg.message_id)
            except: pass
            err_msg = bot.send_message(message.chat.id, f"❌ API Error: Server returned {response.status_code}")
            schedule_delete(message.chat.id, err_msg.message_id, delay=15)

    except requests.exceptions.Timeout:
        try: bot.delete_message(message.chat.id, status_msg.message_id)
        except: pass
        err_msg = bot.send_message(message.chat.id, "⚠️ **Timeout:** Server took too long to respond.", parse_mode="Markdown")
        schedule_delete(message.chat.id, err_msg.message_id, delay=15)
    except Exception as e:
        try: bot.delete_message(message.chat.id, status_msg.message_id)
        except: pass
        err_msg = bot.send_message(message.chat.id, f"⚠️ **Error:** `{str(e)}`", parse_mode="Markdown")
        schedule_delete(message.chat.id, err_msg.message_id, delay=15)

# ==========================================
# 🎮 COMMAND HANDLERS
# ==========================================
@bot.message_handler(commands=['aadhaar', 'uid'])
def cmd_aadhaar(m): handle_api(m, API_AADHAAR, "Aadhaar")

@bot.message_handler(commands=['pak'])
def cmd_pak(m): handle_api(m, API_PAK, "Pak")

@bot.message_handler(commands=['vehicle'])
def cmd_vehicle(m): handle_api(m, API_VEHICLE, "Vehicle")

@bot.message_handler(commands=['num'])
def cmd_num(m): handle_api(m, API_NUM, "Number")

@bot.message_handler(commands=['ifsc'])
def cmd_ifsc(m): handle_api(m, API_IFSC, "IFSC")

@bot.message_handler(commands=['bin'])
def cmd_bin(m): handle_api(m, API_BIN, "BIN")

# Admin command to get group ID
@bot.message_handler(commands=['getid'])
def get_group_id(message):
    if message.from_user.id == OWNER_ID:
        bot.reply_to(message, f"The ID of this chat is: `{message.chat.id}`\nType: {message.chat.type}")
    else:
        bot.reply_to(message, "You are not authorized to use this command.")

# ==========================================
# 🔥 MAIN LOOP
# ==========================================
def keep_alive():
    while True:
        time.sleep(200)
        pass

if __name__ == "__main__":
    print(f"🔥 {SYSTEM_NAME} Online & Protected...")
    
    # 🔴 START RENDER WEB SERVER 🔴
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"⚠️ Bot Crashed! Restarting... Error: {e}")
            time.sleep(2)

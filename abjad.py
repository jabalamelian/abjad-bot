import telebot
import requests
import re
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8096262106:AAEkYE_sbdIvjWhtYEGD88zTHlaOtYsKpF4"
bot = telebot.TeleBot(TOKEN)

# دیکشنری حروف ابجد
abjad_dict = {
    "ا": 1, "ب": 2, "ج": 3, "د": 4, "ه": 5, "و": 6, "ز": 7, "ح": 8, "ط": 9,
    "ی": 10, "ک": 20, "ل": 30, "م": 40, "ن": 50, "س": 60, "ع": 70, "ف": 80, "ص": 90,
    "ق": 100, "ر": 200, "ش": 300, "ت": 400, "ث": 500, "خ": 600, "ذ": 700, "ض": 800, "ظ": 900, "غ": 1000
}

# بارگذاری داده‌های ابجد قرآن
with open("quran_abjad.json", "r", encoding="utf-8") as f:
    quran_abjad_data = json.load(f)

# ذخیره وضعیت کاربران
user_data = {}

# دکمه‌های شروع و محاسبه مجدد
def get_start_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📖 وارد کردن شماره سوره", callback_data="enter_surah"))
    return keyboard

def get_retry_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔄 محاسبه مجدد", callback_data="restart"))
    return keyboard

# حذف بسم‌الله (به‌جز سوره ۱)
def remove_bismillah(surah, ayah_text):
    bismillah_variations = [
        "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
        "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ"
    ]
    if surah != "1":
        for bismillah in bismillah_variations:
            if ayah_text.startswith(bismillah):
                return ayah_text[len(bismillah):].strip()
    return ayah_text

# محاسبه ابجد
def calculate_abjad(text):
    text = re.sub(r'[\u064B-\u065F\u06D6-\u06ED\u0640]', '', text)  # حذف علائم عربی
    text = text.replace("ٱ", "ا").replace("ي", "ی").replace("ى", "ی").replace("ك", "ک")
    text = text.strip()
    return sum(abjad_dict.get(char, 0) for char in text if char in abjad_dict)

# یافتن آیات با مقدار ابجد مشابه
def find_matching_verses(target_abjad):
    matches = [v for v in quran_abjad_data if v["abjad"] == target_abjad]
    return matches[:5]

# شروع ربات
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_data[message.chat.id] = {"surah": None, "ayah": None}
    bot.send_message(message.chat.id, "👋 لطفاً شماره سوره را وارد کنید:", reply_markup=get_start_keyboard())

# دریافت شماره سوره
@bot.callback_query_handler(func=lambda call: call.data == "enter_surah")
def ask_for_surah(call):
    bot.send_message(call.message.chat.id, "🔢 لطفاً شماره سوره را وارد کنید:")
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, get_surah)

def get_surah(message):
    user_data[message.chat.id]["surah"] = message.text
    bot.send_message(message.chat.id, "📖 لطفاً شماره آیه را وارد کنید:")
    bot.register_next_step_handler_by_chat_id(message.chat.id, get_ayah)

# دریافت شماره آیه
def get_ayah(message):
    user_data[message.chat.id]["ayah"] = message.text
    surah = user_data[message.chat.id]["surah"]
    ayah = user_data[message.chat.id]["ayah"]
    
    # درخواست به API
    url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/quran-uthmani"
    response = requests.get(url)
    data = response.json()

    if data["status"] == "OK":
        ayah_text = data["data"]["text"]
        ayah_text = remove_bismillah(surah, ayah_text)
        abjad_value = calculate_abjad(ayah_text)

        # پیدا کردن آیات هم‌ابجد
        matches = find_matching_verses(abjad_value)
        match_texts = "\n".join([f"📖 **{m['surah']}:{m['ayah']}** → {m['text']}" for m in matches])
        response_text = f"📖 **آیه:**\n{ayah_text}\n\n🔢 **مقدار ابجد:** {abjad_value}\n\n🔎 **آیات هم‌ابجد:**\n{match_texts}"

        bot.send_message(message.chat.id, response_text, reply_markup=get_retry_keyboard())
    else:
        bot.send_message(message.chat.id, "❌ سوره یا آیه‌ای با این شماره یافت نشد.", reply_markup=get_retry_keyboard())

# دکمه محاسبه مجدد
@bot.callback_query_handler(func=lambda call: call.data == "restart")
def restart_query(call):
    bot.send_message(call.message.chat.id, "🔄 لطفاً شماره سوره جدید را وارد کنید:")
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, get_surah)

bot.polling()

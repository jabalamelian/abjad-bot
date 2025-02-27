import telebot
import requests
import re
import json
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8096262106:AAEkYE_sbdIvjWhtYEGD88zTHlaOtYsKpF4"
bot = telebot.TeleBot(TOKEN)

user_data = {}

with open("quran_abjad.json", "r", encoding="utf-8") as f:
    quran_abjad_data = json.load(f)

abjad_dict = {
    "ا": 1, "ب": 2, "ج": 3, "د": 4, "ه": 5, "و": 6, "ز": 7, "ح": 8, "ط": 9,
    "ی": 10, "ک": 20, "ل": 30, "م": 40, "ن": 50, "س": 60, "ع": 70, "ف": 80, "ص": 90,
    "ق": 100, "ر": 200, "ش": 300, "ت": 400, "ث": 500, "خ": 600, "ذ": 700, "ض": 800, "ظ": 900, "غ": 1000
}

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

def calculate_abjad(text):
    text = re.sub(r'[\u064B-\u065F\u06D6-\u06ED\u0640]', '', text)
    text = text.replace("ٱ", "ا").replace("ي", "ی").replace("ى", "ی").replace("ك", "ک")
    text = text.strip()
    return sum(abjad_dict.get(char, 0) for char in text if char in abjad_dict)

def find_matching_verses(target_abjad):
    matches = [v for v in quran_abjad_data if v["abjad"] == target_abjad]
    return matches[:5]

def restart_button():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🔄 شروع مجدد"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_data[message.chat.id] = {}
    
    bot.send_message(
        message.chat.id, 
        "🤖 **ربات محاسبه ابجد آیات قرآن**\n"
        "این ربات مقدار ابجد آیات قرآن را محاسبه کرده و آیات هم‌ابجد را نمایش می‌دهد.\n\n"
        "📖 لطفاً **شماره سوره** را وارد کنید:"
    )

@bot.message_handler(func=lambda message: message.text == "🔄 شروع مجدد")
def restart_process(message):
    send_welcome(message)

@bot.message_handler(func=lambda message: message.chat.id in user_data and "surah" not in user_data[message.chat.id])
def get_surah(message):
    user_data[message.chat.id]["surah"] = message.text
    bot.send_message(message.chat.id, "📖 لطفاً **شماره آیه** را وارد کنید:")

@bot.message_handler(func=lambda message: message.chat.id in user_data and "ayah" not in user_data[message.chat.id])
def get_ayah(message):
    user_data[message.chat.id]["ayah"] = message.text
    surah = user_data[message.chat.id]["surah"]
    ayah = user_data[message.chat.id]["ayah"]

    url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/quran-uthmani"
    response = requests.get(url)
    data = response.json()

    if data["status"] == "OK":
        ayah_text = data["data"]["text"]
        ayah_text = remove_bismillah(surah, ayah_text)
        abjad_value = calculate_abjad(ayah_text)

        matches = find_matching_verses(abjad_value)

        match_texts = "\n".join([
            f"📖 **{m['ayah']}** | 🏷 **سوره {m['surah']}**\n{m['text']}" for m in matches
        ])

        response_text = (
            f"📖 **سوره:** {surah}\n"
            f"📖 **آیه:** {ayah}\n"
            f"📖 **متن آیه:**\n{ayah_text}\n\n"
            f"🔢 **مقدار ابجد:** {abjad_value}\n\n"
            "🔎 **آیات هم‌ابجد:**\n" + (match_texts if match_texts else "❌ موردی یافت نشد.")
        )

        bot.send_message(message.chat.id, response_text, reply_markup=restart_button())
    else:
        bot.send_message(message.chat.id, "❌ سوره یا آیه‌ای با این شماره یافت نشد.")

bot.polling()

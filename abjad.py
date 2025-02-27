import telebot
import requests
import re
import json

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

# تابع حذف بسم‌الله (به‌جز در سوره ۱)
def remove_bismillah(surah, ayah_text):
    bismillah_variations = [
        "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
        "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ"
    ]
    if surah != "1":  # اگر سوره ۱ نباشد
        for bismillah in bismillah_variations:
            if ayah_text.startswith(bismillah):
                return ayah_text[len(bismillah):].strip()
    return ayah_text

# تابع محاسبه ابجد
def calculate_abjad(text):
    text = re.sub(r'[\u064B-\u065F\u06D6-\u06ED\u0640]', '', text)  # حذف علائم عربی
    text = text.replace("ٱ", "ا").replace("ي", "ی").replace("ى", "ی").replace("ك", "ک")
    text = text.strip()
    return sum(abjad_dict.get(char, 0) for char in text if char in abjad_dict)

# تابع یافتن آیات با مقدار ابجد مشابه
def find_matching_verses(target_abjad):
    matches = [v for v in quran_abjad_data if v["abjad"] == target_abjad]
    return matches[:5]  # فقط ۵ مورد اول را برگرداند

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 لطفاً شماره سوره و شماره آیه را وارد کنید، مانند:\n**2 255**")

@bot.message_handler(func=lambda message: True)
def get_quran_verse(message):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "❗ لطفاً شماره سوره و شماره آیه را صحیح وارد کنید. مثال: **2 255**")
            return
        
        surah, verse = parts
        url = f"https://api.alquran.cloud/v1/ayah/{surah}:{verse}/quran-uthmani"
        response = requests.get(url)
        data = response.json()

        if data["status"] == "OK":
            ayah_text = data["data"]["text"]
            ayah_text = remove_bismillah(surah, ayah_text)  # حذف بسم‌الله اگر لازم باشد
            abjad_value = calculate_abjad(ayah_text)

            # پیدا کردن آیات هم‌ابجد
            matches = find_matching_verses(abjad_value)

            match_texts = "\n".join([f"📖 **{m['surah']}:{m['ayah']}** → {m['text']}" for m in matches])
            response_text = f"📖 **آیه:**\n{ayah_text}\n\n🔢 **مقدار ابجد:** {abjad_value}\n\n🔎 **آیات هم‌ابجد:**\n{match_texts}"

            bot.reply_to(message, response_text)
        else:
            bot.reply_to(message, "❌ سوره یا آیه‌ای با این شماره یافت نشد.")
    except Exception as e:
        bot.reply_to(message, "❌ خطایی رخ داده است. لطفاً دوباره امتحان کنید.")

bot.polling()

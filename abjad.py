import telebot
import requests
import re

TOKEN = "8096262106:AAEkYE_sbdIvjWhtYEGD88zTHlaOtYsKpF4"
bot = telebot.TeleBot(TOKEN)

# دیکشنری ابجد
abjad_dict = {
    "ا": 1, "ب": 2, "ج": 3, "د": 4, "ه": 5, "و": 6, "ز": 7, "ح": 8, "ط": 9,
    "ی": 10, "ک": 20, "ل": 30, "م": 40, "ن": 50, "س": 60, "ع": 70, "ف": 80, "ص": 90,
    "ق": 100, "ر": 200, "ش": 300, "ت": 400, "ث": 500, "خ": 600, "ذ": 700, "ض": 800, "ظ": 900, "غ": 1000
}

# تابع حذف علائم و پاکسازی متن
def clean_text_for_abjad(text):
    text = text.replace("ي", "ی").replace("ك", "ک")  # تبدیل عربی به فارسی
    text = re.sub(r"[^اآبپتثجچحخدذرزسشصضطظعغفقکگلمنوهی]", "", text)  # حذف علائم و اعداد
    return text

# تابع محاسبه ابجد
def calculate_abjad(text):
    text = clean_text_for_abjad(text)
    return sum(abjad_dict.get(char, 0) for char in text)

# دستور شروع
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! شماره سوره و آیه موردنظر را به این شکل ارسال کنید:\n\nمثال: 1 1")

# پردازش شماره سوره و آیه
@bot.message_handler(func=lambda message: True)
def get_quran_verse(message):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "❌ لطفاً شماره سوره و شماره آیه را درست وارد کنید. مثال: 1 1")
            return
        
        surah, verse = parts
        url = f"https://api.alquran.cloud/v1/ayah/{surah}:{verse}/ar"
        response = requests.get(url)
        data = response.json()

        if data["status"] == "OK":
            ayah_text = data["data"]["text"]
            abjad_value = calculate_abjad(ayah_text)
            bot.reply_to(message, f"📖 آیه: {ayah_text}\n🔢 مقدار ابجد: {abjad_value}")
        else:
            bot.reply_to(message, "❌ سوره یا آیه‌ای با این شماره یافت نشد.")
    except Exception as e:
        bot.reply_to(message, "❌ خطایی رخ داده است. لطفاً دوباره امتحان کنید.")

bot.polling()

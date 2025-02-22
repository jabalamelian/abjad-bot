import telebot
import requests
import re

# 🔹 توکن ربات خودت را اینجا قرار بده
TOKEN = "8096262106:AAEkYE_sbdIvjWhtYEGD88zTHlaOtYsKpF4"
bot = telebot.TeleBot(TOKEN)

# 🔹 جدول ارزش ابجدی حروف عربی
abjad_dict = {
    "ا": 1, "ب": 2, "ج": 3, "د": 4, "ه": 5, "و": 6, "ز": 7, "ح": 8, "ط": 9,
    "ی": 10, "ک": 20, "ل": 30, "م": 40, "ن": 50, "س": 60, "ع": 70, "ف": 80, "ص": 90,
    "ق": 100, "ر": 200, "ش": 300, "ت": 400, "ث": 500, "خ": 600, "ذ": 700, "ض": 800, "ظ": 900, "غ": 1000
}

# 🔹 تابع محاسبه ابجد (حذف علائم اضافی)
def calculate_abjad(text):
    clean_text = re.sub(r"[^\u0600-\u06FF]", "", text)  # فقط حروف عربی را نگه‌دار
    return sum(abjad_dict.get(char, 0) for char in clean_text)

# 🔹 پیام خوش‌آمدگویی
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! شماره سوره و آیه موردنظر را به این شکل ارسال کنید: \n\n📌 مثال: `2 255`", parse_mode="Markdown")

# 🔹 دریافت شماره سوره و آیه از کاربر
@bot.message_handler(func=lambda message: True)
def get_quran_verse(message):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "❌ لطفاً شماره سوره و شماره آیه را درست وارد کنید. مثال: `2 255`", parse_mode="Markdown")
            return
        
        surah, verse = parts
        url = f"https://api.alquran.cloud/v1/ayah/{surah}:{verse}"
        response = requests.get(url)
        data = response.json()

        if data["status"] == "OK":
            ayah_text = data["data"]["text"]  # متن عربی آیه
            abjad_value = calculate_abjad(ayah_text)
            bot.reply_to(message, f"📖 آیه: {ayah_text}\n🔢 مقدار ابجد: {abjad_value}")
        else:
            bot.reply_to(message, "❌ سوره یا آیه‌ای با این شماره یافت نشد.")
    except Exception as e:
        bot.reply_to(message, "❌ خطایی رخ داده است. لطفاً دوباره امتحان کنید.")

# 🔹 اجرای ربات
bot.polling()

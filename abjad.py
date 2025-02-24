import telebot
import requests
import re

TOKEN = "8096262106:AAEkYE_sbdIvjWhtYEGD88zTHlaOtYsKpF4"
bot = telebot.TeleBot(TOKEN)

# دیکشنری حروف ابجد
abjad_dict = {
    "ا": 1, "ب": 2, "ج": 3, "د": 4, "ه": 5, "و": 6, "ز": 7, "ح": 8, "ط": 9,
    "ی": 10, "ک": 20, "ل": 30, "م": 40, "ن": 50, "س": 60, "ع": 70, "ف": 80, "ص": 90,
    "ق": 100, "ر": 200, "ش": 300, "ت": 400, "ث": 500, "خ": 600, "ذ": 700, "ض": 800, "ظ": 900, "غ": 1000
}

# تابع حذف علائم و محاسبه ابجد
def calculate_abjad(text):
    # حذف تمام علائم عربی (تنوین، فتحه، کسره، کشیدگی، و غیره)
    text = re.sub(r'[\u064B-\u065F\u06D6-\u06ED\u0640]', '', text)  

    # جایگزینی الف کوچک (ٱ) با الف معمولی (ا)
    text = text.replace("ٱ", "ا")

    # جایگزینی انواع مختلف "ی" و "ک" برای هماهنگی
    text = text.replace("ي", "ی").replace("ى", "ی")  # تبدیل "ي" و "ى" عربی به "ی" فارسی
    text = text.replace("ك", "ک")  # تبدیل "ك" عربی به "ک" فارسی

    # حذف فضاهای اضافی و نامرئی
    text = text.strip()

    # چاپ کدهای یونیکد متن پردازش‌شده برای بررسی مشکل
    unicode_values = [ord(char) for char in text]
    print(f"متن پس از پردازش: {text}")
    print(f"کدهای یونیکد متن: {unicode_values}")

    # محاسبه مقدار ابجد
    return sum(abjad_dict.get(char, 0) for char in text if char in abjad_dict)

# تابع حذف بسم‌الله در سوره‌های غیر از سوره ۱
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

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 سلام! لطفاً شماره سوره و شماره آیه را به این شکل وارد کنید:\n\n📌 مثال: **1 1** (برای دریافت آیه اول سوره فاتحه)")

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
            bot.reply_to(message, f"📖 **آیه:**\n{ayah_text}\n\n🔢 **مقدار ابجد:** {abjad_value}")
        else:
            bot.reply_to(message, "❌ سوره یا آیه‌ای با این شماره یافت نشد.")
    except Exception as e:
        bot.reply_to(message, "❌ خطایی رخ داده است. لطفاً دوباره امتحان کنید.")

bot.polling()

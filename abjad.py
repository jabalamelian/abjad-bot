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
    text = text.replace("أ", "ا").replace("إ", "ا")  # تبدیل الف‌های همزه‌دار به ا
    text = text.replace("ء", "")  # حذف همزه منفصل
    text = text.strip()
    return sum(abjad_dict.get(char, 0) for char in text if char in abjad_dict)

# تابع یافتن آیات با مقدار ابجد مشابه
def find_matching_verses(target_abjad):
    matches = [v for v in quran_abjad_data if v["abjad"] == target_abjad]
    return matches[:5]  # فقط ۵ مورد اول را برگرداند

# تابع ارسال منوی اصلی
def send_main_menu(chat_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔢 ابجد کلمه", "📖 ابجد کبیر آیه")
    bot.send_message(chat_id, "🤖 **ربات محاسبه ابجد**\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=markup)

# تابع شروع ربات
@bot.message_handler(commands=['start'])
def send_welcome(message):
    send_main_menu(message.chat.id)

# مدیریت انتخاب کاربر از منوی اصلی
@bot.message_handler(func=lambda message: message.text in ["🔢 ابجد کلمه", "📖 ابجد کبیر آیه"])
def menu_selection(message):
    if message.text == "🔢 ابجد کلمه":
        bot.send_message(message.chat.id, "✍ لطفاً کلمه مورد نظر را وارد کنید:")
        bot.register_next_step_handler(message, calculate_word_abjad)
    elif message.text == "📖 ابجد کبیر آیه":
        bot.send_message(message.chat.id, "📌 لطفاً شماره سوره را وارد کنید:")
        bot.register_next_step_handler(message, get_surah_number)

# دریافت شماره سوره
def get_surah_number(message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "❌ شماره سوره معتبر نیست. لطفاً فقط عدد وارد کنید.")
        return
    
    surah = message.text
    bot.send_message(message.chat.id, "📌 لطفاً شماره آیه را وارد کنید:")
    bot.register_next_step_handler(message, lambda m: get_ayah_number(m, surah))

# دریافت شماره آیه و نمایش نتیجه
def get_ayah_number(message, surah):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "❌ شماره آیه معتبر نیست. لطفاً فقط عدد وارد کنید.")
        return
    
    verse = message.text
    url = f"https://api.alquran.cloud/v1/ayah/{surah}:{verse}/quran-uthmani"
    response = requests.get(url)
    data = response.json()

    if data["status"] == "OK":
        ayah_text = data["data"]["text"]
        ayah_text = remove_bismillah(surah, ayah_text)  # حذف بسم‌الله اگر لازم باشد
        abjad_value = calculate_abjad(ayah_text)

        # پیدا کردن آیات هم‌ابجد
        matches = find_matching_verses(abjad_value)

        # ساخت متن خروجی
        response_text = f"📖 محاسبه ابجد آیه\n"
        response_text += f"📌 سوره: {surah}\n"
        response_text += f"📌 آیه: {verse}\n"
        response_text += f"📜 متن آیه:\n{ayah_text}\n\n"
        response_text += f"🔢 مقدار ابجد: {abjad_value}\n\n"

        if matches:
            response_text += "🔍 آیات با ابجد مشابه:\n"
            for m in matches:
                response_text += f"📌 سوره: {m['surah']} | آیه: {m['ayah']}\n📜 {m['text']}\n\n"

        bot.send_message(message.chat.id, response_text, reply_markup=get_repeat_button())
    
    else:
        bot.send_message(message.chat.id, "❌ سوره یا آیه‌ای با این شماره یافت نشد.")

# تابع محاسبه ابجد یک کلمه
def calculate_word_abjad(message):
    word = message.text.strip()
    if not word:
        bot.send_message(message.chat.id, "❌ لطفاً یک کلمه معتبر وارد کنید.")
        return
    
    abjad_value = calculate_abjad(word)
    response_text = f"🔢 **محاسبه ابجد کلمه**\n"
    response_text += f"📜 کلمه: {word}\n"
    response_text += f"🔢 مقدار ابجد: {abjad_value}"
    
    bot.send_message(message.chat.id, response_text, reply_markup=get_repeat_button())

# دکمه تکرار
def get_repeat_button():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔄 شروع مجدد")
    return markup

# مدیریت دکمه تکرار
@bot.message_handler(func=lambda message: message.text == "🔄 تکرار")
def restart_bot(message):
    send_main_menu(message.chat.id)

bot.polling()

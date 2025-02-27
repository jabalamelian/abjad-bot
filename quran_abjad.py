import telebot
import requests
import json
import re
import os

# توکن و چت آیدی
TOKEN = "8096262106:AAEkYE_sbdIvjWhtYEGD88zTHlaOtYsKpF4"
CHAT_ID = "103589355"
bot = telebot.TeleBot(TOKEN)

# دیکشنری حروف ابجد
abjad_dict = {
    "ا": 1, "ب": 2, "ج": 3, "د": 4, "ه": 5, "و": 6, "ز": 7, "ح": 8, "ط": 9,
    "ی": 10, "ک": 20, "ل": 30, "م": 40, "ن": 50, "س": 60, "ع": 70, "ف": 80, "ص": 90,
    "ق": 100, "ر": 200, "ش": 300, "ت": 400, "ث": 500, "خ": 600, "ذ": 700, "ض": 800, "ظ": 900, "غ": 1000
}

# تابع محاسبه ابجد با در نظر گرفتن تبدیل همزه‌دارها
def calculate_abjad(text):
    text = re.sub(r'[\u064B-\u065F\u06D6-\u06ED\u0640]', '', text)  # حذف علائم عربی
    text = text.replace("ٱ", "ا").replace("ي", "ی").replace("ى", "ی").replace("ك", "ک")
    text = text.replace("أ", "ا").replace("إ", "ا")  # تبدیل الف‌های همزه‌دار به ا
    text = text.replace("ء", "")  # حذف همزه منفصل
    text = text.strip()
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

# بررسی اینکه آیا فایل قبلاً ارسال شده است یا نه
if os.path.exists("quran_abjad.json") and os.path.exists("sent.lock"):
    print("⏳ فایل قبلاً ارسال شده است. برنامه متوقف شد.")
else:
    # دریافت کل قرآن از API و محاسبه ابجد
    def fetch_quran():
        quran_abjad = []
        for surah in range(1, 115):  # 114 سوره داریم
            response = requests.get(f"https://api.alquran.cloud/v1/surah/{surah}/quran-uthmani")
            data = response.json()
            if data["status"] == "OK":
                for ayah in data["data"]["ayahs"]:
                    text = remove_bismillah(str(surah), ayah["text"])  # حذف بسم‌الله اگر لازم باشد
                    abjad_value = calculate_abjad(text)
                    quran_abjad.append({
                        "surah": surah,
                        "ayah": ayah["numberInSurah"],
                        "text": text,
                        "abjad": abjad_value
                    })
        return quran_abjad

    quran_abjad_data = fetch_quran()

    with open("quran_abjad.json", "w", encoding="utf-8") as f:
        json.dump(quran_abjad_data, f, ensure_ascii=False, indent=4)

    print("✅ محاسبه ابجد آیات کامل شد! اطلاعات در quran_abjad.json ذخیره شد.")

    # ارسال فایل به تلگرام
    with open("quran_abjad.json", "rb") as f:
        bot.send_document(CHAT_ID, f, caption="📂 فایل quran_abjad.json آماده است! لطفاً دانلود و در گیت‌هاب آپلود کن.")

    print("✅ فایل به تلگرام ارسال شد!")

    # ساخت فایل قفل برای جلوگیری از ارسال دوباره
    with open("sent.lock", "w") as lock:
        lock.write("done")

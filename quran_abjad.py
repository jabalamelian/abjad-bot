import telebot
import requests
import json
import re

# توکن ربات تلگرام و شناسه‌ی چت
TOKEN = "8096262106:AAEkYE_sbdIvjWhtYEGD88zTHlaOtYsKpF4"
CHAT_ID = "103589355"  # این را با آیدی عددی خودت جایگزین کن
bot = telebot.TeleBot(TOKEN)

# دیکشنری مقادیر ابجد
abjad_dict = {
    "ا": 1, "ب": 2, "ج": 3, "د": 4, "ه": 5, "و": 6, "ز": 7, "ح": 8, "ط": 9,
    "ی": 10, "ک": 20, "ل": 30, "م": 40, "ن": 50, "س": 60, "ع": 70, "ف": 80, "ص": 90,
    "ق": 100, "ر": 200, "ش": 300, "ت": 400, "ث": 500, "خ": 600, "ذ": 700, "ض": 800, "ظ": 900, "غ": 1000
}

# تابع حذف علائم عربی و محاسبه‌ی مقدار ابجد
def calculate_abjad(text):
    text = re.sub(r'[\u064B-\u065F\u06D6-\u06ED\u0640]', '', text)  # حذف علائم عربی
    text = text.replace("ٱ", "ا").replace("ي", "ی").replace("ى", "ی").replace("ك", "ک")  # هماهنگ‌سازی حروف
    text = text.strip()
    return sum(abjad_dict.get(char, 0) for char in text if char in abjad_dict)

# تابع حذف بسم‌الله (در صورتی که اول آیه باشد و سوره‌ی 1 نباشد)
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

# دریافت کل قرآن و محاسبه مقادیر ابجد
def fetch_quran():
    quran_abjad = []
    for surah in range(1, 115):  # 114 سوره داریم
        response = requests.get(f"https://api.alquran.cloud/v1/surah/{surah}/quran-uthmani")
        data = response.json()
        if data["status"] == "OK":
            for ayah in data["data"]["ayahs"]:
                text = remove_bismillah(str(surah), ayah["text"])  # حذف بسم‌الله در صورت نیاز
                abjad_value = calculate_abjad(text)
                quran_abjad.append({
                    "surah": surah,
                    "ayah": ayah["numberInSurah"],
                    "text": text,
                    "abjad": abjad_value
                })
    return quran_abjad

# اجرای دریافت و محاسبه‌ی مقادیر ابجد
quran_abjad_data = fetch_quran()

# ذخیره‌ی اطلاعات در فایل JSON
with open("quran_abjad.json", "w", encoding="utf-8") as f:
    json.dump(quran_abjad_data, f, ensure_ascii=False, indent=4)

print("✅ محاسبه‌ی مقادیر ابجد انجام شد. فایل `quran_abjad.json` ذخیره شد.")

# ارسال فایل به تلگرام
try:
    with open("quran_abjad.json", "rb") as f:
        bot.send_document(CHAT_ID, f, caption="📂 فایل `quran_abjad.json` آماده است! دانلود و در گیت‌هاب آپلود کن.")

    print("✅ فایل `quran_abjad.json` با موفقیت به تلگرام ارسال شد!")
except Exception as e:
    print(f"❌ خطا در ارسال فایل به تلگرام: {e}")

# توقف اجرای برنامه بعد از ارسال فایل
exit()

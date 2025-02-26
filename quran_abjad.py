import requests
import json
import re

# دیکشنری حروف ابجد
abjad_dict = {
    "ا": 1, "ب": 2, "ج": 3, "د": 4, "ه": 5, "و": 6, "ز": 7, "ح": 8, "ط": 9,
    "ی": 10, "ک": 20, "ل": 30, "م": 40, "ن": 50, "س": 60, "ع": 70, "ف": 80, "ص": 90,
    "ق": 100, "ر": 200, "ش": 300, "ت": 400, "ث": 500, "خ": 600, "ذ": 700, "ض": 800, "ظ": 900, "غ": 1000
}

# تابع حذف علائم و محاسبه ابجد
def calculate_abjad(text):
    text = re.sub(r'[\u064B-\u065F\u06D6-\u06ED\u0640]', '', text)  # حذف علائم عربی
    text = text.replace("ٱ", "ا").replace("ي", "ی").replace("ى", "ی").replace("ك", "ک")  # هماهنگ‌سازی حروف
    text = text.strip()  # حذف فضاهای اضافی
    return sum(abjad_dict.get(char, 0) for char in text if char in abjad_dict)

# تابع حذف بسم‌الله در سوره‌های غیر از سوره ۱
def remove_bismillah(surah, ayah_text):
    bismillah_variations = [
        "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
        "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ"
    ]
    if surah != 1:  # اگر سوره اول نیست
        for bismillah in bismillah_variations:
            if ayah_text.startswith(bismillah):
                return ayah_text[len(bismillah):].strip()
    return ayah_text

# دریافت تمام آیات و محاسبه مقدار ابجد
def fetch_quran_verses():
    all_verses = []
    for surah in range(1, 115):  # 114 سوره
        url = f"https://api.alquran.cloud/v1/surah/{surah}/quran-uthmani"
        response = requests.get(url)
        data = response.json()
        
        if data["status"] == "OK":
            for ayah in data["data"]["ayahs"]:
                ayah_text = remove_bismillah(surah, ayah["text"])  # حذف بسم‌الله اگر لازم باشد
                abjad_value = calculate_abjad(ayah_text)
                
                all_verses.append({
                    "surah": surah,
                    "ayah": ayah["numberInSurah"],
                    "text": ayah_text,
                    "abjad": abjad_value
                })
    
    # ذخیره اطلاعات در فایل JSON
    with open("quran_abjad.json", "w", encoding="utf-8") as f:
        json.dump(all_verses, f, ensure_ascii=False, indent=2)
    
    print("✅ دریافت و محاسبه ابجد آیات کامل شد! اطلاعات در quran_abjad.json ذخیره شد.")

# اجرای تابع
fetch_quran_verses()

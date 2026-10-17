# TITAN PRO V80.1.2 — Android APK (NNN)

## علت خطای Actions (فعلاً)

خطا این است:

```
Missing TITAN_PRO_V80_NNN_UNIFIED.py
```

یعنی **فایل موتور (~۲ مگابایت) هنوز در ریشه ریپو نیست.**

## کار لازم (یک‌بار)

1. فایل را از همین چت / سیستم خودتان بردارید:
   - نام دقیق: `TITAN_PRO_V80_NNN_UNIFIED.py`
2. در گیت‌هاب باز کنید:
   https://github.com/ehsanrahmanii-code/TITAN-NNN-V80
3. **Add file → Upload files**
4. فایل را بکشید روی صفحه (باید در **ریشه** ریپو باشد، نه داخل پوشه)
5. **Commit changes**

## ساخت APK

1. بروید: https://github.com/ehsanrahmanii-code/TITAN-NNN-V80/actions
2. **Build Titan NNN V80 APK** → **Run workflow** → **Run workflow**
3. بعد از ۱۵–۴۵ دقیقه، Artifact به نام `Titan-NNN-V80-APK` را دانلود کنید.

## داخل APK

- Python 3.11 + numpy + pandas + flask + requests (همه داخل APK)
- WebView روی `http://127.0.0.1:8080`
- داده فقط در پوشه **NNN**

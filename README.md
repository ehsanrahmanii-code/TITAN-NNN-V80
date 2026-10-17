# TITAN PRO V80.1.2 — Android APK (NNN hard-lock)

اپلیکیشن اندروید **تحلیل‌محور** (بدون اجرای سفارش) با موتور TITAN V80.1.2.

## ویژگی‌ها
- **Chaquopy**: پایتون ۳.۱۱ + `numpy` / `pandas` / `flask` / `requests` و وابستگی‌ها **داخل خود APK**
- **WebView** داشبورد محلی روی `http://127.0.0.1:8080`
- تمام داده/کش/لاگ/دیتابیس فقط داخل پوشه **`NNN`**
- بدون وابستگی نصب جدا روی گوشی

## ساخت APK

### روش ۱ — GitHub Actions (پیشنهادی)
1. این ریپو را در GitHub باز کنید.
2. تب **Actions** → workflow **Build Titan NNN V80 APK** → **Run workflow**.
3. پس از اتمام، Artifact به نام `Titan-NNN-V80-APK` را دانلود کنید.

### روش ۲ — Android Studio روی سیستم خودتان
1. Android Studio (Giraffe یا جدیدتر) + JDK 17
2. Clone ریپو
3. Sync Gradle (Chaquopy pip wheelها را دانلود می‌کند)
4. Run / Build → APK

## نصب روی گوشی
1. APK دیباگ را نصب کنید (منبع ناشناس را فعال کنید).
2. در اولین اجرا مجوز **اعلان** و در صورت امکان **دسترسی فایل‌ها** را بدهید تا پوشه `Internal Storage/NNN` ساخته شود.
3. اگر مجوز All-files نباشد، داده در مسیر خصوصی اپ (`files/NNN`) ذخیره می‌شود.

## ساختار
```
app/src/main/python/
  android_main.py              # bootstrap سرور
  TITAN_PRO_V80_NNN_UNIFIED.py # موتور کامل V80
```

## نکته
- فقط **arm64-v8a** (تقریباً همه گوشی‌های ۲۰۱۹ به بعد)
- اینترنت برای قیمت زنده Binance لازم است؛ کتابخانه‌ها از APK می‌آیند نه از اینترنت روی گوشی.

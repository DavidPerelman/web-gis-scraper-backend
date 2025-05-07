# 🐍 בסיס לפייתון
FROM python:3.10-slim

# 🧰 התקנת תלותיות מערכתיות
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libdrm2 \
    libu2f-udev \
    chromium \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 🧪 העתק קבצי הפרויקט
WORKDIR /app
COPY . .

# 📦 התקנת התלויות
RUN pip install --upgrade pip && pip install -r requirements.txt

# ✅ הגדרת משתני סביבה ל־pyppeteer (לא חובה, אבל מונע בעיות)
ENV PYPPETEER_BROWSER_PATH=/usr/bin/chromium

# 🚀 הפעלת האפליקציה
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

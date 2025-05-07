FROM python:3.11-slim

# התקנת תלויות ש־Pyppeteer/Chromium צריכים
RUN apt-get update && apt-get install -y \
    wget gnupg curl unzip \
    libnss3 libatk-bridge2.0-0 libx11-xcb1 libgtk-3-0 \
    libxcomposite1 libxdamage1 libxrandr2 libasound2 libpangocairo-1.0-0 \
    libxshmfence1 libgbm1 libxfixes3 libxext6 libx11-6 \
    --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# יצירת תיקיית עבודה
WORKDIR /app

# העתקת קבצי הפרויקט
COPY . /app

# התקנת תלויות Python
RUN pip install --no-cache-dir -r requirements.txt

# הורדת Chromium מראש (חשוב כדי למנוע שגיאות בזמן ריצה)
RUN python -c "import pyppeteer; pyppeteer.install()"

# פתיחת הפורט (Railway משתמש ב־env var בשם PORT)
ENV PORT=8000
EXPOSE ${PORT}

# הפקודת הפעלה של uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

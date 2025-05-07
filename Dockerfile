FROM python:3.10-slim

# התקנות בסיסיות
RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl ca-certificates fonts-liberation \
    libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 \
    libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 libnss3 \
    libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 \
    xdg-utils libu2f-udev libvulkan1 libxss1 libgbm1 \
    chromium && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# משתנים לסביבת Chrome
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# התקנת תלויות פייתון
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# קבצי הפרויקט
COPY . /app
WORKDIR /app

# פתיחת פורט
EXPOSE 8000

# הפעלת השרת
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

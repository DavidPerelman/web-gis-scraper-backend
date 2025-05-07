# Dockerfile

FROM python:3.11-slim

# התקנת תלות מערכת + דפדפן Chromium
RUN apt-get update && apt-get install -y \
    chromium \
    libglib2.-0 libnss3 libgconf-2-4 libfontconfig1 libxss1 libappindicator3-1 \
    libasound2 libatk-bridge2.0-0 libgtk-3-0 libx11-xcb1 \
    && apt-get clean

# משתנה סביבה ש-Pyppeteer יזהה את כרום
ENV PYPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# העתקת כל הקוד
WORKDIR /app
COPY . /app

# התקנת ספריות Python
RUN pip install --no-cache-dir -r requirements.txt

# הרצת השרת
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

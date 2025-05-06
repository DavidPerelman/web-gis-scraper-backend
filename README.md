# GIS Scraper App

מערכת אינטרנטית מלאה (Full Stack) לחילוץ וניתוח נתוני תוכניות בניה מתוך פוליגון שסופק על ידי המשתמש.

## 📌 סקירה כללית

המערכת מאפשרת העלאת קובץ פוליגון גיאוגרפי (כגון Shapefile או GeoJSON), ולאחר עיבוד הכולל גרידת נתונים מאתר ממשלתי, מחזירה שכבת מידע חדשה עם הנתונים של התוכניות הכלולות בתחום הפוליגון.

### 🔧 צד שרת (FastAPI)

- מקבל קובץ פוליגון מהמשתמש
- מפרש את הפוליגון באמצעות GeoPandas
- מבצע גרידת נתונים מאתר תכניות ממשלתי
- מחזיר שכבה חדשה להורדה (GeoJSON או טבלה)

### 💻 צד לקוח (Next.js) _(בפיתוח עתידי)_

- טופס להעלאת קבצים
- תצוגת מפה אינטראקטיבית (Leaflet)
- טבלה עם תוצאות + כפתור הורדה

---

## 📁 מבנה הפרויקט

project-root/
├── client/ # צד לקוח (React + Next.js)
├── server/ # צד שרת (FastAPI)
│ ├── app/
│ │ ├── main.py
│ │ └── api/
│ │ └── routes.py
│ └── requirements.txt
├── data/ # קבצי דוגמה זמניים
├── notebooks/ # מחברות Jupyter מקוריות
└── README.md

---

## 🚀 טכנולוגיות

- FastAPI + Python 3.11
- GeoPandas + Shapely
- BeautifulSoup / Selenium לגרידה
- Next.js + React + Leaflet (לצד לקוח)
- Docker (בעתיד)
- GitHub Actions (בעתיד, להרצה אוטומטית)

---

## 🔄 שיטת ניהול גרסאות (Git Workflow)

- `main` – גרסה יציבה
- `dev` – ענף פיתוח ראשי
- `feature/*` או `bugfix/*` – ענפי פיתוח נקודתיים

✅ הודעות Commit יהיו באנגלית  
📝 תיאורי Pull Request יהיו בעברית

---

## 📦 התקנת צד שרת

```bash
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
cd server
uvicorn app.main:app --reload

🌱 תכנון עתידי
 MVP: העלאת קובץ + גרידת נתונים + הורדת GeoJSON

 קבלת מספרי תכניות מתוך טבלה

 הורדת פוליגונים בודדים לכל תכנית

 בחירת שדות רצויים לפלט

```

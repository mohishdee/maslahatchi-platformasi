# Maslahatchi Platformasi

Responsive web-platforma: telefon, planshet va kompyuterda ishlaydi.

## Imkoniyatlar
- Login/parol
- SQLite ma'lumotlar bazasi — ma'lumotlar qayta kirganda saqlanadi
- 1000+ o'quvchi uchun forma
- O'quvchi qidirish
- Tahrirlash/o'chirish
- Ota-ona ma'lumotlari
- PINFL/passport
- Kasbiy qiziqish
- Sertifikat/hujjat fayli yuklash
- Dashboard va sinflar statistikasi

## Ishga tushirish
1. Python 3.10+ o'rnating.
2. Terminalni loyiha papkasida oching.
3. `pip install -r requirements.txt`
4. `python app.py`
5. Brauzerda `http://127.0.0.1:5000` ni oching.

Standart login:
- Username: `admin`
- Password: `admin123`

Internetga chiqarishdan oldin `SECRET_KEY` ni almashtiring va admin parolini o'zgartirish funksiyasini qo'shing.

## Muhim
Hozirgi paket — tayyor ishlaydigan lokal/server loyiha. Turli telefon va kompyuterlardan bir xil ma'lumotlar ko'rinishi uchun uni internetdagi serverga deploy qilish kerak. SQLite kichik/o'rta hajm uchun ishlaydi; ko'p foydalanuvchi bilan ishlab ketganda PostgreSQL ga o'tkazish tavsiya etiladi.

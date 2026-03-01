import requests
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
import pytz

BASE_URL = "http://api.aladhan.com/v1/timingsByCity"

async def prayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jadwal shalat berdasarkan kota"""
    if not context.args:
        await update.message.reply_text(
            "🕌 **Jadwal Shalat**\n\n"
            "Format: `/shalat <nama kota>`\n"
            "Contoh: `/shalat Jakarta`\n"
            "Atau: `/shalat Surabaya`\n\n"
            "*Untuk kota di Indonesia saja*",
            parse_mode='Markdown'
        )
        return
    
    city = " ".join(context.args)
    
    # Ambil tanggal hari ini
    today = datetime.now().strftime("%d-%m-%Y")
    
    params = {
        'city': city,
        'country': 'Indonesia',
        'method': 2,  # Kemenag RI
        'date': today
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if data.get('code') != 200:
            await update.message.reply_text(
                f"❌ Kota '{city}' tidak ditemukan.\n"
                f"Coba dengan nama kota yang benar, contoh: Jakarta, Bandung, Surabaya"
            )
            return
        
        timings = data['data']['timings']
        date = data['data']['date']['readable']
        
        # Format waktu shalat
        prayer_times = {
            'Imsak': timings['Imsak'],
            'Subuh': timings['Fajr'],
            'Terbit': timings['Sunrise'],
            'Dhuha': timings['Sunrise'],  # Dhuha sekitar 20 menit setelah terbit
            'Dzuhur': timings['Dhuhr'],
            'Ashar': timings['Asr'],
            'Maghrib': timings['Maghrib'],
            'Isya': timings['Isha']
        }
        
        # Hitung waktu dhuha (20 menit setelah terbit)
        sunrise = timings['Sunrise']
        hour, minute = map(int, sunrise.split(':'))
        dhuha_minute = minute + 20
        dhuha_hour = hour
        if dhuha_minute >= 60:
            dhuha_hour += 1
            dhuha_minute -= 60
        prayer_times['Dhuha'] = f"{dhuha_hour:02d}:{dhuha_minute:02d}"
        
        # Buat pesan
        prayer_msg = f"🕌 **Jadwal Shalat {city}**\n📅 {date}\n\n"
        
        for prayer, time in prayer_times.items():
            prayer_msg += f"• {prayer}: {time} WIB\n"
        
        # Info tambahan
        hijri = data['data']['date']['hijri']
        prayer_msg += f"\n📆 Hijriah: {hijri['day']} {hijri['month']['en']} {hijri['year']}H"
        
        await update.message.reply_text(prayer_msg, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal mengambil jadwal shalat. Error: {str(e)}")

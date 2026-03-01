import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
import pytz
from database import SessionLocal, UserLocation

BASE_URL = "http://api.aladhan.com/v1/timings"

async def set_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set lokasi user pake koordinat"""
    if len(context.args) < 2:
        await update.message.reply_text(
            "📍 **Set Lokasi Manual**\n\n"
            "Format: `/setlokasi <nama> <lat> <lon>`\n"
            "Contoh: `/setlokasi Rumah -6.9175 107.6191`\n\n"
            "Atau: `/setlokasi Kantor -6.2088 106.8456`",
            parse_mode='Markdown'
        )
        return
    
    city_name = context.args[0]
    try:
        lat = float(context.args[1])
        lon = float(context.args[2])
    except:
        await update.message.reply_text("❌ Format koordinat salah. Contoh: -6.9175 107.6191")
        return
    
    # Simpan ke database
    db = SessionLocal()
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    # Cek apakah user udah ada
    user_loc = db.query(UserLocation).filter_by(user_id=user_id).first()
    
    if user_loc:
        user_loc.city_name = city_name
        user_loc.latitude = lat
        user_loc.longitude = lon
        user_loc.country = "Indonesia"
    else:
        new_loc = UserLocation(
            user_id=user_id,
            username=username,
            city_name=city_name,
            latitude=lat,
            longitude=lon
        )
        db.add(new_loc)
    
    db.commit()
    db.close()
    
    await update.message.reply_text(f"✅ Lokasi '{city_name}' tersimpan!")

async def my_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat lokasi tersimpan (command: /mylokasi)"""  # <-- Update ini
    db = SessionLocal()
    user_id = update.effective_user.id
    user_loc = db.query(UserLocation).filter_by(user_id=user_id).first()
    db.close()
    
    if user_loc:
        await update.message.reply_text(
            f"📍 **Lokasi Tersimpan**\n\n"
            f"Nama: {user_loc.city_name}\n"
            f"Koordinat: {user_loc.latitude}, {user_loc.longitude}\n"
            f"Negara: {user_loc.country}",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ Belum ada lokasi tersimpan. Ketik `/setlokasi` untuk setting."
        )

async def prayer_advanced(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jadwal shalat berdasarkan koordinat user"""
    user_id = update.effective_user.id
    
    # Cek di database dulu
    db = SessionLocal()
    user_loc = db.query(UserLocation).filter_by(user_id=user_id).first()
    db.close()
    
    # Kalo ada lokasi tersimpan, pake itu
    if user_loc:
        lat = user_loc.latitude
        lon = user_loc.longitude
        city_display = user_loc.city_name
    else:
        # Fallback ke input manual
        if not context.args:
            await update.message.reply_text(
                "🕌 **Jadwal Shalat**\n\n"
                "Format: `/shalat <kota>`\n"
                "Atau setting lokasi dulu: `/setlokasi <nama> <lat> <lon>`",
                parse_mode='Markdown'
            )
            return
        
        city_name = " ".join(context.args)
        # Pake geocoding buat dapet koordinat dari nama kota
        geocode_url = f"https://nominatim.openstreetmap.org/search?q={city_name},Indonesia&format=json"
        geo_resp = requests.get(geocode_url, headers={'User-Agent': 'TelegramBot'})
        
        if geo_resp.status_code != 200 or not geo_resp.json():
            await update.message.reply_text("❌ Kota tidak ditemukan.")
            return
        
        loc = geo_resp.json()[0]
        lat = float(loc['lat'])
        lon = float(loc['lon'])
        city_display = loc['display_name'].split(',')[0]
    
    # Hitung tanggal hari ini
    today = datetime.now().strftime("%d-%m-%Y")
    
    params = {
        'latitude': lat,
        'longitude': lon,
        'method': 11,  # Kemenag RI
        'date': today
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if data.get('code') != 200:
            await update.message.reply_text("❌ Gagal ambil jadwal shalat.")
            return
        
        timings = data['data']['timings']
        date = data['data']['date']['readable']
        
        # Format waktu shalat
        prayers = ['Imsak', 'Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
        prayer_names = {'Fajr': 'Subuh', 'Dhuhr': 'Dzuhur', 'Asr': 'Ashar', 'Sunrise': 'Terbit', 'Isha': 'Isya'}
        
        msg = f"🕌 **Jadwal Shalat {city_display}**\n📅 {date}\n\n"
        
        for prayer in prayers:
            if prayer in timings:
                name = prayer_names.get(prayer, prayer)
                time = timings[prayer]
                msg += f"• {name}: {time} WIB\n"
        
        # Info tambahan
        hijri = data['data']['date']['hijri']
        msg += f"\n📆 Hijriah: {hijri['day']} {hijri['month']['en']} {hijri['year']}H"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

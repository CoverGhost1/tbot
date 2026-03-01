import requests
import os
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

API_KEY = os.environ.get("OPENWEATHER_API_KEY", "YOUR_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Info cuaca terkini"""
    if not context.args:
        await update.message.reply_text(
            "☁️ **Info Cuaca**\n\n"
            "Format: `/cuaca <nama kota>`\n"
            "Contoh: `/cuaca Jakarta`\n"
            "Atau: `/cuaca Surabaya`",
            parse_mode='Markdown'
        )
        return
    
    city = " ".join(context.args)
    await update.message.reply_text(f"🔍 Mencari cuaca untuk *{city}*...", parse_mode='Markdown')
    
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric',  # Celsius
        'lang': 'id'        # Bahasa Indonesia
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if response.status_code != 200:
            error_msg = data.get('message', 'Kota tidak ditemukan')
            await update.message.reply_text(f"❌ Error: {error_msg}")
            return
        
        # Ambil data cuaca
        city_name = data['name']
        country = data['sys']['country']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        pressure = data['main']['pressure']
        wind_speed = data['wind']['speed']
        weather_desc = data['weather'][0]['description'].capitalize()
        icon = data['weather'][0]['icon']
        
        # Dapatkan waktu sunrise & sunset
        sunrise = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M')
        sunset = datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')
        
        # Emoji berdasarkan cuaca
        weather_emoji = {
            '01d': '☀️', '01n': '🌙',  # Cerah
            '02d': '⛅', '02n': '☁️',  # Sedikit berawan
            '03d': '☁️', '03n': '☁️',  # Berawan
            '04d': '☁️', '04n': '☁️',  # Berawan tebal
            '09d': '🌧️', '09n': '🌧️', # Hujan gerimis
            '10d': '🌦️', '10n': '🌧️', # Hujan
            '11d': '⛈️', '11n': '⛈️', # Badai petir
            '13d': '❄️', '13n': '❄️', # Salju
            '50d': '🌫️', '50n': '🌫️', # Kabut
        }.get(icon, '🌡️')
        
        weather_msg = (
            f"{weather_emoji} **Cuaca di {city_name}, {country}**\n\n"
            f"🌡 Suhu: {temp}°C (terasa {feels_like}°C)\n"
            f"☁️ Kondisi: {weather_desc}\n"
            f"💧 Kelembaban: {humidity}%\n"
            f"🌬 Angin: {wind_speed} m/s\n"
            f"📊 Tekanan: {pressure} hPa\n\n"
            f"🌅 Sunrise: {sunrise} WIB\n"
            f"🌇 Sunset: {sunset} WIB"
        )
        
        await update.message.reply_text(weather_msg, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal mengambil data cuaca. Error: {str(e)}")

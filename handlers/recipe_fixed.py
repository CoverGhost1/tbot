import os
import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import SessionLocal, RecipeHistory
from datetime import datetime

# ALTERNATIF 1: Edamam API (harus daftar)
EDAMAM_APP_ID = os.environ.get("EDAMAM_APP_ID", "")
EDAMAM_APP_KEY = os.environ.get("EDAMAM_APP_KEY", "")

# ALTERNATIF 2: API Masakan Indonesia (scraping atau custom)
# Pake API publik dari mealdb tapi filter masakan Asia
BASE_URL = "https://www.themealdb.com/api/json/v1/1"

async def search_recipe_indonesia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cari resep dengan filter masakan Asia/Indonesia"""
    if not context.args:
        await update.message.reply_text("🍳 **Cari Resep**\nContoh: `/resep rendang`", parse_mode='Markdown')
        return
    
    keyword = " ".join(context.args)
    await update.message.reply_text(f"🔍 Mencari resep *{keyword}*...", parse_mode='Markdown')
    
    # Simpan ke database history
    db = SessionLocal()
    history = RecipeHistory(
        user_id=update.effective_user.id,
        recipe_name=keyword
    )
    db.add(history)
    db.commit()
    
    # Coba cari di TheMealDB
    url = f"{BASE_URL}/search.php?s={keyword}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        meals = data.get("meals", [])
        
        # Filter masakan Asia aja
        asian_countries = ['Indonesian', 'Malaysian', 'Thai', 'Japanese', 'Chinese', 'Korean', 'Indian', 'Vietnamese', 'Filipino']
        asian_meals = [
            meal for meal in meals 
            if meal.get('strArea') in asian_countries
        ] if meals else []
        
        if asian_meals:
            keyboard = []
            for meal in asian_meals[:5]:
                keyboard.append([InlineKeyboardButton(
                    f"{meal['strMeal']} ({meal['strArea']})", 
                    callback_data=f"recipe_{meal['idMeal']}"
                )])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"Ditemukan {len(asian_meals)} resep Asia:",
                reply_markup=reply_markup
            )
            return
    
    # Kalo ga ketemu, kasih alternatif
    await update.message.reply_text(
        f"❌ Resep '{keyword}' tidak ditemukan.\n\n"
        f"**Tips:** Coba keyword lain atau masakan umum:\n"
        f"• rendang\n• nasi goreng\n• sate\n• gulai\n• opor"
    )

async def recipe_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk detail resep"""
    query = update.callback_query
    await query.answer()
    
    meal_id = query.data.replace("recipe_", "")
    
    url = f"{BASE_URL}/lookup.php?i={meal_id}"
    response = requests.get(url)
    
    if response.status_code != 200:
        await query.edit_message_text("❌ Gagal ambil detail resep.")
        return
    
    meal = response.json()['meals'][0]
    
    # Ambil bahan-bahan
    ingredients = []
    for i in range(1, 21):
        ing = meal.get(f"strIngredient{i}")
        measure = meal.get(f"strMeasure{i}")
        if ing and ing.strip() and ing != " ":
            ingredients.append(f"• {measure} {ing}".strip())
    
    ingredients_text = "\n".join(ingredients[:10])
    
    # Ambil instruksi (potong kalo kepanjangan)
    instructions = meal['strInstructions']
    if len(instructions) > 1000:
        instructions = instructions[:1000] + "...\n\n[Lanjutan di sumber asli]"
    
    # Buat pesan
    msg = (
        f"🍽 **{meal['strMeal']}**\n"
        f"🌍 Asal: {meal['strArea']}\n"
        f"🍴 Kategori: {meal['strCategory']}\n\n"
        f"**Bahan-bahan:**\n{ingredients_text}\n\n"
        f"**Cara Masak:**\n{instructions}\n"
    )
    
    if meal.get('strYoutube'):
        msg += f"\n📺 [Tonton Video]({meal['strYoutube']})"
    
    await query.edit_message_text(msg, parse_mode='Markdown', disable_web_page_preview=True)

import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from urllib.parse import quote

# Pake API gratis dari TheMealDB
BASE_URL = "https://www.themealdb.com/api/json/v1/1"

async def search_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cari resep berdasarkan keyword"""
    if not context.args:
        await update.message.reply_text(
            "🍳 **Cari Resep Masakan**\n\n"
            "Contoh: `/resep nasi goreng`\n"
            "Atau: `/resep ayam`",
            parse_mode='Markdown'
        )
        return
    
    keyword = " ".join(context.args)
    await update.message.reply_text(f"🔍 Mencari resep untuk: *{keyword}*...", parse_mode='Markdown')
    
    # Cari resep
    url = f"{BASE_URL}/search.php?s={quote(keyword)}"
    response = requests.get(url)
    
    if response.status_code != 200:
        await update.message.reply_text("❌ Gagal mengambil data resep. Coba lagi nanti.")
        return
    
    data = response.json()
    meals = data.get("meals", [])
    
    if not meals:
        await update.message.reply_text(f"❌ Resep untuk '{keyword}' tidak ditemukan.")
        return
    
    # Tampilkan 5 resep pertama
    keyboard = []
    for meal in meals[:5]:
        keyboard.append([InlineKeyboardButton(
            meal['strMeal'], 
            callback_data=f"recipe_{meal['idMeal']}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Ditemukan {len(meals)} resep. Pilih yang mau dilihat:",
        reply_markup=reply_markup
    )

async def recipe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk callback dari inline button resep"""
    query = update.callback_query
    await query.answer()
    
    meal_id = query.data.replace("recipe_", "")
    
    # Ambil detail resep
    url = f"{BASE_URL}/lookup.php?i={meal_id}"
    response = requests.get(url)
    
    if response.status_code != 200:
        await query.edit_message_text("❌ Gagal mengambil detail resep.")
        return
    
    data = response.json()
    meal = data['meals'][0]
    
    # Format bahan-bahan
    ingredients = []
    for i in range(1, 21):
        ingredient = meal.get(f"strIngredient{i}")
        measure = meal.get(f"strMeasure{i}")
        if ingredient and ingredient.strip():
            ingredients.append(f"• {measure} {ingredient}".strip())
    
    ingredients_text = "\n".join(ingredients[:10])  # Max 10 bahan
    
    # Format instruksi
    instructions = meal['strInstructions'][:500] + "..." if len(meal['strInstructions']) > 500 else meal['strInstructions']
    
    # Pesan lengkap
    recipe_msg = (
        f"🍽 **{meal['strMeal']}**\n"
        f"🌍 Asal: {meal['strArea']}\n"
        f"🍴 Kategori: {meal['strCategory']}\n\n"
        f"**Bahan-bahan:**\n{ingredients_text}\n\n"
        f"**Cara masak:**\n{instructions}\n"
    )
    
    if meal.get('strYoutube'):
        recipe_msg += f"\n📺 Video: {meal['strYoutube']}"
    
    if meal.get('strSource'):
        recipe_msg += f"\n📝 Sumber: {meal['strSource']}"
    
    await query.edit_message_text(recipe_msg, parse_mode='Markdown', disable_web_page_preview=True)

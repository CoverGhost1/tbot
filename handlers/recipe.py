import os
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import SessionLocal, RecipeHistory

BASE_URL = "https://www.themealdb.com/api/json/v1/1"

# ==============================
# 🔍 SEARCH RECIPE
# ==============================

async def search_recipe_indonesia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "🍳 *Cari Resep*\nContoh: `/resep rendang`",
            parse_mode="Markdown"
        )
        return

    keyword = " ".join(context.args)
    await update.message.reply_text(
        f"🔍 Mencari resep *{keyword}*...",
        parse_mode="Markdown"
    )

    # Simpan history (aman)
    try:
        db = SessionLocal()
        history = RecipeHistory(
            user_id=update.effective_user.id,
            recipe_name=keyword
        )
        db.add(history)
        db.commit()
        db.close()
    except Exception as e:
        print("DB Error:", e)

    url = f"{BASE_URL}/search.php?s={keyword}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    await update.message.reply_text("❌ Gagal ambil data dari server.")
                    return
                data = await response.json()
    except Exception as e:
        await update.message.reply_text("❌ Terjadi kesalahan koneksi.")
        print("HTTP Error:", e)
        return

    meals = data.get("meals")

    if not meals:
        await update.message.reply_text(
            f"❌ Resep *{keyword}* tidak ditemukan.",
            parse_mode="Markdown"
        )
        return

    # Filter Asia
    asian_countries = [
        "Indonesian", "Malaysian", "Thai",
        "Japanese", "Chinese", "Korean",
        "Indian", "Vietnamese", "Filipino"
    ]

    asian_meals = [
        meal for meal in meals
        if meal.get("strArea") in asian_countries
    ]

    if not asian_meals:
        await update.message.reply_text(
            "❌ Ditemukan resep tapi bukan kategori Asia."
        )
        return

    keyboard = []
    for meal in asian_meals[:5]:
        keyboard.append([
            InlineKeyboardButton(
                f"{meal['strMeal']} ({meal['strArea']})",
                callback_data=f"recipe_{meal['idMeal']}"
            )
        ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🍽 Ditemukan {len(asian_meals)} resep:",
        reply_markup=reply_markup
    )


# ==============================
# 📖 DETAIL RECIPE CALLBACK
# ==============================

async def recipe_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    meal_id = query.data.replace("recipe_", "")
    url = f"{BASE_URL}/lookup.php?i={meal_id}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    await query.edit_message_text("❌ Gagal ambil detail resep.")
                    return
                data = await response.json()
    except Exception as e:
        await query.edit_message_text("❌ Terjadi kesalahan koneksi.")
        print("HTTP Error:", e)
        return

    meals = data.get("meals")
    if not meals:
        await query.edit_message_text("❌ Detail resep tidak ditemukan.")
        return

    meal = meals[0]

    # Ambil bahan
    ingredients = []
    for i in range(1, 21):
        ing = meal.get(f"strIngredient{i}")
        measure = meal.get(f"strMeasure{i}")

        if ing and ing.strip():
            text = f"• {measure.strip() if measure else ''} {ing.strip()}"
            ingredients.append(text.strip())

    ingredients_text = "\n".join(ingredients[:10])

    instructions = meal.get("strInstructions", "")
    if len(instructions) > 900:
        instructions = instructions[:900] + "...\n\n[Lanjutan di sumber asli]"

    msg = (
        f"🍽 *{meal['strMeal']}*\n"
        f"🌍 Asal: {meal['strArea']}\n"
        f"🍴 Kategori: {meal['strCategory']}\n\n"
        f"*Bahan-bahan:*\n{ingredients_text}\n\n"
        f"*Cara Masak:*\n{instructions}"
    )

    # Tambah link youtube (FIXED)
    if meal.get("strYoutube"):
        msg += f"\n\n📺 [Tonton Video]({meal['strYoutube']})"

    await query.edit_message_text(
        msg,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

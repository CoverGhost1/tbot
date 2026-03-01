import re
import math
from telegram import Update
from telegram.ext import ContextTypes

async def calculator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Informasi cara pakai kalkulator"""
    msg = (
        "🔢 **Kalkulator Sederhana**\n\n"
        "Tinggal ketik langsung operasi matematikanya!\n\n"
        "Contoh:\n"
        "• `2 + 2` = 4\n"
        "• `10 * 5 + 3` = 53\n"
        "• `(8 + 2) * 3` = 30\n"
        "• `2^3` = 8 (pangkat)\n"
        "• `sqrt(16)` = 4 (akar)\n\n"
        "Fitur: +, -, *, /, ^, sqrt(), ()"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

async def handle_calculation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Proses perhitungan matematika"""
    expression = update.message.text.strip()
    
    # Bersihin spasi berlebih
    expression = re.sub(r'\s+', '', expression)
    
    # Ganti ^ dengan ** untuk pangkat
    expression = expression.replace('^', '**')
    
    # Handle sqrt()
    expression = re.sub(r'sqrt\(([^)]+)\)', r'math.sqrt(\1)', expression)
    
    try:
        # Evaluasi expression dengan aman
        # Cuma izinin angka, operator, dan fungsi math tertentu
        allowed_names = {
            k: v for k, v in math.__dict__.items() 
            if not k.startswith("__")
        }
        allowed_names.update({"abs": abs, "round": round})
        
        # Evaluasi
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        
        # Format hasil
        if isinstance(result, float):
            if result.is_integer():
                result = int(result)
            else:
                result = round(result, 4)
        
        await update.message.reply_text(f"📊 Hasil: `{expression}` = **{result}**", parse_mode='Markdown')
        
    except ZeroDivisionError:
        await update.message.reply_text("❌ Error: Tidak bisa membagi dengan nol!")
    except Exception as e:
        await update.message.reply_text(f"❌ Format salah. Contoh: `2 + 2 * 3`")

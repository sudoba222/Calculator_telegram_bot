import logging
import os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from safe_eval import safe_eval


load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def build_keyboard():
    keys = [
        ["7", "8", "9", "/"],
        ["4", "5", "6", "*"],
        ["1", "2", "3", "-"],
        ["0", ".", "%", "+"],
        ["(", ")", "**", "⌫"],
        ["C", "=",],

    ]
    keyboard = [
        [InlineKeyboardButton(k, callback_data=k) for k in row] for row in keys
    ]
    return InlineKeyboardMarkup(keyboard)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    expr = ""
    context.chat_data["expr"] = expr
    await update.message.reply_text(
        f"Calculator\n\n{expr or '0'}", reply_markup=build_keyboard()
    )

# Handle button presses
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    expr = context.chat_data.get("expr", "")

    data = query.data
    if data == "C":
        expr = ""
    elif data == "⌫":
        expr = expr[:-1]
    elif data == "=":
        try:
            result = safe_eval(expr or "0")
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            expr = str(result)
        except Exception:
            expr = "Error"
    else:
        expr += data

    context.chat_data["expr"] = expr
    await query.edit_message_text(
        f"Calculator\n\n{expr or '0'}", reply_markup=build_keyboard()
    )

# If user types a math expression
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    try:
        result = safe_eval(txt)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        await update.message.reply_text(f"{txt} = {result}")
    except Exception as e:
        await update.message.reply_text(f"Could not evaluate: {e}")

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN not found. Put it in .env file.")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
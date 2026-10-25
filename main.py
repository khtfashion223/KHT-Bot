import os
import json
import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DATA_FILE = "kht_data.json"

CATEGORY, NAME, COST, PRICE, STOCK = range(5)
ORDER_PRODUCT, ORDER_QTY, ORDER_NAME, ORDER_PHONE, ORDER_ADDRESS = range(5, 10)

MENU = [
    ["👗 အဝတ်အစား", "💄 အလှကုန်"],
    ["🛒 ပစ္စည်းအားလုံး", "📦 ကျွန်ုပ်၏ Order"],
    ["📞 ဆက်သွယ်ရန်"],
]

ADMIN_MENU = [
    ["➕ ပစ္စည်းထည့်ရန်", "📋 ပစ္စည်းစာရင်း"],
    ["🛒 Order များ", "📊 အရောင်းစာရင်း"],
    ["🏠 ပင်မ Menu"],
]


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                data.setdefault("products", [])
                data.setdefault("orders", [])
                return data
        except (OSError, json.JSONDecodeError):
            logging.exception("Could not read database")

    return {"products": [], "orders": []}


data = load_data()


def save_data():
    temporary = DATA_FILE + ".tmp"
    with open(temporary, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(temporary, DATA_FILE)


def is_admin(update):
    return (
        update.effective_user is not None
        and ADMIN_ID != 0
        and update.effective_user.id == ADMIN_ID
    )


def main_keyboard(update):
    if is_admin(update):
        return ReplyKeyboardMarkup(
            ADMIN_MENU + [["👗 အဝတ်အစား", "💄 အလှကုန်"],
                           ["🛒 ပစ္စည်းအားလုံး", "📦 ကျွန်ုပ်၏ Order"],
                           ["📞 ဆက်သွယ်ရန်"]],
            resize_keyboard=True,
        )
    return ReplyKeyboardMarkup(MENU, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏪 KHT Fashion House မှ ကြိုဆိုပါတယ်။\n\n"
        "👗 အဝတ်အစားနှင့် 💄 အလှကုန်များကို "
        "ဒီ Bot မှာ ကြည့်ရှုပြီး မှာယူနိုင်ပါတယ်။",
        reply_markup=main_keyboard(update),
    )


async def show_products(update, context, category=None):
    products = [
        p for p in data["products"]
        if category is None or p.get("category") == category
    ]

    if not products:
        await update.message.reply_text("လောလောဆယ် ပစ္စည်းမရှိသေးပါ။")
        return

    for

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
DATA_FILE = os.getenv("DATA_FILE", "kht_data.json")

CATEGORY, NAME, COST, PRICE, STOCK = range(5)
ORDER_QTY, ORDER_NAME, ORDER_PHONE, ORDER_ADDRESS = range(5, 9)

CUSTOMER_MENU = [
    ["👗 အဝတ်အစား", "💄 အလှကုန်"],
    ["🛍️ ပစ္စည်းအားလုံး", "📦 ကျွန်ုပ်၏ Order"],
    ["📞 ဆက်သွယ်ရန်"],
]

ADMIN_MENU = [
    ["➕ ပစ္စည်းထည့်ရန်", "📋 ပစ္စည်းစာရင်း"],
    ["🛒 Order များ", "📊 အရောင်းစာရင်း"],
    ["👗 အဝတ်အစား", "💄 အလှကုန်"],
    ["🛍️ ပစ္စည်းအားလုံး", "📦 ကျွန်ုပ်၏ Order"],
    ["📞 ဆက်သွယ်ရန်"],
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
            logging.exception("Database could not be loaded")

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


def keyboard(update):
    if is_admin(update):
        return ReplyKeyboardMarkup(ADMIN_MENU, resize_keyboard=True)

    return ReplyKeyboardMarkup(CUSTOMER_MENU, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏪 KHT Fashion House မှ ကြိုဆိုပါတယ်။\n\n"
        "👗 အဝတ်အစားနှင့် 💄 အလှကုန်များကို "
        "ကြည့်ရှု၍ Order တင်နိုင်ပါတယ်။\n\n"
        "ပစ္စည်းမှာယူရန် ပစ္စည်းစာရင်းထဲက Order Command ကိုနှိပ်ပါ။",
        reply_markup=keyboard(update),
    )


async def show_products(update, context, category=None):
    products = [
        p for p in data["products"]
        if category is None or p.get("category") == category
    ]

    if not products:
        await update.message.reply_text("လောလောဆယ် ပစ္စည်းမရှိသေးပါ။")
        return

    for p in products:
        await update.message.reply_text(
            f"🛍️ {p['name']}\n"
            f"အမျိုးအစား: {p['category']}\n"
            f"ရောင်းဈေး: {p['price']:,.0f} ကျပ်\n"
            f"လက်ကျန်: {p['stock']} ထည်/ခု\n\n"
            f"မှာယူရန်: /order {p['id']}"
        )


async def add_product_start(update, context):
    if not is_admin(update):
        await update.message.reply_text("Admin သာ အသုံးပြုနိုင်ပါတယ်။")
        return ConversationHandler.END

    await update.message.reply_text(
        "ပစ္စည်းအမျိုးအစား ရွေးပါ။\n\n"
        "👗 အဝတ်အစား\n"
        "💄 အလှကုန်\n\n"
        "/cancel ဖြင့် ရပ်နိုင်ပါတယ်။"
    )

    return CATEGORY


async def add_category(update, context):
    choice = update.message.text.strip()

    if choice not in ("👗 အဝတ်အစား", "💄 အလှကုန်"):
        await update.message.reply_text(
            "👗 အဝတ်အစား သို့မဟုတ် 💄 အလှကုန်ကို ရွေးပါ။"
        )
        return CATEGORY

    context.user_data["category"] = choice

    await update.message.reply_text("ပစ္စည်းအမည် ထည့်ပါ။")
    return NAME


async def add_name(update, context):
    name = update.message.text.strip()

    if not name:
        await update.message.reply_text("ပစ္စည်းအမည် ထည့်ပါ။")
        return NAME

    context.user_data["name"] = name

    await update.message.reply_text("တစ်ထည်/တစ်ခု အရင်းဈေးကို ဂဏန်းဖြင့် ထည့်ပါ။")
    return COST


async def add_cost(update, context):
    try:
        value = float(update.message.text.replace(",", "").strip())

        if value < 0:
            raise ValueError

    except ValueError:
        await update.message.reply_text("အရင်းဈေးကို ဂဏန်းဖြင့် ထည့်ပါ။")
        return COST

    context.user_data["cost"] = value

    await update.message.reply_text("တစ်ထည်/တစ်ခု ရောင်းဈေး ထည့်ပါ။")
    return PRICE


async def add_price(update, context):
    try:
        value = float(update.message.text.replace(",", "").strip())

        if value < 0:
            raise ValueError

    except ValueError:
        await update.message.reply_text("ရောင်းဈေးကို ဂဏန်းဖြင့် ထည့်ပါ။")
        return PRICE

    context.user_data["price"] = value

    await update.message.reply_text("ပစ္စည်းအရေအတွက် ထည့်ပါ။")
    return STOCK


async def add_stock(update, context):
    try:
        stock = int(update.message.text.strip())

        if stock < 0:
            raise ValueError

    except ValueError:
        await update.message.reply_text("အရေအတွက်ကို 0 နှင့်အထက် ဂဏန်းဖြင့် ထည့်ပါ။")
        return STOCK

    product_id = max(
        (p["id"] for p in data["products"]),
        default=0
    ) + 1

    product = {
        "id": product_id,
        "category": context.user_data["category"],
        "name": context.user_data["name"],
        "cost": context.user_data["cost"],
        "price": context.user_data["price"],
        "stock": stock,
    }

    data["products"].append(product)
    save_data()
    context.user_data.clear()

    await update.message.reply_text(
        f"✅ ပစ္စည်းထည့်ပြီးပါပြီ။\n\n"
        f"ID: {product_id}\n"
        f"အမည်: {product['name']}\n"
        f"အရင်းဈေး: {product['cost']:,.0f} ကျပ်\n"
        f"ရောင်းဈေး: {product['price']:,.0f} ကျပ်\n"
        f"လက်ကျန်: {stock}",
        reply_markup=keyboard(update),
    )

    return ConversationHandler.END


async def cancel(update, context):
    context.user_data.clear()

    await update.message.reply_text(
        "လုပ်ဆောင်မှု ရပ်လိုက်ပါပြီ။",
        reply_markup=keyboard(update),
    )

    return ConversationHandler.END


async def order_start(update, context):
    if not context.args:
        await update.message.reply_text(
            "ပစ္စည်းစာရင်းမှ /order ID ကိုနှိပ်ပါ။\n"
            "ဥပမာ: /order 1"
        )
        return ConversationHandler.END

    try:
        product_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("ပစ္စည်း ID မမှန်ပါ။")
        return ConversationHandler.END

    product = next(
        (p for p in data["products"] if p["id"] == product_id),
        None
    )

    if not product or product["stock"] <= 0:
        await update.message.reply_text("ပစ္စည်းမရှိတော့ပါ။")
        return ConversationHandler.END

    context.user_data["product_id"] = product_id

    await update.message.reply_text(
        f"{product['name']} ကို ဘယ်နှထည်/ခု မှာယူမလဲ?"
    )

    return ORDER_QTY


async def order_quantity(update, context):
    try:
        quantity = int(update.message.text.strip())

        if quantity <= 0:
            raise ValueError

    except ValueError:
        await update.message.reply_text("အရေအတွက်ကို မှန်ကန်စွာ ထည့်ပါ။")
        return ORDER_QTY

    product = next(
        (
            p for p in data["products"]
            if p["id"] == context.user_data["product_id"]
        ),
        None
    )

    if not product or quantity > product["stock"]:
        await update.message.reply_text("လက်ကျန်ပစ္စည်း မလုံလောက်ပါ။")
        return ConversationHandler.END

    context.user_data["quantity"] = quantity

    await update.message.reply_text("မှာယူသူအမည် ထည့်ပါ။")
    return ORDER_NAME


async def order_customer_name(update, context):
    name = update.message.text.strip()

    if not name:
        await update.message.reply_text("အမည် ထည့်ပါ။")
        return ORDER_NAME

    context.user_data["customer"] = name

    await update.message.reply_text("ဆက်သွယ်ရန် ဖုန်းနံပါတ် ထည့်ပါ။")
    return ORDER_PHONE


async def order_phone(update, context):
    phone = update.message.text.strip()

    if len(phone) < 5:
        await update.message.reply_text("ဖုန်းနံပါတ်ကို ပြန်စစ်ပြီး ထည့်ပါ။")
        return ORDER_PHONE

    context.user_data["phone"] = phone

    await update.message.reply_text("ပို့ဆောင်ရမည့် လိပ်စာ ထည့်ပါ။")
    return ORDER_ADDRESS


async def order_address(update, context):
    address = update.message.text.strip()

    if not address:
        await update.message.reply_text("လိပ်စာ ထည့်ပါ။")
        return ORDER_ADDRESS

    product = next(
        (
            p for p in data["products"]
            if p["id"] == context.user_data["product_id"]
        ),
        None
    )

    quantity = context.user_data["quantity"]

    if not product or product["stock"] < quantity:
        await update.message.reply_text(
            "ပစ္စည်းလက်ကျန် မလုံလောက်တော့ပါ။ ပြန်စမ်းကြည့်ပါ။"
        )
        return ConversationHandler.END

    order_id = max(
        (o["id"] for o in data["orders"]),
        default=0
    ) + 1

    total = product["price"] * quantity

    order = {
        "id": order_id,
        "user_id": update.effective_user.id,
        "customer": context.user_data["customer"],
        "phone": context.user_data["phone"],
        "address": address,
        "product_id": product["id"],
        "product": product["name"],
        "quantity": quantity,
        "total": total,
        "cost": product["cost"] * quantity,
        "status": "Pending",
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    product["stock"] -= quantity
    data["orders"].append(order)
    save_data()

    await update.message.reply_text(
        f"✅ Order တင်ပြီးပါပြီ။\n\n"
        f"Order နံပါတ်: #{order_id}\n"
        f"ပစ္စည်း: {product['name']}\n"
        f"အရေအတွက်: {quantity}\n"
        f"စုစုပေါင်း: {total:,.0f} ကျပ်\n"
        f"အခြေအနေ: Pending\n\n"
        f"KHT Fashion House မှ ဆက်သွယ်ပေးပါမယ်။",
        reply_markup=keyboard(update),
    )

    if ADMIN_ID:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    f"🛒 Order အသစ် #{order_id}\n\n"
                    f"အမည်: {order['customer']}\n"
                    f"ဖုန်း: {order['phone']}\n"
                    f"လိပ်စာ: {order['address']}\n"
                    f"ပစ္စည်း: {order['product']} x {quantity}\n"
                    f"စုစုပေါင်း: {total:,.0f} ကျပ်"
                ),
            )
        except Exception:
            logging.exception("Admin notification failed")

    context.user_data.clear()
    return ConversationHandler.END


async def my_orders(update, context):
    user_id = update.effective_user.id

    orders = [
        o for o in data["orders"]
        if o.get("user_id") == user_id
    ]

    if not orders:
        await update.message.reply_text("သင့်မှာ Order မရှိသေးပါ။")
        return

    for order in orders:
        await update.message.reply_text(
            f"Order #{order['id']}\n"
            f"ပစ္စည်း: {order['product']} x {order['quantity']}\n"
            f"စုစုပေါင်း: {order['total']:,.0f} ကျပ်\n"
            f"အခြေအနေ: {order['status']}"
        )


async def admin_products(update, context):
    if not is_admin(update):
        await update.message.reply_text("Admin သာ အသုံးပြုနိုင်ပါတယ်။")
        return

    if not data["products"]:
        await update.message.reply_text("ပစ္စည်းမရှိသေးပါ။")
        return

    for product in data["products"]:
        await update.message.reply_text(
            f"ID: {product['id']}\n"
            f"အမည်: {product['name']}\n"
            f"အရင်း: {product['cost']:,.0f} ကျပ်\n"
            f"ရောင်းဈေး: {product['price']:,.0f} ကျပ်\n"
            f"လက်ကျန်: {product['stock']}"
        )


async def admin_orders(update, context):
    if not is_admin(update):
        await update.message.reply_text("Admin သာ အသုံးပြုနိုင်ပါတယ်။")
        return

    if not data["orders"]:
        await update.message.reply_text("Order မရှိသေးပါ။")
        return

    for order in data["orders"]:
        await update.message.reply_text(
            f"Order #{order['id']}\n"
            f"အမည်: {order['customer']}\n"
            f"ဖုန်း: {order['phone']}\n"
            f"လိပ်စာ: {order['address']}\n"
            f"ပစ္စည်း: {order['product']} x {order['quantity']}\n"
            f"စုစုပေါင်း: {order['total']:,.0f} ကျပ်\n"
            f"အခြေအနေ: {order['status']}\n\n"
            f"အတည်ပြုရန်: /status_{order['id']}_confirmed\n"
            f"ပို့ရန်: /status_{order['id']}_shipped\n"
            f"ပို့ဆောင်ပြီး: /status_{order['id']}_delivered\n"
            f"ပယ်ဖျက်ရန်: /status_{order['id']}_cancelled"
        )


async def order_status(update, context):
    if not is_admin(update):
        await update.message.reply_text("Admin သာ အသုံးပြုနိုင်ပါတယ်။")
        return

    try:
        _, order_id_text, status_text = update.message.text.split("_", 2)
        order_id = int(order_id_text)

    except ValueError:
        await update.message.reply_text("Command မမှန်ပါ။")
        return

    statuses = {
        "confirmed": "Confirmed",
        "shipped": "Shipped",
        "delivered": "Delivered",
        "cancelled": "Cancelled",
    }

    if status_text not in statuses:
        await update.message.reply_text("Status မမှန်ပါ။")
        return

    order = next(
        (o for o in data["orders"] if o["id"] == order_id),
        None
    )

    if not order:
        await update.message.reply_text("Order မတွေ့ပါ။")
        return

    if order["status"] in ("Delivered", "Cancelled"):
        await update.message.reply_text("ဒီ Order ကို ပိတ်ပြီးသားပါ။")
        return

    if status_text == "cancelled":
        product = next(
            (
                p for p in data["products"]
                if p["id"] == order["product_id"]
            ),
            None
        )

        if product:
            product["stock"] += order["quantity"]

    order["status"] = statuses[status_text]
    save_data()

    await update.message.reply_text(
        f"Order #{order_id} → {order['status']}"
    )

    try:
        await context.bot.send_message(
            chat_id=order["user_id"],
            text=f"သင့် Order #{order_id} အခြေအနေ: {order['status']}"
        )
    except Exception:
        logging.exception("Customer notification failed")


async def business_summary(update, context):
    if not is_admin(update):
        await update.message.reply_text("Admin သာ အသုံးပြုနိုင်ပါတယ်။")
        return

    delivered = [
        o for o in data["orders"]
        if o["status"] == "Delivered"
    ]

    revenue = sum(o["total"] for o in delivered)
    cost = sum(o["cost"] for o in delivered)

    await update.message.reply_text(
        "📊 KHT Fashion House အရောင်းစာရင်း\n\n"
        f"ပစ္စည်းအမျိုးအစား စာရင်းဝင်အရေအတွက်: {len(data['products'])}\n"
        f"Order စုစုပေါင်း: {len(data['orders'])}\n"
        f"ပို့ဆောင်ပြီး Order: {len(delivered)}\n"
        f"ရောင်းရငွေ: {revenue:,.0f} ကျပ်\n"
        f"ပစ္စည်းအရင်း: {cost:,.0f} ကျပ်\n"
        f"အကြမ်းအမြတ်: {revenue - cost:,.0f} ကျပ်\n\n"
        "မှတ်ချက်: ပို့ခနှင့် အခြားကုန်ကျစရိတ်များ မပါဝင်သေးပါ။"
    )


async def contact(update, context):
    await update.message.reply_text(
        "📞 KHT Fashion House\n\n"
        "Order နှင့် ပစ္စည်းအကြောင်း မေးမြန်းလိုပါက "
        "ဒီ Telegram Bot မှတစ်ဆင့် ဆက်သွယ်နိုင်ပါတယ်။"
    )


async def menu_router(update, context):
    text = update.message.text

    if text == "👗 အဝတ်အစား":
        await show_products(update, context, "👗 အဝတ်အစား")

    elif text == "💄 အလှကုန်":
        await show_products(update, context, "💄 အလှကုန်")

    elif text == "🛍️ ပစ္စည်းအားလုံး":
        await show_products(update, context)

    elif text == "📦 ကျွန်ုပ်၏ Order":
        await my_orders(update, context)

    elif text == "📞 ဆက်သွယ်ရန်":
        await contact(update, context)

    elif text == "➕ ပစ္စည်းထည့်ရန်":
        await add_product_start(update, context)

    elif text == "📋 ပစ္စည်းစာရင်း":
        await admin_products(update, context)

    elif text == "🛒 Order များ":
        await admin_orders(update, context)

    elif text == "📊 အရောင်းစာရင်း":
        await business_summary(update, context)

    else:
        await update.message.reply_text(
            "Menu ထဲက ရွေးချယ်မှုကို နှိပ်ပါ။",
            reply_markup=keyboard(update),
        )


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN မသတ်မှတ်ရသေးပါ။")

    if ADMIN_ID == 0:
        raise RuntimeError("ADMIN_ID မသတ်မှတ်ရသေးပါ။")

    app = Application.builder().token(TOKEN).build()

    add_product_conv = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex("^➕ ပစ္စည်းထည့်ရန်$"),
                add_product_start,
            )
        ],
        states={
            CATEGORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_category)
            ],
            NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_name)
            ],
            COST: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_cost)
            ],
            PRICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_price)
            ],
            STOCK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_stock)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    order_conv = ConversationHandler(
        entry_points=[CommandHandler("order", order_start)],
        states={
            ORDER_QTY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, order_quantity)
            ],
            ORDER_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, order_customer_name)
            ],
            ORDER_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, order_phone)
            ],
            ORDER_ADDRESS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, order_address)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(add_product_conv)
    app.add_handler(order_conv)
    app.add_handler(
        MessageHandler(filters.Regex(r"^/status_"), order_status)
    )
    app.add_handler(CommandHandler("admin", admin_orders))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, menu_router)
    )

    print("KHT Fashion House Bot is starting...")
    app.run_polling()


if __name__ == "__main__":
    main()

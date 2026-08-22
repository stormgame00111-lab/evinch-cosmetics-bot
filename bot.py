import os
import sqlite3
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, ContextTypes, filters
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_CHAT_ID")

db = sqlite3.connect("shop.db", check_same_thread=False)
db.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INTEGER NOT NULL
)
""")

if db.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
    db.executemany(
        "INSERT INTO products (name, price) VALUES (?, ?)",
        [
            ("💄 Lipstick", 89000),
            ("🧴 Face Cream", 119000),
            ("🌸 Perfume", 249000),
            ("👁 Mascara", 99000)
        ]
    )
    db.commit()

NAME, PHONE, ADDRESS = range(3)

def money(n):
    return f"{n:,}".replace(",", " ") + " so'm"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cart"] = []

    keyboard = [
        [InlineKeyboardButton("💄 Mahsulotlar", callback_data="products")]
    ]

    await update.message.reply_text(
        "🌸 Sevinch Cosmetics'ga xush kelibsiz!\n\n"
        "Mahsulot tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    rows = db.execute(
        "SELECT id, name, price FROM products"
    ).fetchall()

    keyboard = [
        [
            InlineKeyboardButton(
                f"{name} — {money(price)}",
                callback_data=f"add:{pid}"
            )
        ]
        for pid, name, price in rows
    ]

    keyboard.append([
        InlineKeyboardButton("🛒 Savat", callback_data="cart")
    ])

    await query.edit_message_text(
        "💄 Mahsulotlar:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("✅ Savatga qo'shildi")

    product_id = int(query.data.split(":")[1])

    context.user_data.setdefault("cart", []).append(product_id)

    await products(update, context)

async def cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    cart_items = context.user_data.get("cart", [])

    if not cart_items:
        keyboard = [
            [InlineKeyboardButton("💄 Mahsulotlar", callback_data="products")]
        ]

        await query.edit_message_text(
            "🛒 Savat bo'sh.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    lines = []
    total = 0

    for product_id in cart_items:
        row = db.execute(
            "SELECT name, price FROM products WHERE id=?",
            (product_id,)
        ).fetchone()

        if row:
            name, price = row
            lines.append(f"• {name} — {money(price)}")
            total += price

    keyboard = [
        [InlineKeyboardButton("✅ Buyurtma berish", callback_data="order")],
        [InlineKeyboardButton("💄 Yana mahsulot", callback_data="products")]
    ]

    await query.edit_message_text(
        "🛒 SAVAT\n\n" +
        "\n".join(lines) +
        f"\n\n💰 Jami: {money(total)}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "👤 Ismingizni yozing:"
    )

    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text

    keyboard = [[
        KeyboardButton(
            "📞 Telefon raqamimni yuborish",
            request_contact=True
        )
    ]]

    await update.message.reply_text(
        "📞 Telefon raqamingizni yuboring:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )

    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        context.user_data["phone"] = update.message.contact.phone_number
    else:
        context.user_data["phone"] = update.message.text

    await update.message.reply_text(
        "📍 Yetkazib berish manzilingizni yozing:",
        reply_markup=ReplyKeyboardRemove()
    )

    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text

    cart_items = context.user_data.get("cart", [])

    lines = []
    total = 0

    for product_id in cart_items:
        row = db.execute(
            "SELECT name, price FROM products WHERE id=?",
            (product_id,)
        ).fetchone()

        if row:
            name, price = row
            lines.append(f"• {name} — {money(price)}")
            total += price

    message = (
        "🛍 YANGI BUYURTMA\n\n"
        f"👤 Ism: {context.user_data['name']}\n"
        f"📞 Telefon: {context.user_data['phone']}\n"
        f"📍 Manzil: {context.user_data['address']}\n\n"
        + "\n".join(lines) +
        f"\n\n💰 JAMI: {money(total)}"
    )

    if ADMIN_ID:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=message
        )

    await update.message.reply_text(
        "✅ Buyurtmangiz qabul qilindi!\n\n"
        "Tez orada siz bilan bog'lanamiz. 🌸",
        reply_markup=ReplyKeyboardRemove()
    )

    context.user_data["cart"] = []

    return ConversationHandler.END

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN berilmagan")

    application = Application.builder().token(TOKEN).build()

    conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(order_start, pattern="^order$")
        ],
        states={
            NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_name
                )
            ],
            PHONE: [
                MessageHandler(
                    (filters.CONTACT | filters.TEXT) & ~filters.COMMAND,
                    get_phone
                )
            ],
            ADDRESS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_address
                )
            ]
        },
        fallbacks=[]
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conversation)
    application.add_handler(
        CallbackQueryHandler(products, pattern="^products$")
    )
    application.add_handler(
        CallbackQueryHandler(add_to_cart, pattern="^add:")
    )
    application.add_handler(
        CallbackQueryHandler(cart, pattern="^cart$")
    )

    print("Sevinch Cosmetics bot ishga tushdi!")
    application.run_polling()

if __name__ == "__main__":
    main()

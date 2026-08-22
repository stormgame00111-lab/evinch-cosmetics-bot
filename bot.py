import os
import sqlite3

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN")

# Admin lichkasi
ADMIN_USERNAME = "sevinch_cosmetics_admin"
ADMIN_URL = "https://t.me/sevinch_cosmetics_admin"

# =========================
# DATABASE
# =========================

db = sqlite3.connect("shop.db", check_same_thread=False)

db.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    price INTEGER NOT NULL
)
""")

# Agar eski database'da description ustuni bo'lmasa, qo'shamiz
columns = [
    row[1] for row in db.execute("PRAGMA table_info(products)").fetchall()
]

if "description" not in columns:
    db.execute(
        "ALTER TABLE products ADD COLUMN description TEXT DEFAULT ''"
    )

db.commit()


# =========================
# MAHSULOTLAR
# =========================

PRODUCTS = [
    {
        "name": "💄 Lipstick",
        "description": "Chiroyli rang beruvchi lipstick.",
        "price": 89000,
    },
    {
        "name": "🧴 Face Cream",
        "description": "Yuz terisi uchun krem.",
        "price": 119000,
    },
    {
        "name": "🌸 Perfume",
        "description": "Yoqimli hidli parfum.",
        "price": 249000,
    },
    {
        "name": "👁 Mascara",
        "description": "Kipriklarni chiroyli va hajmli ko‘rsatadi.",
        "price": 99000,
    },

    {
        "name": "✨ CC Cream",
        "description": (
            "Yuzdagi qizarishlar va mayda dog‘larni yopib, "
            "yuzni tiniq ko‘rsatadi. Tarkibida SPF mavjud."
            "\n\n🇰🇷 Original Koreya mahsuloti."
        ),
        "price": 135000,
    },

    {
        "name": "🌸 Teen Skin nabor",
        "description": (
            "Muammoli terilar uchun nabor. "
            "Husnbuzarlarni kamaytirishga yordam beradi."
            "\n\nSalitsil kislotasi poralarni tozalashga "
            "va yog‘ hamda o‘lik hujayralarni ketkazishga yordam beradi."
        ),
        "price": 95000,
    },

    {
        "name": "🇰🇷 ROUND LAB mini uhod nabor",
        "description": (
            "ROUND LAB brendidan 100% original mini uhod nabor."
            "\n\n🇰🇷 Koreya mahsuloti."
        ),
        "price": 65000,
    },

    {
        "name": "🎀 JOCO tanalka",
        "description": (
            "Barcha teri turlari uchun tanalka. "
            "Tabiiy va chiroyli qoplama beradi."
        ),
        "price": 50000,
    },

    {
        "name": "🌟 Stikli tanalka",
        "description": (
            "Trenddagi stikli tanalka. "
            "O‘zining kisti bilan qulay foydalaniladi."
        ),
        "price": 50000,
    },

    {
        "name": "⭐ Broslet",
        "description": "Chiroyli va nafis broslet.",
        "price": 35000,
    },

    {
        "name": "💗 Faberlic ten paletka",
        "description": (
            "Faberlicdan ten paletkalar. "
            "Kist bonus sifatida qo‘shib beriladi. 🌟"
        ),
        "price": 40000,
    },

    {
        "name": "💧 Faberlic HyaluronCa uhod nabor",
        "description": (
            "1. Ko‘z atrofi uchun krem\n"
            "2. Makiyaj ketkazish uchun penka\n"
            "3. Tungi krem\n"
            "4. Kunduzgi krem\n\n"
            "Yuzni namlash va yumshatishga yordam beradi. 🌟"
            "\n\n🔥 Aksiya narxi: 200 000 so‘m"
        ),
        "price": 200000,
    },

    {
        "name": "🎀 Stikli ten",
        "description": (
            "Ko‘zingizni professional makiyaj qilgandek "
            "chiroyli bo‘yab beradi."
        ),
        "price": 35000,
    },

    {
        "name": "✨ Carla Secret 5 in 1 professional paletka",
        "description": (
            "Yuz uchun barcha kerakli vositalar bitta qutida."
            "\n\n❤️ Rumyana — 6 xil rang"
            "\n👁️ Konsiler va korrektor"
            "\n👃 Kontur va bronzer"
            "\n\n🔥 Aksiya narxi: 99 000 so‘m"
        ),
        "price": 99000,
    },

    {
        "name": "💦 Makiyaj fiksatori",
        "description": (
            "Makiyajdan keyin sepiladi. "
            "Makiyajni uzoqroq saqlashga yordam beradi."
            "\n\nYozgi makiyaj uchun juda qulay. 🌸"
        ),
        "price": 40000,
    },

    {
        "name": "🦢 Flower Knows ten paletkasi",
        "description": (
            "✨ Flower Knows ten paletkalari 🌟🎀"
            "\n\n🔥 Aksiyada!"
        ),
        "price": 99000,
    },

    {
        "name": "🌸 Mini rumyana",
        "description": (
            "Koreyscha uslubdagi mini rumyana."
            "\n\n💗 Pigmentatsiyasi zo‘r."
            "\n✨ Bir joyga yig‘ilib qolmaydi."
            "\n💄 Yonoqlarga chiroyli tus beradi."
        ),
        "price": 10000,
    },

    {
        "name": "🌹 Perfume stoykasi",
        "description": (
            "Tualet va parfюм uchun chiroyli stoyka. 😍"
        ),
        "price": 50000,
    },
]


# =========================
# DATABASE'GA MAHSULOTLARNI QO'SHISH
# =========================

def add_products_to_database():
    for product in PRODUCTS:
        exists = db.execute(
            "SELECT id FROM products WHERE name = ?",
            (product["name"],)
        ).fetchone()

        if exists:
            # Narx va tavsifni yangilaymiz
            db.execute(
                """
                UPDATE products
                SET price = ?, description = ?
                WHERE name = ?
                """,
                (
                    product["price"],
                    product["description"],
                    product["name"],
                )
            )
        else:
            db.execute(
                """
                INSERT INTO products
                (name, description, price)
                VALUES (?, ?, ?)
                """,
                (
                    product["name"],
                    product["description"],
                    product["price"],
                )
            )

    db.commit()


add_products_to_database()


# =========================
# YORDAMCHI FUNKSIYALAR
# =========================

def money(number):
    return f"{number:,}".replace(",", " ") + " so‘m"


def product_text(name, description, price):
    return (
        f"<b>{name}</b>\n\n"
        f"{description}\n\n"
        f"<b>💰 Narxi: {money(price)}</b>"
    )


async def safe_edit(query, text, keyboard=None):
    try:
        await query.edit_message_text(
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )
    except BadRequest as error:
        # Telegram "Message is not modified" desa bot to'xtab qolmasin
        if "Message is not modified" not in str(error):
            raise


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["cart"] = []

    keyboard = [
        [
            InlineKeyboardButton(
                "💄 Mahsulotlar",
                callback_data="products"
            )
        ],
        [
            InlineKeyboardButton(
                "🛒 Savat",
                callback_data="cart"
            )
        ],
    ]

    await update.message.reply_text(
        "<b>🌸 Sevinch Cosmetics'ga xush kelibsiz!</b>\n\n"
        "💄 Mahsulot tanlang:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================
# MAHSULOTLAR
# =========================

async def products(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    rows = db.execute(
        "SELECT id, name, price FROM products ORDER BY id"
    ).fetchall()

    keyboard = []

    for product_id, name, price in rows:
        keyboard.append([
            InlineKeyboardButton(
                f"{name} — {money(price)}",
                callback_data=f"add:{product_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🛒 Savat",
            callback_data="cart"
        )
    ])

    await safe_edit(
        query,
        "<b>💄 MAHSULOTLAR</b>\n\n"
        "Kerakli mahsulotni tanlang:",
        InlineKeyboardMarkup(keyboard),
    )


# =========================
# SAVATGA QO'SHISH
# =========================

async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer(
        "✅ Savatga qo‘shildi!",
        show_alert=False
    )

    product_id = int(query.data.split(":")[1])

    context.user_data.setdefault("cart", []).append(product_id)

    await products(update, context)


# =========================
# SAVAT
# =========================

async def cart(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    cart_items = context.user_data.get("cart", [])

    if not cart_items:

        keyboard = [
            [
                InlineKeyboardButton(
                    "💄 Mahsulotlar",
                    callback_data="products"
                )
            ]
        ]

        await safe_edit(
            query,
            "<b>🛒 SAVAT</b>\n\n"
            "Savat hozircha bo‘sh.",
            InlineKeyboardMarkup(keyboard),
        )

        return

    lines = []
    total = 0

    for product_id in cart_items:

        row = db.execute(
            """
            SELECT name, price
            FROM products
            WHERE id = ?
            """,
            (product_id,)
        ).fetchone()

        if row:
            name, price = row

            lines.append(
                f"• <b>{name}</b> — {money(price)}"
            )

            total += price

    text = (
        "<b>🛒 SAVATINGIZ</b>\n\n"
        + "\n".join(lines)
        + f"\n\n<b>💰 JAMI: {money(total)}</b>"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "🛍 Zakaz berish",
                url=ADMIN_URL
            )
        ],
        [
            InlineKeyboardButton(
                "💄 Yana mahsulot",
                callback_data="products"
            )
        ],
        [
            InlineKeyboardButton(
                "🗑 Savatni tozalash",
                callback_data="clear_cart"
            )
        ],
    ]

    await safe_edit(
        query,
        text,
        InlineKeyboardMarkup(keyboard),
    )


# =========================
# SAVATNI TOZALASH
# =========================

async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer(
        "🗑 Savat tozalandi!"
    )

    context.user_data["cart"] = []

    keyboard = [
        [
            InlineKeyboardButton(
                "💄 Mahsulotlar",
                callback_data="products"
            )
        ]
    ]

    await safe_edit(
        query,
        "<b>🛒 SAVAT</b>\n\n"
        "Savat tozalandi.",
        InlineKeyboardMarkup(keyboard),
    )


# =========================
# BOTNI ISHGA TUSHIRISH
# =========================

def main():

    if not TOKEN:
        raise RuntimeError(
            "BOT_TOKEN berilmagan"
        )

    application = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            products,
            pattern="^products$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            add_to_cart,
            pattern="^add:"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            cart,
            pattern="^cart$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            clear_cart,
            pattern="^clear_cart$"
        )
    )

    print(
        "🌸 Sevinch Cosmetics bot ishga tushdi!"
    )

    application.run_polling()


if __name__ == "__main__":
    main()

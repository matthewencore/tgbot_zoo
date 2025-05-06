from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from quiz_data import QUESTIONS
from utils.scoring import get_result_animal
from utils.image_gen import generate_result_image
from urllib.parse import quote
import sqlite3

user_states = {}
user_answers = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_states[user_id] = 0
    user_answers[user_id] = []
    await update.message.reply_text(
        "🐾 Привет! Готов узнать своё тотемное животное в Московском зоопарке?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Начать викторину 🐾", callback_data="start_quiz")]
        ])
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "contact":
        await query.message.reply_text(
            "📩 Контакты зоопарка:\n✉️ Email: zoo@moscowzoo.ru\n📞 Телефон: +7 (495) 123-45-67"
        )
        return



    if data == "start_quiz":
        user_states[user_id] = 0
        user_answers[user_id] = []
        await send_question(query.message, user_id)
        return

    if data == "about_opeka":
        await query.message.reply_text(
            "👨‍👩‍👧‍👦 Программа опеки Московского зоопарка позволяет вам стать частью жизни животного!"
            "Вы можете выбрать животное и помогать заботиться о нём — морально и материально."
            "Подробнее: https://moscowzoo.ru/my-zoo/opeka"
        )
        return

    if data == "leave_feedback":
        await query.message.reply_text("✍️ Напиши свой отзыв прямо в чат. Мы читаем каждый!")
        return

    if not data.startswith("answer_"):
        await query.message.reply_text("⚠️ Некорректный ответ.")
        return

    try:
        answer = int(data.split("_")[1])
    except:
        await query.message.reply_text("⚠️ Ошибка при разборе ответа.")
        return

    if user_id not in user_states or user_states[user_id] >= len(QUESTIONS):
        await query.message.reply_text("❗ Пожалуйста, начни викторину заново с /start.")
        return

    user_answers[user_id].append(answer)
    user_states[user_id] += 1

    if user_states[user_id] < len(QUESTIONS):
        await send_question(query.message, user_id)
    else:
        result = get_result_animal(user_answers[user_id])
        username = query.from_user.username or query.from_user.first_name or "пользователь"
        image_path = generate_result_image(result, username=username)

        share_text = f"Я прошёл викторину в Московском зоопарке и узнал, что моё тотемное животное — {result['name']}! 🐾 Пройди и ты!"
        share_url = f"https://t.me/share/url?url=https://t.me/ZOO_MSCW_matthewencore_BOT&text={quote(share_text)}"
        vk_url = f"https://vk.com/share.php?url=https://t.me/ZOO_MSCW_matthewencore_BOT&title={quote(share_text)}"

        await query.message.reply_photo(
            photo=image_path,
            caption=(
                f"🎉 Твоё тотемное животное — {result['name']}!"
                f"{result['description']}"
                "🧡 Московский зоопарк предлагает уникальную программу опеки!"
                "Стань другом животного и поддержи его уход и питание."
                "Узнай больше об опеке — нажми на кнопку ниже!"
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔁 Пройти снова", callback_data="start_quiz")],
                [InlineKeyboardButton("💬 Оставить отзыв", callback_data="leave_feedback")],
                [InlineKeyboardButton("📘 Подробнее об опеке", callback_data="about_opeka")],
                [InlineKeyboardButton("💬 Контакт", callback_data="contact")],
                [
                    InlineKeyboardButton("📤 Поделиться в Telegram", url=share_url),
                    InlineKeyboardButton("📤 Поделиться во ВКонтакте", url=vk_url)
                ]
            ])
        )
        user_states.pop(user_id, None)
        user_answers.pop(user_id, None)

async def send_question(message, user_id):
    idx = user_states.get(user_id, 0)
    if idx >= len(QUESTIONS):
        return

    question = QUESTIONS[idx]
    keyboard = [[InlineKeyboardButton(opt["text"], callback_data=f"answer_{opt['score']}")]
                for opt in question["options"]]

    await message.reply_text(question["text"], reply_markup=InlineKeyboardMarkup(keyboard))

async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()
    conn = sqlite3.connect("feedback.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO feedback (user_id, username, text) VALUES (?, ?, ?)",
        (user.id, user.username, text)
    )
    conn.commit()
    conn.close()
    await update.message.reply_text("Спасибо за отзыв! 🧡 Мы читаем каждый.")

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != 5612071306:
        await update.message.reply_text("🚫 У вас нет доступа к админ-панели.")
        return
    await update.message.reply_text(
        "🛠 Админ-панель доступна:"
        "\n/admin_feedback — последние отзывы"
        "\n/export_feedback — экспорт CSV"
        "\n/contact — контакты зоопарка"
        "\n/start — начать викторину"
    )

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"📩 Контакты зоопарка:\n"
        f"✉️ Email: zoo@moscowzoo.ru\n"
        f"📞 Телефон: +7 (495) 123-45-67\n"
        f"Ваш ID: {user.id}"
    )

async def admin_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != 5612071306:
        await update.message.reply_text("🚫 У вас нет доступа к этой команде.")
        return

    import sqlite3
    conn = sqlite3.connect("feedback.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, text, timestamp FROM feedback ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("Отзывов пока нет.")
        return

    message = "\n\n".join([f"👤 @{r[1] or '—'} ({r[0]})\n🕒 {r[3]}\n💬 {r[2]}" for r in rows])
    await update.message.reply_text(f"📥 Последние отзывы:\n\n{message}")

async def export_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != 5612071306:
        await update.message.reply_text("🚫 У вас нет доступа к экспорту.")
        return

    import sqlite3, csv
    conn = sqlite3.connect("feedback.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, text, timestamp FROM feedback")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("Нет отзывов для экспорта.")
        return

    with open("feedback_export.csv", "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["User ID", "Username", "Text", "Timestamp"])
        writer.writerows(rows)

    with open("feedback_export.csv", "rb") as csvfile:
        await update.message.reply_document(csvfile, filename="feedback_export.csv")


def main():
    app = ApplicationBuilder().token("7968140640:AAGo4G4BkchwBxrha_V6DGsgc-0AVISrxUk").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, feedback))
    app.add_handler(CommandHandler("admin_feedback", admin_feedback))
    app.add_handler(CommandHandler("export_feedback", export_feedback))
    app.add_handler(CommandHandler("contact", contact))
    app.run_polling()

if __name__ == "__main__":
    main()

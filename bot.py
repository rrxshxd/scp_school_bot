from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from telegram.ext import CallbackQueryHandler
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT", 5432)
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

(FULL_NAME, USERNAME, GROUP, LEVEL, LANGUAGES, MOTIVATION, EXPERIENCE) = range(7)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Давай заполним твою заявку.\nНапиши свое ФИО:")
    return FULL_NAME

async def full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["full_name"] = update.message.text
    await update.message.reply_text("Отлично! Теперь отправь свой Telegram username (без @):")
    return USERNAME

async def username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["username"] = update.message.text
    await update.message.reply_text("Напиши номер своей группы:")
    return GROUP

async def group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["group_number"] = update.message.text

    keyboard = [["Основы"], ["Уверенный уровень"], ["Проходил стажировки / работал в сфере"]]
    await update.message.reply_text(
        "Выбери уровень владения программированием:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    )
    return LEVEL

async def level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["programming_level"] = update.message.text
    await update.message.reply_text("Какие языки программирования ты знаешь?")
    return LANGUAGES

async def languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["known_languages"] = update.message.text
    await update.message.reply_text("Почему ты хочешь участвовать в проекте SCP School?")
    return MOTIVATION

async def motivation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["motivation"] = update.message.text
    await update.message.reply_text("Есть ли у тебя опыт работы с детьми или преподавания?")
    return EXPERIENCE

async def experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["teaching_experience"] = update.message.text

    user_data = context.user_data

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO applications (username, full_name, group_number, programming_level, known_languages, motivation, teaching_experience)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (username) DO UPDATE SET
            full_name = EXCLUDED.full_name,
            group_number = EXCLUDED.group_number,
            programming_level = EXCLUDED.programming_level,
            known_languages = EXCLUDED.known_languages,
            motivation = EXCLUDED.motivation,
            teaching_experience = EXCLUDED.teaching_experience;
    """, (
        user_data["username"],
        user_data["full_name"],
        user_data["group_number"],
        user_data["programming_level"],
        user_data["known_languages"],
        user_data["motivation"],
        user_data["teaching_experience"]
    ))
    conn.commit()
    cur.close()
    conn.close()

    await update.message.reply_text("Спасибо! Твоя заявка была принята.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Заявка отменена.")
    return ConversationHandler.END

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, full_name)],
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, username)],
            GROUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, group)],
            LEVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, level)],
            LANGUAGES: [MessageHandler(filters.TEXT & ~filters.COMMAND, languages)],
            MOTIVATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, motivation)],
            EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, experience)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
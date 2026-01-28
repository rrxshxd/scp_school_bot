from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
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

(MENU, FULL_NAME, USERNAME, GROUP, LEVEL, LANGUAGES, MOTIVATION, EXPERIENCE) = range(8)

async def exit_conversation(update: Update):
    keyboard = [["Информация о школе"], ["Заполнить заявку"], ["Выйти"]]
    await update.message.reply_text("Ты вышел из заполнения анкеты. Выбери действие:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
                                    )
    return MENU

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Информация о школе"], ["Заполнить заявку"], ["Выйти"]]
    await update.message.reply_text(
        "Привет! Это бот по приему заявок на участие в проекте SCP School.\n"
        "Выбери действие:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return MENU

async def menu_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text

    if choice == "Информация о школе":
        keyboard = [["Назад"], ["Выйти"]]
        info_text = (
            "🌍 Миссия:\n\n"
            "SCP School — это больше, чем школа программирования. Это проект, который меняет жизни. "
            "Мы даём подросткам из социально уязвимых слоёв шанс войти в мир IT: пройти путь от первых строк кода "
            "до уверенной разработки собственных приложений.\n"
            "Каждый урок — это маленький шаг к большим мечтам.\n\n"
            "📚 Как устроено обучение:\n\n"
            "1) Обучение строится на трёхлетней программе: от основ до уверенного уровня программиста.\n\n"
            "2) Каждый год разделён на 4 триместра — осенний, зимний, весенний и летний.\n\n"
            "3) Каждый триместр приходят новые группы школьников: кто-то делает первый шаг в IT, а кто-то продолжает свой путь.\n\n"
            "4) Занятия проходят офлайн по субботам, 1,5 часа (40 мин теория + 40 мин практика).\n\n"
            "5) В каждой группе — до 10 школьников и 2 преподавателя, чтобы каждому уделить внимание.\n\n"
            "6) Каждую неделю ученики получают домашние задания, а преподаватели сопровождают их и поддерживают онлайн.\n\n"
            "👩‍🏫 Роль преподавателя:\n\n"
            "Ты не просто объясняешь код — ты вдохновляешь.\n"
            "Преподаватель в SCP School — это наставник, который помогает школьникам поверить в себя и увидеть, "
            "что IT — это не сухая теория, а живые проекты и свобода идей.\n\n"
            "🎁 Что ты получишь:\n\n"
            "1) 📈 Получишь + к социальному и научному GPA.\n\n"
            "2) 🎓 Сертификат от AITU с указанием часов преподавания.\n\n"
            "3) 🗣 Прокачаешь навыки коммуникации, работы в команде и лидерства.\n\n"
            "4) 💡 Ценный опыт преподавания, который оценят работодатели.\n\n"
            "5) ❤️ Главное — почувствуешь, что ты реально меняешь чью-то жизнь.\n\n"
            "💡 Кого мы ищем:\n\n"
            "1) Студентов, готовых преподавать frontend или backend разработку.\n\n"
            "2) Тех, кто умеет говорить простыми словами о сложных вещах.\n\n"
            "3) Людей, которым важно развитие других так же, как и собственное.\n\n"
            "4) И особенно ценится опыт работы с детьми — он помогает лучше понимать учеников и находить с ними общий язык."
        )

        await update.message.reply_text(
            info_text,
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return MENU

    elif choice == "Заполнить заявку":
        await update.message.reply_text("Напиши свое ФИО:")
        return FULL_NAME

    elif choice == "Назад":
        keyboard = [["Информация о школе"], ["Заполнить заявку"], ["Выйти"]]
        await update.message.reply_text(
            "Ты вернулся в меню.\nВыбери действие:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return MENU

    elif choice == "Выйти":
        await update.message.reply_text(
            "Ты вышел из бота. Чтобы снова его запустить - напиши /start",
            reply_markup=ReplyKeyboardRemove(),
        )

        return ConversationHandler.END

    else:
        await update.message.reply_text("Пожалуйста, выбери действие из меню.")
        return MENU


async def full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Отмена":
        return await exit_conversation(update)

    context.user_data["full_name"] = update.message.text
    keyboard =[["Отмена"]]
    await update.message.reply_text("Отлично! Теперь напиши свой Telegram username (без @):", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return USERNAME

async def username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Отмена":
        return await exit_conversation(update)

    context.user_data["username"] = update.message.text
    keyboard =[["Отмена"]]
    await update.message.reply_text("Напиши номер своей группы:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return GROUP

async def group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Отмена":
        return await exit_conversation(update)

    context.user_data["group_number"] = update.message.text
    keyboard = [["Основы"], ["Уверенный уровень"], ["Проходил стажировки / работал в сфере"], ["Отмена"]]
    await update.message.reply_text(
        "Выбери уровень владения программированием:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return LEVEL

async def level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Отмена":
        return await exit_conversation(update)

    context.user_data["programming_level"] = update.message.text
    keyboard =[["Отмена"]]
    await update.message.reply_text("Какие языки программирования ты знаешь?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return LANGUAGES

async def languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Отмена":
        return await exit_conversation(update)

    context.user_data["known_languages"] = update.message.text
    keyboard =[["Отмена"]]
    await update.message.reply_text("Почему ты хочешь участвовать в проекте SCP School?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return MOTIVATION

async def motivation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Отмена":
        return await exit_conversation(update)

    context.user_data["motivation"] = update.message.text
    keyboard =[["Отмена"]]
    await update.message.reply_text("Есть ли у тебя опыт работы с детьми или преподавания?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
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

    keyboard = [["Информация о школе"], ["Заполнить заявку"], ["Выйти"]]
    await update.message.reply_text(
        "Ты снова в меню. Выбери действие:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await exit_conversation(update)

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_choice)],
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
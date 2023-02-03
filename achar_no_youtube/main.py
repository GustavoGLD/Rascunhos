import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webdriver import WebElement, WebDriver
from selenium.webdriver.support import expected_conditions as EC

import os
from dotenv import load_dotenv
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = await update.message.reply_text("Preparando o navegador...")
    context.user_data["driver"] = webdriver.Firefox()
    await message.edit_text("Digite o que quer buscar!")
    context.user_data["driver"].get("https://www.youtube.com/")

    return 1

async def typing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard: list[list[InlineKeyboardButton]] = []

    message = await update.message.reply_text("Pesquisando...")

    search_bar = context.user_data["driver"].find_element(By.XPATH, "//input[@id='search']")
    search_bar.click()
    search_bar.send_keys(update.message.text)


    presentations: list[WebElement] = WebDriverWait(context.user_data["driver"], 5).until(
        EC.presence_of_all_elements_located((By.XPATH, "//li[@role='presentation']"))
    )

    keyboard.append([InlineKeyboardButton(update.message.text, callback_data=update.message.text)])
    for present in presentations:
        keyboard.append([InlineKeyboardButton(present.text, callback_data=present.text)])
    keyboard.pop()

    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.edit_text("Possíveis resultados de pesquisa:", reply_markup=reply_markup)

    return 2

async def searching(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f'Pesquisando por "{" ".join(query.data.split())}"...')

    context.user_data["driver"].get("https://www.youtube.com/results?search_query=" + "+".join(query.data.split()))

    await query.edit_message_text(f"Deseja filtro por Data de Upload?", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("Sim", callback_data="True"), InlineKeyboardButton("Não", callback_data="False")],
    ]))

    return 3

async def get_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    driver: WebDriver = context.user_data["driver"]
    video: WebElement = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[1]"))
    ).find_element(By.ID, 'thumbnail')

    await context.bot.send_message(chat_id=update.effective_chat.id, text=video.get_attribute('href'))

    return ConversationHandler.END

async def asking_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "False":
        return await get_result(update, context)

    filters = ["Última hora", "Hoje", "Esta semana", "Este mês", "Este ano"]
    keyboard: list[list[InlineKeyboardButton]] = []
    for n in range(len(filters)):
        keyboard.append([InlineKeyboardButton(filters[n], callback_data=str(n))])

    await query.message.edit_text("Selecione o filtro:", reply_markup=InlineKeyboardMarkup(keyboard))

    return 4

async def filtering(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    driver: WebDriver = context.user_data["driver"]
    driver.find_element(By.XPATH, f"//button[@aria-label='Filtros de enquete']").click()
    WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.XPATH, f"//ytd-search-filter-renderer"))
    )[int(query.data)].find_element(By.ID, 'endpoint').click()

    await query.message.edit_text("Encontramos um vídeo para você!")
    return await get_result(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Use /start para começarmos!")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Volte sempre!"
    )

    return ConversationHandler.END

def main() -> None:

    application = Application.builder().token(os.environ['TOKEN']).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            1: [MessageHandler(filters.TEXT, typing)],
            2: [CallbackQueryHandler(searching)],
            3: [CallbackQueryHandler(asking_filter)],
            4: [CallbackQueryHandler(filtering)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))

    application.run_polling()


if __name__ == "__main__":
    main()

import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv
import asyncio

# Загружаем переменные окружения
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")

# Получаем URL Render из переменных окружения
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")
if RENDER_EXTERNAL_URL:
    WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}/webhook"
else:
    # Fallback для локальной разработки
    WEBHOOK_URL = None

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ========== ИНЛАЙН-КЛАВИАТУРЫ ==========

main_menu_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="👤 Об эксперте", callback_data="about")],
        [InlineKeyboardButton(text="📁 Портфолио", callback_data="portfolio")],
        [InlineKeyboardButton(text="💰 Услуги и цены", callback_data="services")],
        [InlineKeyboardButton(text="📝 Запись на консультацию", callback_data="consultation")],
        [InlineKeyboardButton(text="📞 Контакты", callback_data="contacts")],
    ]
)

back_to_menu_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu")]
    ]
)

# ========== СОСТОЯНИЯ ДЛЯ ФОРМЫ ЗАПИСИ ==========

class ConsultationForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_comment = State()

# ========== ОБРАБОТЧИКИ КОМАНД И КОЛБЭКОВ ==========

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = """
    👋 *Добро пожаловать!*

    Я — бот-визитка *Александры Чижовой* — эксперта в области маркетинга, основателя агентства Digital Octopus.

    🔥 *12 лет опыта* | *200+ проектов* | *ТОП-спикер*

    Выберите раздел, чтобы узнать больше:
    """
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=main_menu_inline)

@dp.message(Command("menu"))
async def cmd_menu(message: types.Message):
    welcome_text = """
    👋 *Главное меню*

    Выберите раздел:
    """
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=main_menu_inline)

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    welcome_text = """
    👋 *Главное меню*

    Выберите раздел:
    """
    await callback.message.edit_text(welcome_text, parse_mode="Markdown", reply_markup=main_menu_inline)
    await callback.answer()

# ----- РАЗДЕЛ "ОБ ЭКСПЕРТЕ" -----
@dp.callback_query(F.data == "about")
async def about_expert(callback: CallbackQuery):
    text = """
    *👤 Александра Чижова*

    🔸 *Основатель и CEO* агентства полного цикла *Digital Octopus*
    🔸 *Автор* бестселлеров «Маркетинг для дилетантов» и «Цифровой маркетинг»
    🔸 *Ведущий эксперт* в области digital-маркетинга с 12-летним опытом
    🔸 *Спикер* на ключевых отраслевых конференциях (РИФ, Digital Days и др.)
    🔸 Более 200 успешных запусков и масштабирований бизнесов в digital

    *Образование:* 
    - МГУ им. Ломоносова, факультет журналистики
    - Дополнительное образование: Coursera, Google Digital Academy

    *Награды:*
    🏆 «Маркетолог года» по версии Tagline Awards (2022)
    🏆 ТОП-5 digital-агентств России (по версии РА «Кубок Медиа»)

    Александра специализируется на комплексном продвижении бизнесов: от создания стратегии до запуска рекламных кампаний.
    """
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_to_menu_inline)
    await callback.answer()

# ----- РАЗДЕЛ "ПОРТФОЛИО" -----
@dp.callback_query(F.data == "portfolio")
async def portfolio(callback: CallbackQuery):
    text = """
    *📁 Портфолио и кейсы*

    Вот некоторые из реализованных проектов под руководством Александры:
    """
    
    portfolio_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Кейс: Запуск бренда косметики", callback_data="case_cosmetics")],
            [InlineKeyboardButton(text="Кейс: Рост e-commerce проекта", callback_data="case_ecommerce")],
            [InlineKeyboardButton(text="Видео-отзыв клиента", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")],
            [InlineKeyboardButton(text="Сайт агентства", url="https://digitaloctopus.ru/")],
            [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu")],
        ]
    )
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=portfolio_kb)
    await callback.answer()

@dp.callback_query(F.data.startswith("case_"))
async def show_case_detail(callback: CallbackQuery):
    case_data = callback.data
    if case_data == "case_cosmetics":
        text = """
        *Кейс: Запуск бренда органической косметики «Herbae»*

        🔹 *Задача:* Вывести новый бренд на рынок с нуля.
        🔹 *Срок:* 6 месяцев.
        🔹 *Действия:*
            - Разработана айдентика и УТП
            - Создан сайт и воронки продаж
            - Запущены таргетированная реклама и коллаборации с блогерами
        🔹 *Результат:* 
            - Оборот в первый месяц: 1.5 млн руб.
            - Рост аудитории в соцсетях: +15 000 подписчиков
            - ROI рекламы: 320%
        """
    elif case_data == "case_ecommerce":
        text = """
        *Кейс: Масштабирование e-commerce проекта «TechGadgets»*

        🔹 *Задача:* Увеличить месячную выручку на 200%.
        🔹 *Срок:* 4 месяца.
        🔹 *Действия:*
            - Проведен аудит рекламных кампаний
            - Переработана структура сайта и UX
            - Внедрена сквозная аналитика
            - Запущены кампании в Яндекс.Директ и Google Ads
        🔹 *Результат:*
            - Рост выручки: +240%
            - Снижение стоимости заказа на 35%
            - Увеличение LTV клиента на 50%
        """
    
    back_to_portfolio_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад к портфолио", callback_data="portfolio")],
            [InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_menu")],
        ]
    )
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_to_portfolio_kb)
    await callback.answer()

# ----- РАЗДЕЛ "УСЛУГИ И ЦЕНЫ" -----
@dp.callback_query(F.data == "services")
async def services_and_prices(callback: CallbackQuery):
    text = """
    *💰 Услуги и цены*

    💼 *Индивидуальная консультация* (1,5 часа)
    - Глубокий разбор вашего проекта
    - Аудит текущей маркетинговой стратегии
    - План действий на 3 месяца
    - *Стоимость:* 15 000 руб.

    🚀 *Стратегия продвижения* (полный пакет)
    - Анализ рынка и конкурентов
    - Разработка маркетинговой стратегии на 6-12 месяцев
    - Рекомендации по каналам продвижения и бюджетам
    - *Стоимость:* от 50 000 руб.

    🏢 *Ведение проекта* (подписка)
    - Ежемесячное сопровождение и корректировка стратегии
    - Контроль исполнителей (дизайнеры, таргетологи и др.)
    - Регулярные отчеты и планерки
    - *Стоимость:* от 80 000 руб./месяц

    *📌 Примечание:* Точная стоимость определяется после первичной беседы.
    """
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_to_menu_inline)
    await callback.answer()

# ----- РАЗДЕЛ "ЗАПИСЬ НА КОНСУЛЬТАЦИЮ" -----
@dp.callback_query(F.data == "consultation")
async def consultation_start(callback: CallbackQuery, state: FSMContext):
    text = """
    *📝 Запись на консультацию*

    Чтобы записаться на индивидуальную консультацию к Александре, заполните короткую форму.

    *Шаг 1 из 3:* Как к вам обращаться? (Введите ваше имя и фамилию)
    """
    await callback.message.edit_text(text, parse_mode="Markdown")
    await state.set_state(ConsultationForm.waiting_for_name)
    await callback.answer()

@dp.message(ConsultationForm.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("*Шаг 2 из 3:* Введите ваш номер телефона для связи:", parse_mode="Markdown")
    await state.set_state(ConsultationForm.waiting_for_phone)

@dp.message(ConsultationForm.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("*Шаг 3 из 3:* Опишите кратко ваш запрос или задайте вопрос (необязательно):", parse_mode="Markdown")
    await state.set_state(ConsultationForm.waiting_for_comment)

@dp.message(ConsultationForm.waiting_for_comment)
async def process_comment(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    request_text = (
        "*✅ Новая заявка на консультацию!*\n\n"
        f"*Имя:* {user_data['name']}\n"
        f"*Телефон:* {user_data['phone']}\n"
        f"*Комментарий:* {message.text if message.text else 'не указан'}\n"
        f"*От пользователя:* @{message.from_user.username or 'без username'}"
    )
    
    await message.answer(request_text, parse_mode="Markdown")
    
    final_text = """
    🎉 *Спасибо! Ваша заявка принята.*

    Александра или её ассистент свяжутся с вами в течение 24 часов для уточнения деталей.

    Что дальше?
    """
    
    after_form_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📅 Выбрать дату", callback_data="choose_time")],
            [InlineKeyboardButton(text="💬 Написать напрямую", url="https://t.me/chizhova_marketing")],
            [InlineKeyboardButton(text="⬅️ В главное меню", callback_data="back_to_menu")],
        ]
    )
    
    await message.answer(final_text, parse_mode="Markdown", reply_markup=after_form_kb)
    await state.clear()

# ----- РАЗДЕЛ "КОНТАКТЫ" -----
@dp.callback_query(F.data == "contacts")
async def contacts(callback: CallbackQuery):
    text = """
    *📞 Контакты и связь*

    *Александра Чижова*
    🔸 Основатель Digital Octopus
    🔸 Эксперт по маркетингу

    *Основные каналы связи:*
    📧 *Email:* a.chizhova@digitaloctopus.ru
    💬 *Личный Telegram:* @chizhova_marketing
    📸 *Instagram:* @chizhova_marketing

    *Офис агентства Digital Octopus:*
    📍 Москва, ул. Большая Дмитровка, 7/5 стр.1
    (встречи по предварительной договоренности)
    """
    
    contacts_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu")],
        ]
    )
    
    try:
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=contacts_kb)
    except Exception:
        await callback.message.answer(text, parse_mode="Markdown", reply_markup=contacts_kb)
    await callback.answer()

@dp.callback_query(F.data == "choose_time")
async def choose_time(callback: CallbackQuery):
    text = """
    *📅 Выбор времени консультации*

    К сожалению, функция онлайн-записи временно недоступна.

    Пожалуйста, напишите Александре напрямую в Telegram или отправьте email, чтобы согласовать удобное время.
    """
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Написать в Telegram", url="https://t.me/chizhova_marketing")],
            [InlineKeyboardButton(text="📧 Отправить email", url="mailto:a.chizhova@digitaloctopus.ru")],
            [InlineKeyboardButton(text="⬅️ В главное меню", callback_data="back_to_menu")],
        ]
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    await callback.answer()

@dp.message()
async def handle_text(message: types.Message):
    if message.text and not message.text.startswith('/'):
        await message.answer("Выберите раздел из меню:", reply_markup=main_menu_inline)

# ========== WEBHOOK НАСТРОЙКИ ==========

async def on_startup(bot: Bot):
    """Установка webhook при запуске"""
    if WEBHOOK_URL:
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url != WEBHOOK_URL:
            await bot.set_webhook(
                url=WEBHOOK_URL,
                drop_pending_updates=True
            )
            logger.info(f"Webhook установлен на {WEBHOOK_URL}")
        else:
            logger.info("Webhook уже установлен")
    else:
        logger.warning("WEBHOOK_URL не задан. Работаю в polling режиме.")

async def on_shutdown(bot: Bot):
    """Удаление webhook при остановке"""
    if WEBHOOK_URL:
        await bot.delete_webhook()
        logger.info("Webhook удален")

async def health_check(request):
    """Health check endpoint для Render"""
    return web.Response(text="OK", status=200)

async def handle_main(request):
    """Корневой endpoint"""
    return web.Response(text="Telegram Bot is running! Use /start in Telegram.", status=200)

# ========== ЗАПУСК ПРИЛОЖЕНИЯ ==========

async def main_webhook():
    """Запуск в режиме Webhook"""
    logger.info("Запуск бота в режиме Webhook...")
    
    # Регистрируем обработчики startup/shutdown
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Создаем aiohttp приложение
    app = web.Application()
    
    # Регистрируем health check и корневой endpoint
    app.router.add_get("/health", health_check)
    app.router.add_get("/", handle_main)
    
    # Создаем обработчик webhook
    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    
    # Регистрируем webhook endpoint
    webhook_handler.register(app, path="/webhook")
    
    # Настраиваем приложение aiogram
    setup_application(app, dp, bot=bot)
    
    # Получаем порт из переменной окружения
    port = int(os.environ.get("PORT", 10000))
    host = "0.0.0.0"
    
    logger.info(f"Запуск сервера на {host}:{port}")
    if WEBHOOK_URL:
        logger.info(f"Webhook URL: {WEBHOOK_URL}")
    
    print("=" * 50)
    print("Бот запущен в режиме Webhook!")
    print(f"Сервер запущен на {host}:{port}")
    if WEBHOOK_URL:
        print(f"Webhook URL: {WEBHOOK_URL}")
    print("=" * 50)
    
    # Запускаем сервер
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    
    # Бесконечный цикл
    await asyncio.Event().wait()

async def main_polling():
    """Запуск в режиме Polling (для локальной разработки)"""
    logger.info("Запуск бота в режиме Polling...")
    
    # Удаляем webhook перед запуском polling
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook удален, запускаем polling...")
    except Exception as e:
        logger.warning(f"Ошибка при удалении webhook: {e}")
    
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    try:
        # Если задан WEBHOOK_URL - запускаем в режиме webhook
        if WEBHOOK_URL:
            asyncio.run(main_webhook())
        else:
            # Иначе запускаем в режиме polling (для локальной разработки)
            asyncio.run(main_polling())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
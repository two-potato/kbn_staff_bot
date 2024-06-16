import asyncio
import logging
import logging.handlers
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from handlers import storage_checker
from os import getenv


TOKEN = "7438270511:AAHzG3xHVaAdvMIaPXtefHCqlrrRP2dshkM"
# TOKEN = getenv("TELEGRAM_TOKEN")
PAGE_SIZE = 5  # Количество товаров на одной странице


class RotatingFileHandlerWithLimit(logging.handlers.RotatingFileHandler):

    def __init__(self, filename, max_lines=3000, *args, **kwargs):
        super().__init__(filename, *args, **kwargs)
        self.max_lines = max_lines
        self.current_lines = 0

    def emit(self, record):
        if self.current_lines >= self.max_lines:
            self.doRollover()
        super().emit(record)
        self.current_lines += 1

    def doRollover(self):
        super().doRollover()


async def main() -> None:
    dp = Dispatcher()
    dp.include_router(storage_checker.router)
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    handler = RotatingFileHandlerWithLimit(
        "logs/bot.log", max_lines=3000, backupCount=1, encoding="utf-8"
    )
    logging.basicConfig(level=logging.INFO, handlers=[handler])
    asyncio.run(main())

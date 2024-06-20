# from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


# def main_kb(user_telegram_id: int):
# def main_kb():
#     kb_list = [
#         [KeyboardButton(text="📖 О нас"), KeyboardButton(text="👤 Профиль")],
#         [KeyboardButton(text="📝 Заполнить анкету"), KeyboardButton(text="📚 Каталог")],
#     ]
#     # if user_telegram_id in admins:
#     #     kb_list.append([KeyboardButton(text="⚙️ Админ панель")])
#     keyboard = ReplyKeyboardMarkup(
#         keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True
#     )
#     return keyboard

# from aiogram.types import BotCommand, BotCommandScopeDefault
# from bot import bot

# async def set_commands():
#     commands = [
#         BotCommand(command="start", description="Старт"),
#         BotCommand(command="start_2", description="Старт 2"),
#         BotCommand(command="start_3", description="Старт 3"),
#     ]
#     await bot.set_my_commands(commands, BotCommandScopeDefault())

import logging
from aiogram import Router, html, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from site_parser import parse_product_info, get_product_list_data
from keyboards.storage_checker_kb import (
    create_pagination_keyboard,
    create_product_info_buttons,
    create_product_link_button,
)

router = Router()
PAGE_SIZE = 5  # Количество товаров на одной странице


def create_product_info_message(result_data: dict) -> str:
    return (
        f"Арт: {result_data['art']}\n\n"
        f"{html.bold(result_data['title'])}\n\n"
        f"Бренд: {result_data['brand']}\n"
        f"Цена: {result_data['price']}\n"
        f"На складе: {result_data['stock_warehouse']}\n"
        f"В шоу-руме: {result_data['showroom_stock']}\n"
        f"На удаленном складе: {result_data['remote_warehouse']}\n"
    )


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}!\n "
        f"Я помогу тебе найти товар по названию или артикулу\n"
        f"Введите запрос для поиска."
    )


@router.message(F.text == "/map")
async def command_storage_handler(message: Message) -> None:
    await message.answer(
        f"Я помогу тебе найти товар по названию или артикулу\n"
        f"Введите запрос для поиска."
    )


@router.message()
async def handle_message(message: Message):
    search_query = message.text.strip()
    await message.reply(f"Ищу товар: {search_query}...")

    try:
        data = get_product_list_data(search_query)
        logging.info(f"Полученные данные (список): {data}")

        if not data:
            await message.answer("Товар не найден.")
            return

        if len(data) == 1:
            product = data[0]
            logging.info(f"Информация о продукте (словарь): {product}")

            result_data = parse_product_info(product["art"])
            print(f"-------------------->{result_data}")
            logging.info(f"Информация о продукте (словарь): {result_data}")

            required_keys = [
                "title",
                "brand",
                "price",
                "stock_warehouse",
                "showroom_stock",
                "remote_warehouse",
                "url",
                "art",
                "img",
            ]
            missing_keys = [key for key in required_keys if key not in result_data]
            if missing_keys:
                logging.warning(f"Отсутствующие ключи: {missing_keys}")
                await message.answer("Не удалось получить полную информацию о товаре.")
                return

            reply_message = create_product_info_message(result_data)
            reply_markup = create_product_link_button(result_data["url"])
            await message.answer_photo(
                photo=result_data["img"],
                reply_markup=reply_markup,
                caption=reply_message,
                parse_mode="HTML",
            )
        else:
            total_pages = (len(data) + PAGE_SIZE - 1) // PAGE_SIZE
            await send_paginated_list(message, data, 1, total_pages, search_query)

    except Exception as e:
        logging.error(f"Ошибка при разборе информации о продукте: {e}", exc_info=True)
        await message.answer(
            "Произошла ошибка при обработке запроса. Попробуйте позже."
        )


async def send_paginated_list(
    message: Message, data: list, page: int, total_pages: int, search_query: str
):
    start_index = (page - 1) * PAGE_SIZE
    end_index = start_index + PAGE_SIZE
    paginated_data = data[start_index:end_index]
    for obj in paginated_data:
        reply_message = (
            f"Арт:<b> {obj['art']}\n</b>" f"{obj['title']}\n" f"Цена: {obj['price']}\n"
        )
        reply_markup = create_product_info_buttons(
            obj["url"], f"show_count_{obj['art']}"
        )
        await message.answer_photo(
            caption=reply_message,
            photo=obj["img"],
            reply_markup=reply_markup,
            parse_mode="HTML",
        )
    if len(paginated_data) > 1:
        await message.answer(
            "Выберите страницу:",
            reply_markup=create_pagination_keyboard(page, total_pages, search_query),
        )


@router.callback_query(lambda c: c.data and c.data.startswith("page_"))
async def handle_pagination(callback_query: CallbackQuery):
    data_parts = callback_query.data.split("_")
    page = int(data_parts[1])
    search_query = "_".join(data_parts[2:])

    try:
        data = get_product_list_data(search_query)
        total_pages = (len(data) + PAGE_SIZE - 1) // PAGE_SIZE
        await send_paginated_list(
            callback_query.message, data, page, total_pages, search_query
        )
    except Exception as e:
        logging.error(f"Ошибка при разборе информации о продукте: {e}", exc_info=True)
        await callback_query.message.answer(
            "Произошла ошибка при обработке запроса. Попробуйте позже."
        )


@router.callback_query(lambda c: c.data and c.data.startswith("show_count_"))
async def handle_show_count(callback_query: CallbackQuery):
    art = callback_query.data.split("_")[2]
    await callback_query.message.answer("Уточняю количество...")

    try:
        result_data = parse_product_info(art)[0]
        count_message = create_product_info_message(result_data)
        await callback_query.message.reply(count_message)
    except Exception as e:
        logging.error(f"Ошибка при разборе информации о продукте: {e}", exc_info=True)
        await callback_query.message.answer(
            "Произошла ошибка при обработке запроса. Попробуйте позже."
        )

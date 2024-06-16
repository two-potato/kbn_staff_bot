from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_pagination_keyboard(
    page: int, total_pages: int, search_query: str
) -> InlineKeyboardMarkup:
    pagination_buttions_kb = InlineKeyboardBuilder()
    if page > 1:
        pagination_buttions_kb.add(
            InlineKeyboardButton(
                text="Предыдущая", callback_data=f"page_{page - 1}_{search_query}"
            )
        )
    if page < total_pages:
        pagination_buttions_kb.add(
            InlineKeyboardButton(
                text="Следующая", callback_data=f"page_{page + 1}_{search_query}"
            )
        )
    return pagination_buttions_kb.as_markup()


def create_product_info_buttons(url: str, callback_data) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Link", url=url))
    builder.add(InlineKeyboardButton(text="Количество", callback_data=callback_data))
    return builder.as_markup()


def create_product_link_button(url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Link", url=url))
    return builder.as_markup()

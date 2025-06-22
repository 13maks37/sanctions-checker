from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def generate_inline_keyboard(
    width: int, *args: str, **kwargs: str
) -> InlineKeyboardMarkup:
    """
    Keyboard generator function with parameter of number of buttons per line
    """
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    if args:
        for button in args:
            buttons.append(
                InlineKeyboardButton(
                    text=button,
                    callback_data=button,
                )
            )
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(
                InlineKeyboardButton(text=text, callback_data=button)
            )

    kb_builder.row(*buttons, width=width)
    return kb_builder.as_markup()

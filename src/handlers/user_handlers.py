import os
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, Document
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from src.db.operations import UserDAO
from src.keyboards.inline.keyboard import generate_inline_keyboard
from src.services.sanctions_scraper import scrape_sanctions_companies
from src.core.config import settings


router: Router = Router()


class FSMSanctionCompany(StatesGroup):
    wait_file = State()


# Handler on /start if user base allows use
@router.message(CommandStart())
async def start_handler(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
):
    await state.clear()
    existing_user = await UserDAO.get_by_tg_id(
        session=session,
        tg_id=message.from_user.id,
    )
    if existing_user:
        await message.answer(
            text="Main Menu",
            reply_markup=generate_inline_keyboard(
                1,
                **{"sanctions_company": "Company sanctions"},
            ),
        )
    else:
        await message.answer(
            text=(
                "This is a private bot. You are denied access to it. "
                "To gain access, write to the contact listed in /help."
            )
        )


# Handler on /menu if user base allows use
@router.message(Command(commands="menu"))
async def menu_handler(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
):
    await state.clear()
    existing_user = await UserDAO.get_by_tg_id(
        session=session,
        tg_id=message.from_user.id,
    )
    if existing_user:
        await message.answer(
            text="Main Menu",
            reply_markup=generate_inline_keyboard(
                1,
                **{"sanctions_company": "Company sanctions"},
            ),
        )
    else:
        await message.answer(
            text=(
                "This is a private bot. You are denied access to it. "
                "To gain access, write to the contact listed in /help."
            )
        )


# Handler on /help to call the navigation menu
@router.message(Command(commands="help"))
async def help_handler(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
):
    await state.clear()
    await message.answer("Tehnical support - @teenchain")


@router.callback_query(F.data == "sanctions_company")
async def sanctions_company(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        text=(
            "Paste the file with companies in <b>.xls or .xlsx</b> format and "
            "wait for the file with companies under sanctions to be received."
        )
    )
    await state.set_state(FSMSanctionCompany.wait_file)


@router.message(StateFilter(FSMSanctionCompany.wait_file))
async def process_file(message: Message, state: FSMContext, bot: Bot):
    document: Document = message.document
    if not document:
        await message.answer(
            "Please send a file in <b>.xls or .xlsx</b> format."
        )
        return
    file_name = document.file_name
    file_ext = os.path.splitext(file_name)[1].lower()
    if file_ext not in [".xls", ".xlsx"]:
        await message.answer(
            "Invalid file format. Only <b>.xls or .xlsx</b> accepted."
        )
        return
    os.makedirs(settings.TMP_DIR_BOT, exist_ok=True)
    unique_filename = f"{uuid4().hex}_{file_name}"
    file_path = f"{settings.TMP_DIR_BOT}/{unique_filename}"
    await message.bot.download(document, destination=file_path)
    await message.answer("The file has been received and is being processed.")
    await state.clear()
    await scrape_sanctions_companies(
        uploaded_file_path=file_path,
        chat_id=message.from_user.id,
        bot=bot,
    )

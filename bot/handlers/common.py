"""Common handlers."""
from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message()
async def echo_handler(message: Message):
    """Echo handler for unrecognized messages."""
    await message.answer(
        "🤖 Я получил ваше сообщение!\n\n"
        "Используйте /start для начала работы с ботом."
    )

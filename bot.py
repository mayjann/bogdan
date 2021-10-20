#!/usr/bin/env python3

import re
from asyncio import sleep
from os import mkdir, remove
from random import choice, randint

from aiofiles import open
from markovify import NewlineText
from vkbottle.bot import Bot, Message
from vkbottle.dispatch.rules.bot import ChatActionRule, FromUserRule


bot = Bot("054f02735c30f4cad2d4c99b9a8d03e0355d0cc51dba8169c221fdf2f8ea914d384ddcf4c5383a09f2819")


@bot.on.chat_message(ChatActionRule("chat_invite_user"))
async def invited(message: Message) -> None:
    """Приветствие при приглашении бота в беседу."""
    if message.group_id == -message.action.member_id:
        await message.answer(
            """чпок в пупок дяде нужны права админа дай дай дай"""
        )


@bot.on.chat_message(text=["/сброс", "/reset"])
async def reset(message: Message) -> None:
    """пока база данных...."""
    peer_id = message.peer_id
    try:
        members = await message.ctx_api.messages.get_conversation_members(
            peer_id=peer_id
        )
    except Exception:
        await message.answer(
            "Не удалось проверить, холоп ты или нет, "
            + "потому что я холоп без прав админа"
        )
        return
    admins = [member.member_id for member in members.items if member.is_admin]
    from_id = message.from_id
    if from_id in admins:

        try:
            remove(f"/sdcard/db/db.txt")
        except FileNotFoundError:
            pass

        await message.answer(f"@id{from_id}, база данных все...")
    else:
        await message.answer(
            "холопы не могут обнулять базу"
        )


@bot.on.chat_message(FromUserRule())
async def talk(message: Message) -> None:
    peer_id = message.peer_id
    text = message.text.lower()

    if text:
        while "\n\n" in text:
            text = text.replace("\n\n", "\n")

        user_ids = tuple(set(pattern.findall(text)))
        for user_id in user_ids:
            text = re.sub(rf"\[id{user_id}\|.*?]", f"@id{user_id}", text)
            
        try:
            mkdir("db")
        except FileExistsError:
            pass

        async with open(f"/sdcard/db/db.txt", "a") as f:
            await f.write(f"\n{text}")

    if randint(1, 100) > 25:
        return
    
    async with open(f"/sdcard/db/db.txt") as f:
        db = await f.read()
    db = db.strip().lower()

    await sleep(0)

    text_model = NewlineText(input_text=db, well_formed=False, state_size=1)
    sentence = text_model.make_sentence(tries=1000) or choice(db.splitlines())

    await message.answer(sentence)


if __name__ == "__main__":
    pattern = re.compile(r"\[id(\d*?)\|.*?]")
    bot.run_forever()

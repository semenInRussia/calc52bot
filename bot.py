import os
import asyncio, logging
import json
from sympy import symbols, Eq, solveset, Complexes

logging.basicConfig(level=logging.INFO)
from aiogram.filters.command import Command
from aiogram import Bot, Dispatcher, types, F

with open("token.txt", "r") as f:
    token = f.readline().strip()

bot = Bot(token=token)
disp = Dispatcher()


def _solve(a: list[float]):
    x = symbols("x")
    a.reverse()
    eq = 0
    for p, v in enumerate(a):
        eq += (x**p) * v

    return solveset(Eq(eq, 0), x)


def log(f):
    # wrapper which do logging

    async def w(msg: types.Message):
        logging.info(f"new message: {msg.text}")
        await f(msg)

    return w


banned = ["Biomeh_1729"]

OWNER_ID = "664167507"


def noban(f):
    # wrapper which checks ensure that user is not banned

    async def wrapped(msg: types.Message):
        if msg.from_user is None:
            await f(msg)
            return
        who = msg.from_user.username
        logging.info(f"new user {who} {' [banned]' if who in banned else ''}")
        if who in banned:
            logging.warning(f"id: {msg.chat.id}")
            await msg.answer("привет, ты забанен")
            if msg.text:
                await bot.send_message(OWNER_ID, msg.text)
        else:
            await f(msg)

    return wrapped


@disp.message(Command('start'))
@log
@noban
async def tg_start(msg: types.Message):
    await msg.answer("Привет я калькулятор 52")
    await msg.answer("Ты можешь ввсти уравнение вида:")
    await msg.answer("x^2 - 2x + 4")
    await msg.answer("В виде: ")
    await msg.answer("1 -2 4")
    await msg.answer("цель показать где бог")


async def send_file(msg: types.Message, path: str, **kwargs):
    await msg.answer_document(types.FSInputFile(path, **kwargs))


@disp.message(Command("code"))
@log
async def tg_code(msg: types.Message):
    if msg.from_user:
        logging.info(f"query for code: {msg.from_user.username}")
    await send_file(msg, __file__, filename="calc52bot.py")
    await send_file(msg, os.path.join(os.path.dirname(__file__), "cits.json"))


def is_num(s: str) -> bool:
    try:
        a = float(s)
    except ValueError:
        return False
    return True


def only_text(s: str) -> str:
    words = s.split(" ")
    # remove words which starts with @ or /
    for w in words:
        if w and w[0] in '/@':
            s = s.replace(w, "")
    return s.strip()


with open("cits.json", encoding="utf-8") as f:
    cits = json.loads(f.read())


def handle_cits(f):
    # wrapper which before run function answer with cits, if message have one key of citations

    async def w(msg: types.Message):
        logging.info("check cits")
        if not msg.text:
            await f(msg)
            return
        t = only_text(msg.text).lower().rstrip(".")
        if t in cits:
            logging.info("show cite")
            await msg.reply(cits[t])
        else:
            await f(msg)

    return w


@disp.message(Command("cits"))
@log
@noban
async def tg_cits(msg: types.Message):
    logging.info("give list of cits")
    await msg.answer(
        "Список ключей для цитат, просто напишите ключ, я дам цитату:")
    await msg.answer("\n- ".join([""] + list(cits.keys())))


LOX_ID = "5368391681"


@disp.message(Command("lox"))
@log
@noban
async def lox(msg: types.Message):
    # send message to lox
    if msg.text:
        logging.warning("message to lox was sent")
        await bot.send_message(LOX_ID, only_text(msg.text))
        await msg.answer("отправил")


@disp.message(F.text)
@disp.message(Command("calc"))
@log
@noban
@handle_cits
async def tg_solve(msg: types.Message):
    if not msg.text:
        return
    txt = only_text(msg.text)

    if not txt.strip():
        await msg.answer("ВВеди коэффициенты вашего МНогоЧлена")
        return
    if not all(map(is_num, txt.split())):
        await msg.answer(
            "Коэффициенты МНогоЧлена, это числа, возможно с точкой (не запятой)"
        )
        return

    nums = list(map(float, txt.split()))
    ans = _solve(nums)
    if not ans:
        await msg.answer("Нет корней, увы")
        return
    if ans == Complexes:
        await msg.answer("x - любое")
        return
    await msg.answer("Ыот:")
    for v in ans:  # type: ignore
        await msg.answer(str(v))


async def main():
    await disp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("bye!")

import logging

from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import executor

from db.db_commands import *
from load_bot import dp, bot

logging.basicConfig(level=logging.INFO)


class AddRawService(StatesGroup):
    waiting_raw_service_info = State()


class AddService(StatesGroup):
    waiting_add_service_name = State()
    waiting_add_service_prise_discount = State()


class ServicesList(StatesGroup):
    get_var = State()
    day_list = State()
    month_list = State()


class MoneyCounter(StatesGroup):
    get_var_money = State()
    get_money_for_month = State()
    get_money_for_current_month = State()


async def set_commands(bot: Bot):
    commands = [
        types.BotCommand(command="/raw_service", description="Добавить вид услуги"),
        types.BotCommand(command='/add', description='Добавить услугу'),
        types.BotCommand(command='/services_list', description='Список услуг'),
        types.BotCommand(command='/money_counter', description='Вывести ЗП'),
        # types.BotCommand(command='/other_commands', description='Доп. меню'),
        types.BotCommand(command='/cancel', description='Отменить действие'),
    ]
    await bot.set_my_commands(commands)


async def money_counter_start(message: types.Message):
    var = ['За текущий месяц', 'За другой месяц']
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*var)
    await MoneyCounter.get_var_money.set()
    await message.answer('За какй период интересует?', reply_markup=keyboard)


async def get_var_money(message: types.Message):
    var = message.text
    if var == 'За текущий месяц':
        res = get_money_for_month(
            id=message.from_user.id,
            month=date.today().month
        )
        await message.answer(f'З/П за текущий месяц: {res}р.')
    elif var == 'За другой месяц':
        await MoneyCounter.get_money_for_month.set()
        await message.answer('Впиши номер месяца')


async def get_money_month(message: types.Message):
    res = get_money_for_month(
        id=message.from_user.id,
        month=message.text
    )
    a = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
         'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    await message.answer(f'З/П за {a[(int(message.text) % 12) - 1]}: {res}р.')


async def services_list_start(message: types.Message):
    var_list = ['За день', 'За месяц', 'Последние 10 записей']
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*var_list)
    await ServicesList.get_var.set()
    await message.answer('Выбери вариант с клавиатуры', reply_markup=keyboard)


async def get_var_list(message: types.Message):
    var = message.text
    if var == 'За день':
        days = ['Сегодня', 'Вчера']
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(*days)
        await ServicesList.day_list.set()
        await message.answer('Выбери вариант с клавиатуры.', reply_markup=keyboard)
    elif var == 'За месяц':
        await ServicesList.month_list.set()
        await message.answer('Впиши номер месяца')
    elif var == 'Последние 10 записей':
        res = get_last_notes(id_employee=message.from_user.id)
        for row in res:
            await message.answer(
                f'Id: {row[0]}\n'
                f'Услуга: {row[1]}\n'
                f'Сумма на руки: {row[2]}\n'
                f'Скидка: {row[3]}\n'
                f'Дата: {row[4].strftime("%d.%m.%Y")}'
            )


async def day_list(message: types.Message, state: FSMContext):
    res = get_services_for_day(
        day=message.text,
        id_employee=message.from_user.id
    )
    for row in res:
        await message.answer(
            f'Id: {row[0]}\n'
            f'Услуга: {row[1]}\n'
            f'Сумма на руки: {row[2]}\n'
            f'Скидка: {row[3]}\n'
            f'Дата: {row[4].strftime("%d.%m.%Y")}'
        )
    await state.finish()


async def month_list(message: types.Message, state: FSMContext):
    res = get_services_for_month(
        num_month=int(message.text),
        id_employee=message.from_user.id
    )
    for row in res:
        await message.answer(
            f'Id: {row[0]}\n'
            f'Услуга: {row[1]}\n'
            f'Сумма на руки: {row[2]}\n'
            f'Скидка: {row[3]}\n'
            f'Дата: {row[4].strftime("%d.%m.%Y")}'
        )
    await state.finish()


async def add_service_start(message: types.Message):
    names = get_all_raw_services_name(message.from_user.id)
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=3)
    for name in names:
        keyboard.add(name)
    await AddService.waiting_add_service_name.set()
    await message.answer(
        'Выбери с клавиатуры что будем добавлять: ',
        reply_markup=keyboard
    )


async def add_service_name(message: types.Message, state: FSMContext):
    """Выбираем добовляемую оказанную услугу
        запоминаем название и переходим к след. стейту"""
    await state.update_data(service_name=message.text)
    await AddService.waiting_add_service_prise_discount.set()
    await message.answer('Введи стоймость и скидку(если нет - 0): \nПример: 2000 0')


async def add_service_other(message: types.Message, state: FSMContext):
    """Получаем оставшиеся данные и передаем их для сохранения в БД"""
    async with state.proxy() as data:
        data['price'] = message.text.split(' ')[0]
        data['discount'] = message.text.split(' ')[1]
        data['id_employee'] = message.from_user.id
    user_data = await state.get_data()
    add_complite_service(user_data)
    await message.reply('Добавлено')
    await state.finish()


async def add_raw_service_start(message: types.Message):
    await message.answer('Введите название услуги и получаемый процент: \nПример: Уход 40')
    await AddRawService.waiting_raw_service_info.set()


async def add_raw_service_info(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['service_name'] = message.text.rsplit(' ', 1)[0]  # Принимает название из любого кол-ва строк
        data['fix_percent'] = message.text.split(' ')[-1]
        data['id_employee'] = message.from_user.id
    print(f"name = {data['service_name']}\npercent = {data['fix_percent']}")
    user_data = await state.get_data()
    add_raw_service(user_data)
    await message.reply('Добавлено')
    await state.finish()


async def cmd_cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.answer("Действие отменено", reply_markup=types.ReplyKeyboardRemove())


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_cancel, commands='cancel', state='*')
    dp.register_message_handler(cmd_cancel, Text(equals="Отмена", ignore_case=True), state="*")


def register_services_list(dp: Dispatcher):
    dp.register_message_handler(services_list_start, commands='services_list', state='*')
    dp.register_message_handler(get_var_list, state=ServicesList.get_var)
    dp.register_message_handler(day_list, state=ServicesList.day_list)
    dp.register_message_handler(month_list, state=ServicesList.month_list)


def register_handlers_services(dp: Dispatcher):
    dp.register_message_handler(add_raw_service_start, commands='raw_service', state="*")
    dp.register_message_handler(add_raw_service_info, state=AddRawService.waiting_raw_service_info)
    dp.register_message_handler(add_service_start, commands='add', state="*")
    dp.register_message_handler(add_service_name, state=AddService.waiting_add_service_name)
    dp.register_message_handler(add_service_other, state=AddService.waiting_add_service_prise_discount)


def register_money_counter(dp: Dispatcher):
    dp.register_message_handler(money_counter_start, commands='money_counter', state='*')
    dp.register_message_handler(get_var_money, state=MoneyCounter.get_var_money)
    dp.register_message_handler(get_money_month, state=MoneyCounter.get_money_for_month)


async def main(dp):
    register_handlers_common(dp)
    register_handlers_services(dp)
    register_services_list(dp)
    register_money_counter(dp)
    await set_commands(bot)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=main, skip_updates=True)

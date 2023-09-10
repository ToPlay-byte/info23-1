from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pytz


"""Токен бота."""
bot_token = '6394112244:AAEQKMH0Ho-piL8G4eM8LfSoB2nCutvC4_M'
"""Переменная, отвечающая за самого бота."""
bot = Bot(token=bot_token)
"""Диспетчер(Как я понял, позволяет реагировать боту на какие-то события)."""
dp = Dispatcher(bot)
"""Заголовки запросов."""
headers = {
    'Cookie': 'advanced-frontend=g5hausd80fkk4svcl3qhpatqfi; _csrf-frontend=77f228fbecb4e8b718a' 
              'f121ced7f1bf1fffee536ef5586d5fc708d03f8fc6033a%3A2%3A%7Bi%3A0%3Bs%3A14%3A%22' 
              '_csrf-frontend%22%3Bi%3A1%3Bs%3A32%3A%22FMHFOdn0a9QsJWBvoPerk5zI7mTQRPE6%22%3B%7D',
}

form_data = {
    'TimeTableForm[structureId]': '0',
    'TimeTableForm[course]': '1',
    'TimeTableForm[groupId]': '2490',
    'TimeTableForm[facultyId]': '1',
    'date-picker': '0.0.0+-+04.09.2023',
    'TimeTableForm[dateStart]': '0.0.0',
    'TimeTableForm[dateEnd]': '0.0.0',
    'TimeTableForm[indicationDays]': '5',
    'time-table-type': '1',
    '_csrf-frontend': 'gIdU7Cx2Swh1w-h78N30aGQ0C6z8pcnkB-qS-LSaVwfGyhyqYxIlOBT6uQi6irYeC2Ru3peQs60wh8ap5soSMQ=='

}
"""Список дней недели. Они указаны последовательно в 6 вложеных массивах начиная с понедельника и заканчивая субботой.
Внутри этих вложеных массивов находятся 3 разных варианта написания команды за конкретный день недели
(первые 2 - это на украинском и русском языках соответственно, третий - краткий вариант."""
weak_word_lists = [
    ['/суббота', '/субота', '/сб'],
    ['/понедельник', '/понеділок', '/пн'],
    ['/вторник', '/вівторок', '/вт'],
    ['/среда', '/середа', '/ср'],
    ['/четверг', '/четверг', '/чт'],
    ['/пятница', '/п\'ятниця', '/пт']
]

"""Нужно для того, чтобы выводить нужный день."""
needeble_day = 0
"""Группа, по которой будет происходить поиск. Указывается лишь номер группы,
 буква не нужна, может лишь помешать поиску."""
current_group = "407"


def get_date():
    """Получаем  нужную дату для отображения расписания"""
    week = datetime.now(pytz.timezone('Europe/Kyiv')).isocalendar().week
    year = datetime.today().year
    date = datetime.strptime(f'{year}, {week}, {needeble_day}', '%Y, %W, %w').strftime('%d.%m.%Y')
    return date


def get_request():
    """Получаем запрос на строницу с расписанием"""
    global form_data
    # Изменяем форму для запроса на страницу
    form_data['date-picker'] = f'{get_date()}+-+{get_date()}'
    form_data['TimeTableForm[dateStart]'] = f'{get_date()}'
    form_data['TimeTableForm[dateEnd]'] = f'{get_date()}'
    req = requests.post(url='https://asu.dpu.edu.ua/time-table/group?type=0', data=form_data, headers=headers)
    return req


def check_weak_day_input_in_message(message):
    """Эта функция проверяет, что ввёл пользователь. Для этого его сообщение будет проверяться
    в функции find_weak_day_in_message(). Если всё таки выйдет, что такой день недели будет найден,
    то тогда в переменную needeble_day(нужный день недели) указывает индекс нужного дня
    для дальнейшего вывода расписания занятий и вернёт True. А если не выйдет,
    то полностью пройдётся по циклу и вернёт False.

Принимает:
- message(сообщение, которое пользователь ввёл).

Возвращает одно из двух значений:
- True, если найден день недели, который ввёл пользователь;
- False, если не найден день недели, который ввёл пользователь."""
    global needeble_day
    for i in range(0, 6):
        if find_weak_day_in_message(message, i):
            needeble_day = i
            return True
    return False


def find_weak_day_in_message(message, current_weak_number):
    """Эта функция проверяет, соответствует ли указаный пользователем в сообщении день недели с тем,
     номер которого указан в качестве переменной current_weak_number. Если да, возвращает True, иначе False.

Принимает:
- message(сообщение, которое пользователь ввёл), current_weak_number(индекс дня недели в масиве weak_word_lists).

Возвращает одно из двух значений:
- True, если найден нужный день недели;
- False, если не найден нужный день недели."""
    current_weak_word_list = weak_word_lists[current_weak_number]
    for current_word in current_weak_word_list:
        if current_word == message.text.lower():
            return True
    return False


async def get_data():
    data = {}
    req = get_request()
    soap = BeautifulSoup(req.content, 'html.parser')
    table = soap.find('table', id='timeTable')
    # Находим рядки, которые имеют информацию о расписании
    find_lessons = table.find_all('div', class_='cell')
    # Получаем  их
    rows = [item.find_parent('tr') for item in find_lessons if item.text.strip()]
    for row in rows:
        if row:
            name = row.find('span', class_='lesson').text
            data[name] = {}
            data[name]['time'] = {
                'start': row.find('span', class_='start').text,
                'end': row.find('span', class_='end').text
            }
            data[name]['lesson'] = row.find('div', class_='cell').div.div.text.replace('\n', ' ').lstrip()
    return data


@dp.message_handler(commands='start')
async def _start(message):
    """ Приём сообщения для старта бота. Сам бот после активации выводит приветствие
     и предлагает отправить сообщение "/расписание занятий".

Принимает:
- message(сообщение, которое ввёл пользователь)."""
    first_selection = KeyboardButton('/расписание занятий')
    list_selection = ReplyKeyboardMarkup()
    list_selection.add(first_selection)
    await bot.send_message(message.chat.id, "Привіт!", reply_markup=list_selection)


timetable_of_lessons_syntax = ['/расписание занятий', '/розклад занять',
                               '/расписание', '/розклад']
"""Массив, который содержит 4 разных варианта написания команды, чтобы активировать функцию _week()."""


def check_right_input_timetable_of_lessons(message):
    """Проверяет, правильно ли введена команда для вывода Telegram-кнопок пользователю.

Сама функция создаёт переменную message_text, которая принимает текст сообщения пользователя в низком регистре.
 После идёт проверка, соответствует ли значение этой переменной хотя бы одному
  из элементов массива timetable_of_lessons_syntax.
  Если да, то возвращает True, иначе False.

Принимает:
- message(сообщение, которое ввёл пользователь).

Возвращает одно из двух:
- True, если пользователь ввёл правильную команду;
- False, если пользователь ввёл неправильную команду."""
    message_text = message.text.lower()
    for i in timetable_of_lessons_syntax:
        if message_text == i:
            return True
    return False


@dp.message_handler(lambda message: check_right_input_timetable_of_lessons(message))
async def _week(message):
    """Приём сообщения для вывода кнопок, чтобы отдавать команды боту не с помощью написания их с клавиатуры,
     а через специальные кнопки Telegram.

Принимает:
- message(сообщение, которое ввёл пользователь)."""
    days_list = [KeyboardButton(weak_word_lists[0][1]), KeyboardButton(weak_word_lists[1][1]),
                 KeyboardButton(weak_word_lists[2][1]), KeyboardButton(weak_word_lists[3][0]),
                 KeyboardButton(weak_word_lists[4][1]), KeyboardButton(weak_word_lists[5][1])]

    days = (ReplyKeyboardMarkup().add(days_list[0],
                                      days_list[1],
                                      days_list[2],
                                      days_list[3],
                                      days_list[4],
                                      days_list[5]))

    await bot.send_message(message.chat.id, 'Виберіть день тижня:', reply_markup=days)


async def weak_day_lessons_construct(message, current_weak_number):
    """Предназначен для создания списка занятий за конкретный день недели и последующего вывода сообщения
     о нём пользователю. Внутри описан этот процесс.

Принимает:
- message(сообщение, которое ввёл пользователь);
- current_weak_number(номер конкретного дня недели)"""
    # Отправляем сообщение, которое предупреждает пользователя, что мы обрабатываем данные со страницы
    # за какой-то день недели.
    message_text = await bot.send_message(chat_id=message.chat.id,
                                          text='Отримуємо дані...')
    # Создаём переменную lessons и присваиваем ей значение результата выполнения функции data(), в качестве
    # параметров передаём ссылку на нужный день недели.
    lessons = await get_data()
    # Удаляет сообщение, которое предупреждало пользователя об обработке данных.
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message_text.message_id)
    if lessons:
        text_to_send = f'Розклад на {get_date()}. \n'
        for lesson, description in lessons.items():
            time = description['time']
            text_to_send += f'{lesson}. {description["lesson"]} {time["start"]}-{time["end"]}\n'
    else:
        text_to_send = 'Немає пар'

    await bot.send_message(chat_id=message.chat.id,text=text_to_send)


@dp.message_handler(lambda message: check_weak_day_input_in_message(message))
async def output_weak_day_lessons(message):
    """Начинает процесс вывода расписания занятий, если пользователь ввёл правильную команду.

Принимает:
- message(сообщение, которое ввёл пользователь)."""
    # Если всё окей, то запускает цепочку функций, которые выводят сообщение.
    await weak_day_lessons_construct(message, needeble_day)


@dp.message_handler(lambda message: message.text.lower() == 'русский военный корабль')
async def warschip(message):
    """Чёткий и ясный ответ на всеми известную фразу.

Принимает:
- message(сообщение, которое ввёл пользователь)."""
    await bot.send_message(message.chat.id, 'иди на хуй')


# Проверяем нормально ли всё со скриптом.
if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # # loop.create_task(checkUp())

    # Запускаем бота в long-polling режиме.
    executor.start_polling(dp, skip_updates=True)

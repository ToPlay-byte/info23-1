
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bs4 import BeautifulSoup
import aiohttp

bot_token = '5194007208:AAGrNcr154AqweZVbLgCfA65q69hcujvt6w'
"""Токен бота."""
bot = Bot(token=bot_token)
"""Переменная, отвечающая за самого бота."""
dp = Dispatcher(bot)
"""Диспетчер(Как я понял, позволяет реагировать боту на какие-то события)."""
url = [
    'https://docs.google.com/spreadsheets/d/e/2PACX-1vTl4XRsk2pxPAAumyB'
    '-0l2au3dkO7jC1PDeaTvctjBBU9HOpXyYwapoE_1PNlZsjrFDKFrpj-HK3oDK/pubhtml# ',
    'https://docs.google.com/spreadsheets/d/e/2PACX-1vQNDy6kP_Er32th8XuYpJRKI26iFJiauYR7IY7L'
    '-Kqfhu_SYYLUs3hg1MSzWHw2bglOLhwcXgYBiwJD/pubhtml#',
    'https://docs.google.com/spreadsheets/d/e/2PACX-1vRpSkr059jyQUZv7HPp813kYED2fmigy14J8fThJ1Eo'
    '-6sEixrsjCezT281QCs0eMXBw4oSBoIFqhGM/pubhtml',
    'https://docs.google.com/spreadsheets/d/e/2PACX-1vRDA31eofItYZ5nQWwfvF26yq8Snig-oGbtdisOuAm2Ur0-v1h'
    '-Qwdmh3-eT3nQGRKW1e7D7KQ2UjUq/pubhtml',
    'https://docs.google.com/spreadsheets/d/e/2PACX'
    '-1vTwv0DHzrT97qJvh7lBovx6BubKJIO_gk_Lesgyn22RlxMclC3z1OW6TKJDhFe1CBJ6fGDSUcciZXzX/pubhtml# ',
    'https://docs.google.com/spreadsheets/d/e/2PACX'
    '-1vScVScHS0fxSDzdeJwVFgTXo0mSfgZ-Z65KzCLc1bcsX-73tI4UW4Fie8CMpCMVdTD34JNNoM0-oN-7/pubhtml#'
]
"""Ссылки на нужные страницы в Google Sheets."""

headers = {
    'registration-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 '
                          'Safari/537.36 '
}
"""Заголовки запросов."""

weak_word_lists = [['/понедельник', '/понеділок', '/пн'],
                   ['/вторник', '/вівторок', '/вт'],
                   ['/среда', '/середа', '/ср'],
                   ['/четверг', '/четверг', '/чт'],
                   ['/пятница', '/п\'ятниця', '/пт'],
                   ['/суббота', '/субота', '/сб']]
"""Список дней недели. Они указаны последовательно в 6 вложеных массивах начиная с понедельника и заканчивая субботой.
Внутри этих вложеных массивов находятся 3 разных варианта написания команды за конкретный день недели(первые 2 - это на украинском и русском языках соответственно, третий - краткий вариант."""

needeble_day = 0
"""Нужно для того, чтобы выводить нужный день."""

current_group = "407"
"""Группа, по которой будет происходить поиск. Указывается лишь номер группы, буква не нужна, может лишь помешать поиску."""


changes_text = """Зміни бота в останніх версії:
- Проведено рефакторинг коду. Це покращить читабельність коду для його розробників;
- Виправлені помилки, пов'язані із некорректним виведенням розкладу занять;
- Додано відправлення повідомленя, яке попереджає користувача про те, що бот оброблює інформацію із Google Sheets, через що просить його почекати і повідомляє, що повідомлення-попередження видалиться відразу після обробки, а розклад занять відправиться новим повідомленням.
- Тепер бот конкретно вказує, яка помилка у нього виникла при обробці даних.

Зміни в минулих версіях:
- Виправлення помилок та доробки бота.

Версія бота: не встановлено."""
"""Текст для ответа пользователям на запрос об изменениях в боте. Желательно новые изменения указывать здесь."""

def check_weak_day_input_in_message(message):
    """Эта функция проверяет, что ввёл пользователь. Для этого его сообщение будет проверяться в функции find_weak_day_in_message(). Если всё таки выйдет, что такой день недели будет найден, то тогда в переменную needeble_day(нужный день недели) указывает индекс нужного дня для дальнейшего вывода расписания занятий и вернёт True. А если не выйдет, то полностью пройдётся по циклу и вернёт False.

Принимает: 
- message(сообщение, которое пользователь ввёл).

Возвращает одно из двух значений:
- True, если найден день недели, который ввёл пользователь;
- False, если не найден день недели, который ввёл пользователь."""
    global needeble_day
    for i in range(0, 6):
        if(find_weak_day_in_message(message, i) == True):
            needeble_day = i
            return True
    return False

def find_weak_day_in_message(message, current_weak_number):
    """Эта функция проверяет, соответствует ли указаный пользователем в сообщении день недели с тем, номер которого указан в качестве переменной current_weak_number. Если да, возвращает True, иначе False.

Принимает: 
- message(сообщение, которое пользователь ввёл), current_weak_number(индекс дня недели в масиве weak_word_lists).

Возвращает одно из двух значений:
- True, если найден нужный день недели;
- False, если не найден нужный день недели."""
    current_weak_word_list = weak_word_lists[current_weak_number]
    for current_word in current_weak_word_list:
        if(current_word == message.text.lower()):
            return True
    return False 
def find_lessons(soup):
    """Эта функция проходится по переменной soup(HTML-элемент, который содержит элементы таблицы, в которой находятся сами пары), где отображаются пары и вписывает их в переменную  list_of_lessons(список аудиторий).

Описание процесса: 
    Для начала создаём переменные: 
- list_of_lessons(отвечет за список занятий. Нужна для вывода списка занятий боту и отправки пользователю);
- n(отвечет за номер текущего занятия. Нужна, чтобы вставлять пары двух групп по порядку(чтобы в будущем просмотреть будет лекция, практика или не будет пары));
- group_was_found(отвечет за то, нашли мы нужную группу или нет. Поможет в будущем обработать эту ошибку).

    Дальше проходимся по HTML-элементам tr и ищем занятия, но сначала проводим поиск названия нужной группы. Если нашло, то пропускаем итерацию и разрешаем пройтись по ячейкам занятий в таблице, а если нет, то ищем дальше. После успешного нахождения, мы добавляем при каждой итерации новый вложеный массив, который будет отвечать за один или пару элементов, которые представляют значение занятий в ячейках таблицы на странице. Дальше прибавляем к значению переменной n число 1 и проходимся по HTML-элементам td. Если текущий элемент - это номер пары, то пропускаем итерацию. После идут проверки на неправильность оформления Google Sheets. Если предыдущий элемент и текущий не имеют атрибута colspan, то проверяем, является ли пребедущий элемент просто номером пары. Если да, то пропускаем итерацию, а если нет, то указываем, что текущая пара отсутствует. Если это последняя ячейка и она неправильно оформленая и наш массив неполный(то есть, там уже нету 2 обозначений пар), то указываем, что пара отсутствует. И последняя проверка на неправильность оформления - есть ли у текущей ячейки аргумент colspan. Если есть, то указываем, что пара отсутствует. Теперь проверка на то, сейчас лекция или практика. Если аргумент colspan = 2, значит практика. Если 4, то лекция. После выполнения прошлого обхода, проверяем, заполнился ли масив. Если да, то выходим из цикла. Если нет, то идём по другому ряду. Если у нас после процесса поиска нужной группы окажется, что её нету, то переменная group_was_found будет равна False, а это значит, что условие в конце функции будет истинное, что приведёт к тому, что вывод будет ["Current group not found"]. Этот вывод даст знать боту, что нужно сказать, что или на сайте ошибка оформления групп, или просто не составили расписание нужной группе, в следствии чего бот выведет это.

Принимает:
- soup(HTML-элемент, который содержит элементы таблицы, в которой находятся сами пары).

Возвращает одно из двух:
- list_of_lessons(список аудиторий), lessons_max_count(максимальное количество занятий);
- ValueError("Group not found")(если процесс поиск групп окажется провальным), lessons_max_count(максимальное количество занятий)."""
    list_of_lessons = []
    n = -1
    group_was_found = False
    lessons_max_count = -1
    
    for g in soup.find_all('tr'):
        if(g.find('td', attrs={"colspan":"2"}) != None):
            if(g.find('td', attrs={"colspan":"2"}).get_text().find(current_group) >= 0):
                group_was_found = True
                continue
            else:
                if(group_was_found == False):
                    continue
        else:
            if(group_was_found == False):
                continue
        
        list_of_lessons.append([])
        
        n += 1
        for j in g.find_all('td'):
            if(j == g.find("td")):
                if(j.get_text() == ""):
                    lessons_max_count = (int)(((g.find_previous("tr")).find("td")).get_text())
                    list_of_lessons.remove([])
                    n -= 1
                    break
                if(j.get_text() == ((g.find_previous("tr")).find("td")).get_text()):
                    lessons_max_count = (int)(((g.find_previous("tr")).find("td")).get_text())
                    list_of_lessons.remove([])
                    n -= 1
                    break
                continue
            if(j.find_previous("td").get("colspan") == None and j.get("colspan") == None):
                if(j.find_previous("td") == g.find("td")):
                    continue
                else:
                    list_of_lessons[n].append(None)
            if(j.next_element == None and j.get("colspan" == None) and j.find_previous("td").get("colspan") == None):
                if(len(list_of_lessons[n])<2):
                    list_of_lessons[n].append(None)
                continue
            if(j.get("colspan" == None)):
                list_of_lessons[n].append(None)
                continue
            if (j.get("colspan") in ["2","4"]):
                list_of_lessons[n].append(j)
                if(j.get("colspan") == "4" or len(list_of_lessons[n]) == 2):
                    break
        if(len(list_of_lessons[n]) == 1 and list_of_lessons[n][0].get("colspan") == "2"):
            list_of_lessons[n].append(None)
            
        if (len(list_of_lessons) == lessons_max_count):
            break
    if (group_was_found == False):
        return ValueError("Group not found"), lessons_max_count
    return list_of_lessons, lessons_max_count

def find_lessons_audits(soup_audits):
    """Эта функция проходится по переменной soup_audits(HTML-элемент, который содержит элементы таблицы, в которой находятся сами аудитории), где отображаются аудитории и вписывает их в переменную list_of_lessons_audiences(список аудиторий)

Описание процесса: 
    Создаём переменную, проходимся по HTML-элементам tr и ищем аудитории. Если нашло назнание нашей группы, то пропускаем итерацию, если нашло не пустую аудиторию, то вписываем её полностью(пример: " (Аудиторія 46)"), а если нашло пустую, то вписываем простую строку, что даст нам понять, что занятие онлайн или просто не указали аудиторию.

Принимает: 
- soup_audits(HTML-элемент, который содержит элементы таблицы, в которой находятся сами аудитории. Там должны быть tr и td элементы, чтобы поиск прошёл успешно).

Возвращает: 
- list_of_lessons_audiences(список аудиторий)."""
    list_of_lessons_audiences = []
        
    for g in soup_audits.find_all('tr'):
        if(g.find("td").get_text().find(current_group) >= 0):
            for j in g.find_all('td'):
                if(j.get_text().find(current_group) >= 0):
                    continue
                if(len(j.get_text().replace(" ", "")) == 0 or j.get_text() == "-"):
                    list_of_lessons_audiences.append("")
                else:
                    list_of_lessons_audiences.append(f" (Аудиторія {j.get_text()})")

        if(len(list_of_lessons_audiences) == 6):
            break
    
    return list_of_lessons_audiences

def find_lecture_or_practice(list_of_lessons, list_of_lessons_audiences):
    """Эта функция проходится по переменным list_of_lessons(список пар) и list_of_lessons_audiences(список аудиторий) и добавляет в локальную переменную lessons значение, которое говорит, пара, которую сейчас расматривает цикл, должна быть практикой, лекцией или её вообще не должно быть.

Принимает:
- list_of_lessons(список пар)
- list_of_lessons_audiences(список аудиторий).

Возвращает:
- lessons(расписание)."""
    lessons = []
    for g in range(0, len(list_of_lessons)):
        # Кратко говоря, если у обеих групп не совместная пара.
        if(len(list_of_lessons[g]) == 2):
            # Если на Google Sheets оказалось, что ни у какой группы не оформлено правильно расписание, то тогда:
            if(list_of_lessons[g][0] == None and list_of_lessons[g][1] == None):
                # добавить в занятия, что пары нету;
                lessons.append("[Відсутня пара]")
                # пропустить текущую итерацию.
                continue
            # Если на Google Sheets оказалось, что у паралельной группе не правильно оформленно расписание...
            if((list_of_lessons[g][0] != None and list_of_lessons[g][1] == None)):
                #...и у нашей группе есть какая-то пара, то тогда:
                if(len(list_of_lessons[g][0].get_text().replace(" ", "")) != 0 and list_of_lessons[g][0].get_text() != "-"):
                    # добавить в занятия, что у нас есть практическое занятие;
                    lessons.append(list_of_lessons[g][0].get_text() + f" [Практика]{list_of_lessons_audiences[g]}")
                    # пропустить текущую итерацию;
                    continue
                #...и у нашей группы нету пар, то тогда:
                else:
                    # добавить в занятия, что у нас нету пары.
                    lessons.append("[Відсутня пара]")
            # Если на Google Sheets оказалось, что у всех группах всё оформлено правильно...
            if((list_of_lessons[g][0] != None and list_of_lessons[g][1] != None)):
                # ...и у нас есть какая-то пара, то тогда:
                if(len(list_of_lessons[g][0].get_text().replace(" ", "")) != 0 and list_of_lessons[g][0].get_text() != "-"):
                    # добавить в расписания, что у нас есть практическое занятие;
                    lessons.append(list_of_lessons[g][0].get_text() + f" [Практика]{list_of_lessons_audiences[g]}")
                    # пропустить текущую итерацию
                    continue
                # ...и у нас нету пары...
                elif(len(list_of_lessons[g][0].get_text().replace(" ", "")) == 0 or list_of_lessons[g][0].get_text() == "-"):
                    # ... а у паралельной группы есть пара, то тогда:
                    if(len(list_of_lessons[g][1].get_text().replace(" ", "")) != 0 and list_of_lessons[g][1].get_text() != "-"):
                        # добавить в расписания, что у нас пары нету, но у паралельной группы есть;
                        lessons.append(f"[Відсутня пара(але не у {(int)(current_group)+1} групі)]")
                        # пропустить текущую итерацию.
                        continue
                    # ... и у паралельной группы тоже, то тогда:
                    elif(len(list_of_lessons[g][1].get_text().replace(" ", "")) == 0 or list_of_lessons[g][1].get_text() == "-"):
                        # добавить в расписания, что у нас нету пары;
                        lessons.append("[Відсутня пара]")
                        # пропустить текущую итерацию.
                        continue
            # Если на Google Sheets оказалось, что у нашей группе не правильно оформленно расписание...
            if(list_of_lessons[g][0] == None and list_of_lessons[g][1] != None):
                # ...и у паралельной группе есть какая-то пара, то тогда:
                if(len(list_of_lessons[g][1].get_text().replace(" ", "")) != 0 and list_of_lessons[g][1].get_text() != "-"):
                    # добавить в расписания, что у нас нету пары, а у паралельной группы есть;
                    lessons.append(f"[Відсутня пара(але не у {(int)(current_group)+1} групі)]")
                    # пропустить текущую итерацию.
                    continue
                # ...и у паралельной группе нету пары, то тогда:
                else:
                    # добавить в расписания, что у нас нету пары;
                    lessons.append("[Відсутня пара]")
                    # пропустить текущую итерацию.
                    continue
        # Кратко говоря, если у обеих групп совместная пара.
        if(len(list_of_lessons[g]) == 1):
            # Если ячейка пары пустая(в плане, там ничего нету), то тогда:
            if(list_of_lessons[g][0] == None):
                # добавить в расписания, что пары нету.
                lessons.append("[Відсутня пара]")
            # А если непустая...
            else:
                # ...и если там что-то написано...
                if(len(list_of_lessons[g][0].get_text().replace(" ", "")) != 0 and list_of_lessons[g][0].get_text() != "-"):
                    # ...добавить в расписания, что у нас будет лекция.
                    lessons.append(list_of_lessons[g][0].get_text() + f" [Лекція]{list_of_lessons_audiences[g]}")
                # ...и если там пусто...
                else:
                    lessons.append("[Відсутня пара]")
    
    return lessons

async def data(link):
    """ По ссылке, которая передаётся в качестве аргумента, происходит поиск на странице Google Sheets нужного дня недели, занятий и их аудиторий. Внутри функции это всё задокументировано.
    
Принимает: 
- link(ссылка на страницу Google Sheets).

Возвращает одно из 4 значений:
- lessons(список занятий) в случае, если все занятия были найдены успешно;
- ValueError("Lessons count")(ошибка, которая гласит, что количество занятий в переменной и количество занятий в списке lessons не сходятся);
- TypeError("Unknown type of list_of_lessons")(ошибка, которая гласит, что list_of_lessons имеет тип, который не удалось обработать);
- list_of_lessons, которое имеет значение ValueError("Group not found")(ошибка, которая гласит, что группа, которая указаная в переменной current_group, не была найдена)."""
    # Получение ответа от страницы.
    async with aiohttp.ClientSession() as session:
        async with session.request("get",link,headers=headers) as response_temp:
            response = await response_temp.text()
            # Получаем HTML-элементы, которые относятся к элементам таблицы, в которых находятся нужные пары.
            soup =  BeautifulSoup(response, 'html.parser').find('div', id='1778922595') \
                .find('div', class_="grid-container").find('table', class_='waffle').find('tbody')
            # Получаем HTML-элементы, которые относятся к элементам таблицы, в которых находятся нужные аудитории.
            soup_audits =  BeautifulSoup(response, 'html.parser').find('div', id='436522941') \
                .find('div', class_="grid-container").find('table', class_='waffle').find('tbody')
    
    
    # Создаём переменную list_of_lessons(список пар) и присваиваем ей значение результата выполнения
    # функции find_lessons(), которая в качестве аргумента принимает переменную soup.
    list_of_lessons, lessons_max_count = find_lessons(soup)
    # Чтобы не тянуть время, сначала проверим, является ли тип list_of_lessons списком.
    # Если да, то...
    if(type(list_of_lessons) is list):
        # ...то тогда:
        # - Проверим сразу, нету ли у нас ошибки с количеством расписаний.
        # Если каким-то чудом вышло, что у нас не полное расписание...
        if(len(list_of_lessons)+1 <= lessons_max_count):
            # ... то тогда вместо сообщения бота возвращаем ValueError, с аргументом "Lessons count"
            # чтобы было понятно, что произошла ошибка количества занятий и это нужно отправить пользователю.
            return ValueError("Lessons count")
    # В противном случае, если тип переменной list_of_lessons - это ValueError...
    elif(type(list_of_lessons) is ValueError):
        # ...то тогда вернём эту переменную с типом ValueError, которая уже имеет аргумент со значением "Group not found",
        # что поможет боту определить ошибку и вывести её пользователю.
        return list_of_lessons
    # Ну а если list_of_lessons это не list и не ValueError...
    else:
        # ...то тогда уведомляем пользователя, что у нас неизвестный тип переменной list_of_lessons.
        # В качестве агрумента укажем, что тип list_of_lessons неизвестный.
        return TypeError("Unknown type of list_of_lessons")
    
    # Создаём переменную list_of_lessons_audiences(список аудиторий) и присваиваем ей значение результата выполнения
    # функции find_lessons_audits(), которая в качестве аргумента принимает переменную soup_audits.
    list_of_lessons_audiences = find_lessons_audits(soup_audits)
       
    # Если список групп есть списком...
    lessons = find_lecture_or_practice(list_of_lessons, list_of_lessons_audiences)
    
        # - Определяем, какой день указан на странице;
    day = (str)(soup.find_all('tr')[1].find_all('td')[0].get_text())
        # - Добавляем этот день в сообщение бота;
    lessons.append(f"Розклад занять {day.lower()}:")
        
    # Если всё прошло хорошо, то возвращаем боту его сообщение.
    return lessons

@dp.message_handler(commands='start')
async def _start(message):
    """ Приём сообщения для старта бота. Сам бот после активации выводит приветствие и предлагает отправить сообщение "/расписание занятий".
    
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

Сама функция создаёт переменную message_text, которая принимает текст сообщения пользователя в низком регистре. После идёт проверка, соответствует ли значение этой переменной хотя бы одному из элементов массива timetable_of_lessons_syntax. Если да, то возвращает True, иначе False.
    
Принимает:
- message(сообщение, которое ввёл пользователь).

Возвращает одно из двух:
- True, если пользователь ввёл правильную команду;
- False, если пользователь ввёл неправильную команду."""
    message_text = message.text.lower()
    for i in timetable_of_lessons_syntax:
        if(message_text == i):
            return True
    return False

@dp.message_handler(lambda message:check_right_input_timetable_of_lessons(message))
async def _week(message):
    """Приём сообщения для вывода кнопок, чтобы отдавать команды боту не с помощью написания их с клавиатуры, а через специальные кнопки Telegram.
    
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
    """Предназначен для создания списка занятий за конкретный день недели и последующего вывода сообщения о нём пользователю. Внутри описан этот процес.

Принимает:
- message(сообщение, которое ввёл пользователь);
- current_weak_number(номер конкретного дня недели)"""
    # Отправляем сообщение, которое предупреждает пользователя, что мы обрабатываем данные с страницы за какой-то день недели.
    message_text = await bot.send_message(chat_id=message.chat.id,
text=f"""Проводжу зв'язок із Google Sheets, щоб дізнатися розклад занять за день тижня \"{weak_word_lists[current_weak_number][1][1:].capitalize()}\". Це не дуже швидкий процес, почекайте, будь ласка...
Після успішної обробки данних я видалю це повідомлення та відправлю розклад занять новим повідомленням.""")
    # Создаём переменную lessons и присваиваем ей значение результата выполнения функции data(), в качестве
    # параметров передаём ссылку на нужный день недели.
    lessons = await data(url[current_weak_number])
    # Удаляет сообщение, которое предупреждало пользователя об обработке данных.
    await bot.delete_message(chat_id=message.chat.id,
                       message_id=message_text.message_id)
    # Если тип переменной lessons - это список(list)...
    if(type(lessons) is list):
        # ...то тогда:
        # - Устанавливаем первым элементом дату, которая указана была на странице Google Sheets;
        text_to_send = lessons[-1]
        # - Устанавливаем номер занятия.
        lesson_index = 1
        # Проходимся по списку lessons
        for i in lessons:
            # Если текущий элемент не есть элементом, который отвечает за дату...
            if(i != lessons[-1]):
                # ...то тогда:
                # - добавляем для переменной text_to_send название занятия и её номер;
                text_to_send += f"\n{lesson_index}. {i}"
                # - увеличиваем значение номера занятия на 1.
                lesson_index += 1
        # Выводит новое сообщение с расписание занятий в Telegram.
        m = await bot.send_message(
            chat_id=message.chat.id,
            text = text_to_send)
    # А если тип переменной lessons - это ValueError...
    elif(type(lessons) is ValueError):
        # ...то тогда:
        # - Если аргумент ошибки был "Group not found"...
        if(lessons.args[0] == "Group not found"):
            # ...то тогда выводим сообщение, что группа не найдена.
            await bot.send_message(chat_id=message.chat.id,
                                text=f"Виникла помилка:\nБот не знайшов розклад занять для группи {current_group} за день тижня \"{weak_word_lists[current_weak_number][1][1:].capitalize()}\"")
        # - А если аргумент ошибки был "Lessons count"...
        elif(lessons.args[0] == "Lessons count"):
            # ...то тогда выводим сообщение, что неправильное количество пар.
            await bot.send_message(chat_id=message.chat.id,
                                text=f"Виникла помилка:\nБот виявив неправильну кількість пар для группи {current_group} за день тижня \"{weak_word_lists[current_weak_number][1][1:].capitalize()}\"")
    # - В противном случае...
    else:
        # ...выводим пользователю сообщение, что у нас неизвестная ошибка.
        await bot.send_message(chat_id=message.chat.id,
                                text=f"Виникла невідома помилка.")

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

@dp.message_handler(lambda message: message.text.lower() == "/зміни" or message.text.lower() == "/изменения")
async def changes(message):
    """Выводить пользователю сообщение, которое покажет изменения, которые произошли в боте.
    
Принимает:
- message(сообщение, которое ввёл пользователь)."""
    await bot.send_message(message.chat.id, changes_text)

""" async def checkUp():
#     check = ...
#     }
#     all_schedule = [data(url[0]), data(url[1]), data(url[2]), data_2(url[3]), data_2(url[4])]
#     while True:
#         for schedule in zip(check.values(), all_schedule, check.keys()):
#             if tuple(schedule[0]) != schedule[1]:
#                 await bot.send_message(
#                     chat_id=-1001753097408,
#                     text=f'Расписание изменилось {schedule[1][6]} \n1.{schedule[1][0]}\n2.{schedule[1][1]}\n3.{schedule[1][2]}\n4.{schedule[1][3]}'
#                         f'\n5.{schedule[1][4]}\n6.{schedule[1][5]}'
#                 )
#                 check[schedule[2]] = schedule[1]
#             else:
#                 continue
#         await asyncio.sleep(1)"""

# Проверяем нормально ли всё с скриптом.
if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # # loop.create_task(checkUp())
    
    # Запускаем бота в long-polling режиме.
    executor.start_polling(dp, skip_updates=True)

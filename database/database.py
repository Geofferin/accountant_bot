import os
import sqlite3
from itertools import chain


class Database:

    def __init__(self):
        path_to_bd = os.path.join(os.path.dirname(__file__), 'db.db')
        self.conn = sqlite3.connect(path_to_bd)
        self.cursor = self.conn.cursor()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        join_data DEFAULT (datetime('now','localtime')))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS costs(
        id INTEGER PRIMARY KEY,
        value INTEGER NOT NULL,
        date DEFAULT (datetime('now','localtime')),
        user_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL)''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories(
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL
        )''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS incomes(
        id INTEGER PRIMARY KEY,
        value INTEGER NOT NULL,
        date DEFAULT (datetime('now','localtime')),
        user_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL)''')

        self.conn.commit()

    def user_exists(self, user_id):
        """Проверяем, есть ли юзер в базе"""
        result = self.cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        result = result.fetchall()
        return bool(result)

    def add_user(self, user_id):
        """Добавляем юзера в базу"""
        self.cursor.execute("INSERT INTO users (id) VALUES (?)", (user_id,))
        return self.conn.commit()

    """В этих двух функциях используется глобальная переменная"""

    def get_categories(self, user_id, operation):
        """Получаем категории доходов и расходов для пользователя"""
        if operation == 'income':
            self.cursor.execute("SELECT name FROM categories WHERE user_id = ? and type = 'income'", (user_id,))
        elif operation == 'spend':
            self.cursor.execute("SELECT name FROM categories WHERE user_id = ? and type = 'spend'", (user_id,))
        elif operation == 'all':
            self.cursor.execute('''SELECT name FROM categories WHERE user_id = ?''', (user_id,))
        result = str(self.cursor.fetchall()).replace('[', '').replace('(', '').replace(',', '').replace(')', '').replace(']', '').replace(
            "'", '').split()
        return result

    def add_category(self, user_id, new_category, operation):
        if operation == 'income':
            self.cursor.execute('''INSERT INTO categories (name, user_id, type) VALUES (?, ?, ?)''', (new_category, user_id, 'income'))
        elif operation == 'spend':
            self.cursor.execute('''INSERT INTO categories (name, user_id, type) VALUES (?, ?, ?)''', (new_category, user_id, 'spend'))
        return self.conn.commit()

    def del_category(self, user_id, category_del, operation):
        if operation == 'income':
            self.cursor.execute('''DELETE FROM categories WHERE user_id = ? and name = ? and type = ?''',
                                (user_id, category_del, 'income'))
        elif operation == 'spend':
            self.cursor.execute('''DELETE FROM categories WHERE user_id = ? and name = ? and type = ?''',
                                (user_id, category_del, 'spend'))
        self.conn.commit()

    '''
    TO DO:
    ВО ПЕРВЫХ, ОТРЕДАКТИРОВАТЬ САМУ БАЗУ, РАЗДЕЛИВ ДОХОДЫ И РАСХОДЫ = DONE
        сделать добавление записей в нужную таблицу = DONE
        в базе отображается другой часовой пояс, нужно поправить на московский - https://qna.habr.com/q/1090250 = DONE
    ВО ВТОРЫХ РАЗОБРАТЬСЯ ТАБЛИЦЕЙ ПОЛЬЗОВАТЕЛЕЙ, НУЖНА ЛИ ОНА ВООБЩЕ = Таблица крайне необходима, иначе каждому п-лю будут выводиться вообще все записи.
    В ТРЕТЬИХ СДЕЛАТЬ ПОДСЧЕТ ТЕКУЩЕГО БАЛАНСА И ДОБАВИТЬ КОМАНДУ ДЛЯ ЕГО ВЫВОДА В БОТ = DONE
    А ТАК ЖЕ СДЕЛАТЬ ВЫВОД СПИСКА ОПЕРАЦИЙ (ОН И ТАК ЕСТЬ, ПРОСТО ДОРАБОТАТЬ ПОД СЕБЯ) = DONE
    '''

    def add_income(self, user_id, value, category):
        """Создаем запись о доходах"""
        category_id = self.cursor.execute('SELECT id FROM categories WHERE user_id = ? and name = ? and type = ?',
                                          (user_id, category, 'income'))
        category_id = category_id.fetchall()[0][0]
        self.cursor.execute("INSERT INTO incomes (value, category_id, user_id) VALUES (?, ?, ?)",
                            (value, category_id, user_id))
        self.conn.commit()

    def add_cost(self, user_id, value, category):
        """Создаем запись о расходах"""
        category_id = self.cursor.execute('SELECT id FROM categories WHERE user_id = ? and name = ? and type = ?',
                                          (user_id, category, 'spend'))
        category_id = category_id.fetchall()[0][0]
        self.cursor.execute("INSERT INTO costs (value, category_id, user_id) VALUES (?, ?, ?)",
                            (value, category_id, user_id))
        self.conn.commit()

    def get_balance(self, user_id):
        """Получаем разницу мержу всеми доходами и расходами - текущий баланс"""
        incomes = self.cursor.execute("SELECT value FROM incomes WHERE user_id = ?", (user_id,)).fetchall()
        costs = self.cursor.execute('SELECT value FROM costs WHERE user_id = ?', (user_id,)).fetchall()
        total_income = sum(chain.from_iterable(incomes))
        total_costs = sum(chain.from_iterable(costs))
        return total_income - total_costs

    def get_history(self, period, user_id, categories = tuple()):
        """Получаем историю за нужный период"""
        categories_mask = ', '.join(['?'] * len(categories))
        categories_query = lambda mask: f"AND categories.name in ({mask})" * bool(categories_mask) # этот подзапрос будет добавлен только если были переданы параметры с категориями
        sql_query = lambda fr, cat_query, mask, per: f'''
        SELECT
            {fr}.date,
            {fr}.value,
            categories.name
        FROM {fr}
        JOIN categories ON {fr}.category_id = categories.id
        WHERE {fr}.user_id = ?
            {categories_query(mask)}
            AND {fr}.date BETWEEN datetime('now', '-{per} days') AND datetime('now', 'localtime')
        ORDER BY {fr}.date'''

        self.cursor.execute(sql_query('incomes', categories_query, categories_mask, period),
                            (user_id, *categories))

        income_data = self.cursor.fetchall()

        self.cursor.execute(sql_query('costs', categories_query, categories_mask, period),
                            (user_id, *categories))

        spend_data = self.cursor.fetchall()

        return self.history_format(income_data, spend_data)

    def history_format(self, income, spend):
        history = 'income:\n'
        for date, value, category in income:
            history += f'    Категория: {category}\n'
            history += f'    Дата: {date}\n'
            history += f'    Сумма: {value} ₽\n\n'
        history += '\ncost:\n'

        for date, value, category in spend:
            history += f'    Категория: {category}\n'
            history += f'    Дата: {date}\n'
            history += f'    Сумма: {value} ₽\n\n'

        return history

    def close(self):
        """Закрываем соединение с БД"""
        self.conn.close()

import sqlite3
import os

class Database:

    def __init__(self):
        path_to_bd = os.path.join(os.path.dirname(__file__), 'db.db')
        self.conn = sqlite3.connect(path_to_bd)
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        """Проверяем, есть ли юзер в базе"""
        result = self.cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
        return bool(len(result.fetchall()))

    def get_user_id(self, user_id):
        """Достаем id юзера в базе по его user_id"""
        result = self.cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
        return result.fetchone()[0]

    def add_user(self, user_id):
        """Добавляем юзера в базу"""
        self.cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        return self.conn.commit()

    """В этих двух функциях используется глобальная переменная"""
    def get_categories(self, user_id, operation):
        """Получаем категории доходов и расходов для пользователя"""
        if operation == 'income':
            self.cursor.execute("SELECT income_categories FROM users WHERE user_id = ?", (user_id,))
        elif operation == 'spend':
            self.cursor.execute("SELECT spend_categories FROM users WHERE user_id = ?", (user_id,))
        result = str(self.cursor.fetchall()).replace('[', '').replace('(', '').replace(',', '').replace(')', '').replace(']', '').replace("'", '').split()
        return result

    def add_category(self, user_id, new_category, operation):
        if operation:
            self.cursor.execute("UPDATE users SET income_categories = income_categories || ? WHERE user_id = ?", (new_category, user_id))
        elif not operation:
            self.cursor.execute("UPDATE users SET spend_categories = spend_categories || ? WHERE user_id = ?", (new_category, user_id))
        return self.conn.commit()

    def del_category(self, user_id, category_del, operation):
        if operation:
            self.cursor.execute("UPDATE users SET income_categories = REPLACE(income_categories, ?, '') WHERE user_id = ?", (category_del, user_id))
        elif not operation:
            self.cursor.execute("UPDATE users SET spend_categories = REPLACE(spend_categories, ?, '') WHERE user_id = ?", (category_del, user_id))
        return self.conn.commit()

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
        self.cursor.execute("INSERT INTO incomes (value, category, user_id) VALUES (?, ?, ?)", (value, category, self.get_user_id(user_id)))
        return self.conn.commit()

    def add_cost(self, user_id, value, category):
        """Создаем запись о расходах"""
        self.cursor.execute("INSERT INTO costs (value, category, user_id) VALUES (?, ?, ?)", (value, category, self.get_user_id(user_id)))
        return self.conn.commit()

    def get_balance(self, user_id):
        """Получаем разницу мержу всеми доходами и расходами - текущий баланс"""
        total_income = 0
        self.cursor.execute("SELECT value FROM incomes WHERE user_id = ?", (self.get_user_id(user_id),))
        for i in self.cursor.fetchall():
            total_income += float(str(i).replace('\'', '').replace('(', '').replace(')', '').replace(',', ''))

        total_costs = 0
        self.cursor.execute("SELECT value FROM costs WHERE user_id = ?", (self.get_user_id(user_id),))
        for i in self.cursor.fetchall():
            total_costs += float(str(i).replace('\'', '').replace('(', '').replace(')', '').replace(',', ''))

        return total_income - total_costs

    def get_history(self, period, user_id):
        """Получаем историю за нужный период"""
        self.cursor.execute(f"""SELECT date, value, category FROM incomes WHERE user_id = ? AND date BETWEEN datetime('now', '-{period} days')
                                AND datetime('now', 'localtime') ORDER BY date""", (self.get_user_id(user_id),))
        history = 'income: '
        history += '\nincome: '.join(map(str, self.cursor.fetchall()))
        history += '\n\ncost: '
        self.cursor.execute(f"""SELECT date, value, category FROM costs WHERE user_id = ? AND date BETWEEN datetime('now', '-{period} days') 
                                AND datetime('now', 'localtime') ORDER BY date""", (self.get_user_id(user_id),))
        history += '\ncost: '.join(map(str, self.cursor.fetchall()))
        return history

    def close(self):
        """Закрываем соединение с БД"""
        self.conn.close()

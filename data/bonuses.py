import yaml, sqlite3


connection = sqlite3.connect('data/db.sqlite3')
cursor = connection.cursor()


with open('data/bonuses.yaml', 'r') as file:
    data = yaml.safe_load(file)
    for emp in data:
        cursor.execute('insert into bonuses(min_streak, bonus_cm, bonus_attempts) values(?, ?, ?)', (emp['min_streak'], emp['bonus_cm'], emp['bonus_attempts']))

    connection.commit()
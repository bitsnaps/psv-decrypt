import sqlite3

# Simple Usage:
#    db = SqliteReader('test.db')
#    data = db.find_one('SELECT count(*) FROM user')
#    print('count: ', data[0])
#    db.execute('INSERT INTO user VALUES (4, "Karim")')
#    rows = db.find_all('SELECT id, name FROM user')
#    for row in rows:
#        print('id: ', row[0], ', name: ', row[1])
#    db.close()
class SqliteReader:

    connexion = None
    cursor = None

    def __init__(self, db_path):
        self.connexion = sqlite3.connect(db_path)
        self.cursor = self.connexion.cursor()

    def find_one(self, sql, params = []):
        cursor = self.query(sql, params)
        return cursor.fetchone()

    def find_all(self, sql, params = []):
        cursor = self.query(sql, params)
        return cursor.fetchall()

    def query(self, sql, params = []):
        if not self.check_connection():
            return
        if params:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)
        return self.cursor

    def execute(self, sql):
        if not self.check_connection():
            return
        result = self.cursor.execute(sql)
        self.connexion.commit()
        return result

    def get_column_names(self, sql):
        if not self.check_connection():
            return
        self.cursor.execute(sql)
        names = list(map(lambda x: x[0], self.cursor.description))
        return names

    def get_last_id(self):
        if not self.check_connection():
            return
        return self.cursor.lastrowid

    def is_connected(self):
        #result = True
        #if not self.connexion:
        #    print('Error: No connexion provided')
        #    result = False
        #if not self.cursor:
        #    print('Error: Cursor not found')
        #    result = False
        #return result
        return self.connexion and self.cursor

    def check_connection(self):
        result = True
        if not self.connexion:
            print('Error: No connexion provided')
            result = False
        if not self.cursor:
            print('Error: Cursor not found')
            result = False
        return result

    def close(self):
        if not self.check_connection():
            return
        self.connexion.close()

    def db_connect(self):
        cnt = sqlite3.connect('C:/Dev/PluralsightDec/test.db')
        cur = cnt.cursor()
        #cur.execute('CREATE TABLE IF NOT EXISTS user (id integer PRIMARY KEY, name text NOT NULL)')
        #cur.execute('INSERT INTO user VALUES (1, "Ali")')
        #cur.execute('INSERT INTO user VALUES (2, "Said")')
        #cur.execute('INSERT INTO user VALUES (3,"Hakim")')
        #cnt.commit()
        #cur.execute('SELECT name FROM user WHERE id = 2')
        #data = cur.fetchone()
        #print(data[0])
        #assert data[0] == 'Said'
        cur.execute('SELECT count(*) FROM user')
        data = cur.fetchone()
        #rows = cur.fetchall()
        assert data[0] == 3

        data = cur.execute('SELECT * FROM user WHERE id = 1')
        user1 = data.fetchone()
        print('user name: ', user1[1], ', id: ', user1[0])
        names = list(map(lambda x: x[0], cur.description))
        print(names)
        cnt.close()
        return names
import sys, os
from app.decryptor import *
from app.utils import Utils
#from app.sqlite_reader import *

if __name__=='__main__':
    #print('AppData: ', os.environ['APPDATA'])

    #args = sys.argv
    #for arg in args:
    #    print(arg)

    decOpt = DecryptorOptions(sys.argv[1:])
    # check if path is not null
    if not decOpt.InputPath:
        Utils.print_input_path_mandatory()
        sys.exit(2)

    print('Input path: ', decOpt.InputPath, ', Out path: ', decOpt.OutputPath)

    decryptor = Decryptor(decOpt)
    decryptor.decryptAllFolders(decOpt.InputPath, decOpt.OutputPath)

    #s = str(b'hello') # need to be string not bytes
    #print(Utils.md5(s))
    #print(str(base64.b64encode(Utils.md5(s).encode())).replace('/', '_'))

    # Testing the db
    #db = SqliteReader('test.db')
    #data = db.find_one('SELECT count(*) FROM user')
    #print('count: ', data[0])
    #db.execute('INSERT INTO user VALUES (4, "Karim")')
    #print(db.get_last_id()) # 4
    ##db.execute('DELETE FROM user WHERE id=4')
    #print(db.get_column_names('SELECT * FROM user'))
    #rows = db.find_all('SELECT id, name FROM user')
    #for row in rows:
    #    print('id: ', row[0], ', name: ', row[1])
    #db.close()








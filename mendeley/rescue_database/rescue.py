from pygdbmi.gdbcontroller import GdbController
import sys
import argparse
import os

class ValidException(Exception):
    pass

def validWithKeyword(gdb, keyword, timeout_sec=1, debug=0):
    while True:
        response = gdb.get_gdb_response(timeout_sec)
        if debug:
            print(response, file=sys.stderr)
        
        for msg in response:
            if keyword in msg['payload']:
                return msg['payload']

def getResult(response):
    return response[response.find('=')+2:]

def attempt(times, mendeley, db, debug=0):
    gdb = GdbController(mendeley, ['--debug'])
    
    try:
        gdb.write('b sqlite3_open_v2', read_response=False)
        validWithKeyword(gdb, 'Breakpoint', debug=debug)
        
        gdb.write('r', read_response=False)
        validWithKeyword(gdb, 'sqlite3_open_v2', 5, debug=debug)
        
        response = None
        while True:
            response = gdb.write('x/s $rdi')
            if db in response[0]['payload']:
                if debug:
                    print(response, file=sys.stderr)
                break
            
            gdb.write('c', read_response=False)
            validWithKeyword(gdb, 'sqlite3_open_v2', 5, debug=debug)
        
        for i in range(1, times):
            gdb.write('c', read_response=False)
            validWithKeyword(gdb, 'sqlite3_open_v2', 5, debug=debug)
            response = gdb.write('x/s $rdi')
            if db not in response[0]['payload']:
                raise ValidException('Attemp failed')
         
        gdb.write('b sqlite3_key', read_response=False)
        validWithKeyword(gdb, 'Breakpoint', debug=debug)
        
        gdb.write('c', read_response=False)
        validWithKeyword(gdb, 'sqlite3_key', debug=debug)
        
        response = gdb.write('p/x $rdi')
        if debug:
            print(response, file=sys.stderr)
        addr = getResult(response[0]['payload'])
        
        gdb.write('fin', read_response=False)
        validWithKeyword(gdb, 'sqlite3_key', debug=debug)
        
        response = gdb.write('p (int) sqlite3_rekey_v2(%s, 0, 0, 0)' % addr)
        if debug:
            print(response, file=sys.stderr)
        rtn = getResult(response[0]['payload'])
        
        if rtn != '0':
            raise ValidException('Attempt failed')
        
    except ValidException as e:
        print(e)
        return False
    except Exception as e:
        print(e)
        return False
    finally:
        gdb.exit()
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description="Rescue the data from the envrypted mendeley database.")
    parser.add_argument('--path', '-p', required=True,
                        help="The mendeleydesktop file path.")
    parser.add_argument('--database', '-db', required=True,
                        help="The encrypted database file path.")
    parser.add_argument('--attempts', '-t', default=2, type=int,
                        help="The time of attempt, 2 times is default. Multiple attempts needed \
                        due to the thread interleaving or spurious opening of the database.")
    parser.add_argument('--save', '-s', default='.',
                        help="Path to save the rescued database, current working folder is default.")
    parser.add_argument('--debug', action="store_true",
                        help="Display debug information.")
    args = parser.parse_args()

    mendeley = os.path.realpath(args.path)
    if not os.path.exists(mendeley):
        print('%s not found.' % args.path)
        sys.exit(1)

    db = os.path.realpath(args.database)
    if not os.path.exists(db):
        print('%s not found.' % args.database)
        sys.exit(2)

    # Backup the database
    if os.system('cp -p "%s" "%s.bak"' % (db, db)):
        print('Unable to backup the database, please check the permission.')
        sys.exit(3)

    fail = True
    for i in range(1, args.attempts+1):
        print('%d attempt' % i)
        if attempt(i, mendeley, db, args.debug):
            print('Succeeded!')
            fail = False
            break

    if not fail:
        if os.system('cp -p "%s" "%s"' % (db, args.save)):
            print('Unable to copy the file, you may have to copy the file and restore the database manually.')
            sys.exit(4)

    # Restore the database
    if os.system('cp -p "%s.bak" "%s"' % (db, db)):
        print('Unable to restore the database, you may have to restore the file manually.')
        sys.exit(5)

    # Delete the backup
    if os.system('rm "%s.bak"' % db):
        print('Unable to delete the backup, you may have to delete the file manually.')
        sys.exit(6)

    sys.exit(-1 if fail else 0)
from pygdbmi.gdbcontroller import GdbController
import sys
import argparse
import os
import traceback

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

def setPath(gdb, path, var_count):
    length = len(path)+1
    count = var_count+1
    gdb.write('p malloc(%d)' % length)
    gdb.write('set {char [%d]} $%d = "%s"' % (length, count, path), read_response=False)
    gdb.write('set $rdi = $%d' % count, read_response=False)
    response = gdb.write('x/s $rdi')
    if path not in response[0]['payload']:
        raise ValidException('Unable to set database file.')
    return count

def attempt(times, mendeley, db, save_path, debug=0):
    gdb = GdbController(mendeley, ['--debug'])
    var_count = 0
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
        
        var_count = setPath(gdb, save_path, var_count)
        for i in range(1, times):
            gdb.write('c', read_response=False)
            validWithKeyword(gdb, 'sqlite3_open_v2', 5, debug=debug)
            response = gdb.write('x/s $rdi')
            if db not in response[0]['payload']:
                raise ValidException('Attemp failed')
            var_count = setPath(gdb, save_path, var_count)
         
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
    except Exception:
        traceback.print_exc()
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
    parser.add_argument('--save', '-s', default='save.sqlite',
                        help="The filename to save the rescued database, save.sqlite is default.")
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
    
    save_path = os.path.join(os.getcwd(), args.save)
    # Copy the database
    if os.system('cp -p "%s" "%s"' % (db, save_path)):
        print('Unable to copy the database.')
        sys.exit(3)

    for i in range(1, args.attempts+1):
        print('%d attempt' % i)
        if attempt(i, mendeley, db, save_path, args.debug):
            print('Succeeded!')
            sys.exit(0)
            break

    sys.exit(-1)
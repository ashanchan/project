from colorama import Fore, Back, Style
import util.system as SYSTEM
# ===================================================


def show(mode, msg):
    if mode == 'error':
        print(Fore.RED + msg)
        SYSTEM.talkBack('say "Fatal Error" ')
    elif mode == 'warning':
        print(Fore.YELLOW + msg)
    elif mode == 'info':
        print(Fore.GREEN + msg)
# ===================================================


def reset():
    print(Style.RESET_ALL)

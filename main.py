import os
import sys
import log_manager
import pyperclip
import configer

def copy_and_print(text, notification):
    pyperclip.copy(text)
    print(text)
    print("\n\n\n DONE! \n\n\n")
    # if there is some notification string， print it out. if notification is None, do nothing
    if notification:
        print(notification)


def change(args):
    print("TODO")

def exchange(args):
    print("TODO")

def begin():
    copy_and_print(configer.get_prompt(), False)

def start(args):
    print("TODO")

def end(args):
    print("TODO")

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1]
        args = sys.argv[2:]
        if command == "change":
            change(args)
        elif command == "exchange":
            exchange(args)
        elif command == "start":
            start(args)
        elif command == "end":
            end(args)
        else:
            print(f"Unknown command: {command}")
    else:
        begin()

    # CMD GUI mode
    # Not yet implemented. please use command line arguments

if __name__ == "__main__":
    main()

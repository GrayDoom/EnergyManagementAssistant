import os
import sys
import log_manager
import pyperclip
import configer

def copy_and_print(text, contain):
    # if contain is true, add "`info " to the front, and " end`" to the end
    # basically, contain is true except the begin function
    text = text if not contain else f"`info {text} end`"
    pyperclip.copy(text)
    print(text)
    print("\n\n\n DONE! \n\n\n")
    return 0

def change(args):
    # args is a list of strings, transfer it to log_manager insert function
    # use return value copy_and_print
    text = log_manager.insert(args)
    copy_and_print(text, True)

class ex_change():
    def __init__(self, args):
        # get the two index from args
        self.index1 = int(args[0])
        self.index2 = int(args[1])

    def header(self):
        # turn the new header into a list
        header = configer.get_header()
        # take it to configer.set_header
        configer.set_header(header)
        # also update the log by log_manager.rebuild_header
        log_manager.rebuild_header()

    def update_log(self, data):
        text = log_manager.update(data)
        copy_and_print(text, True)

    def header_and_log(self, data):
        # `update_header_and_log` by self.update_header and change function outside this class
        self.header()
        self.update_log(data)

def begin():
    text = configer.get_prompt() + log_manager.init() + "`"
    copy_and_print(text, False)

def start(args):
    # This is the info about the user's status when they start this manager
    # similar to the change function. But need more steps, maybe.
    log_manager.insert(args)
    copy_and_print(" ".join(args), True)

def end(args):
    # This is the info about the user's status when they end this manager
    # handle the args, then call log_manager.end
    # use return value copy_and_print
    log_manager.end(args)
    copy_and_print(" ".join(args), True)

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1]
        args = sys.argv[2:]
        if command == "change":
            change(args)
        elif command == "exchange":
            exchanger = ex_change(args)
            exchanger.update_header_and_log(args[2])  # assuming timestamp is the third argument
        elif command == "start":
            start(args)
        elif command == "end":
            end(args)
        else:
            print(f"Unknown command: {command}")
    else:
        begin()

if __name__ == "__main__":
    main()

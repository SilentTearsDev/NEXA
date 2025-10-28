import sys, os
# garantáljuk, hogy a projekt gyökere benne legyen az import path-ban
sys.path.append(os.path.dirname(__file__))

from ui.shell import NexaShell

if __name__ == "__main__":
    app = NexaShell()
    app.mainloop()

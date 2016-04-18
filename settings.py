from parser import Parser
import os


class SettingsParser(Parser):
    def __init__(self, filename):
        Parser.__init__(self, filename)


class Settings:
    _instances = dict()
    _files = list()

    def __init__(self, filename):
        self.filename = filename
        self.path = os.path.abspath(filename)

        if not os.path.exists(filename):
            file = open(self.path, 'w')
            file.close()

        if not os.path.isfile(filename):
            pass

        if self.path not in Settings._files:
            Settings._files.append(self.path)
            self.parser = SettingsParser(self.path)
            Settings._instances[self.path] = self.parser
        else:
            self.parser = Settings._instances[self.path]

    def __setitem__(self, key, value):
        self.parser[key] = value

    def __getitem__(self, item):
        return self.parser[item]

    def update(self):
        self.parser.update()

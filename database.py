from parser import parse_string
from collections import OrderedDict
from time import sleep
from threading import Thread
import os.path


class Database:
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

        if self.path not in Database._files:
            Database._files.append(self.path)
            self.parser = FileParser(self.path)
            Database._instances[self.path] = self.parser
        else:
            self.parser = Database._instances[self.path]

    def __setitem__(self, key, value):
        self.parser[key] = value

    def __getitem__(self, item):
        return self.parser[item]

    def update(self):
        self.parser.update()


class FileParser:
    def __init__(self, filename):
        self.filename = filename

        if not os.path.exists(self.filename):
            try:
                file = open(self.filename, 'a')
                file.close()
            except OSError:
                raise OSError('Could not create file ' + filename)

        self._data = OrderedDict()
        self._data_raw = ''
        self._read_from_file()

    def __setitem__(self, key, value):
        self.check_value_key(value, key)
        self._data[key] = value
        Thread(target=self._write_to_file).start()

    def __getitem__(self, item):
        for key in self._data:
            if key == item:
                return self._data[key]
        raise KeyError

    def _read_from_file(self):
        for i in range(100):
            if i == 99:
                raise IOError('Could not read config file')
            try:
                file = open(self.filename, 'r')
                self._data_raw = file.read()
                file.close()
                break
            except IOError:
                sleep(0.02)

        new_data = OrderedDict()
        lines = [line.strip() for line in self._data_raw.split('\n')[:-1]]
        for line in lines:
            if line == '':
                continue
            key = line.split('=', 1)[0].strip()
            if key in new_data:
                raise KeyError('Key "' + key + '" is found more than once in ' + self.filename)
            value = parse_string(line.split('=', 1)[1].strip())
            new_data[key] = value
        self._data = new_data

    def _write_to_file(self):
        file = open(self.filename, 'w')
        for key in self._data:
            file.write(str(key) + ' = ' + str(self._data[key]) + '\n')
        file.close()

    @staticmethod
    def check_value_key(value, key):
        if type(value) not in [list, dict, tuple, str, int, float, bool]:
            if value:
                raise TypeError('Parser only accepts values of these types: int, float, str, bool, list, dict, tuple')
        if '=' in key:
            raise KeyError("Key may not contain '=' signs")


settings1 = Settings('testfile')
settings2 = Settings('testfile')
settings3 = Settings('testfile2')

# settings1['test1'] = ([{'kee:eey': 'value'}], 'string', [0, 1, [3, [([[4]],), 5]], 6], (True, None, False))
settings2['test2'] = 2

print(settings2['test1'])
print(settings1['test2'])

settings3['test1'] = 5

print(settings1['test1'])
print(settings3['test1'])
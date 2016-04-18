from time import sleep
from os.path import exists

"""
Problems:
 - _parse_value does not see difference between set and dict
 - _write_to_file should be recursively implemented
"""


class Parser(object):
    def __init__(self, filename):
        self.filename = filename
        self.first_chars = ['[', '{', '(', '"', "'"]
        self.last_chars = [']', '}', ')', '"', "'"]

        if not exists(self.filename):
            try:
                file = open(self.filename, 'a')
                file.close()
            except OSError:
                raise OSError('Could not create file ' + filename)

        self._data = dict()
        self._data_sequence = list()
        self._data_raw = ''
        self._read_from_file()

    def __setitem__(self, key, value):
        self.check_value_key(value, key)

        self._data[key] = value
        if self._data_sequence:
            if key not in self._data_sequence:
                self._data_sequence.append(key)
        self._write_to_file()

    def __getitem__(self, item):
        for key in self._data:
            if key == item:
                return self._data[key]
        raise KeyError

    def check_value_key(self, value, key):
        if type(value) not in [list, dict, tuple, str, int, float, bool]:  # set
            if value:
                raise TypeError('Parser only accepts values of these types: int, float, str, bool, list, dict, tuple')
        if '=' in key:
            raise KeyError("Key may not contain '=' signs")

    def update(self):
        raw_old = self._data_raw
        self._read_from_file()
        if self._data_raw != raw_old:
            self._write_to_file()

    def set_data(self, data):
        new_data = dict()
        new_data_sequence = list()

        if isinstance(data, dict):
            new_data = data
        elif isinstance(data, list) and isinstance(data[0], dict):
            for dictionary in data:
                if not dictionary:
                    new_data_sequence.append(None)
                    continue
                key = list(dictionary.keys())[0]
                if key in new_data.keys:
                    raise ValueError('Data should not contain the same key twice.')
                value = dictionary[key]
                new_data[key] = value
                new_data_sequence.append(key)
        elif isinstance(data, list) and isinstance(data[0], tuple):
            for tup in data:
                if not tup:
                    new_data_sequence.append(None)
                    continue
                key, value = tup
                new_data[key] = value
                new_data_sequence.append(key)
        elif not data:
            pass
        else:
            raise ValueError('Data should be a dict, list of dicts or list of tuples')

        self._data = new_data
        self._data_sequence = new_data_sequence
        self._write_to_file()

    def _write_to_file(self):
        file_string = ''

        if not self._data_sequence:
            for key in self._data:
                file_string += str(key) + ' = ' + str(self._data[key]) + '\n'
        else:
            for key in self._data_sequence:
                if not key:
                    file_string += '\n'
                else:
                    file_string += str(key) + ' = ' + str(self._data[key]) + '\n'
        file = open(self.filename, 'w')
        file.write(file_string)
        file.close()

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

        new_data = dict()
        new_data_sequence = list()
        raw_lines = [line.strip() for line in self._data_raw.split('\n')[:-1]]
        for line in raw_lines:
            line = line.strip()
            if line == '':
                new_data_sequence.append(None)
                continue
            key = line.split('=', 1)[0].strip()
            if key in new_data:
                raise KeyError('Key "' + key + '" is found more than one time in ' + self.filename)
            val = line.split('=', 1)[1].strip()
            value = self._parse_value(val)
            new_data[key] = value
            new_data_sequence.append(key)
        self._data = new_data
        self._data_sequence = new_data_sequence

    def _parse_value(self, string):
        if string[0] in ['[', '(']:
            return self._parse_list_tuple(string)
        elif string[0] == '{':
            return self._parse_dict(string)
        elif string == 'True':
            return True
        elif string == 'False':
            return False
        elif string == 'None':
            return None
        elif string[0] in ["'", '"']:
            if string[0] != string[-1]:
                raise TypeError('String is not parsed correctly')
            return string[1:-1]
        else:
            try:
                value = float(string)
                if value.is_integer():
                    value = int(value)
                return value
            except ValueError:
                return string

    def _parse_list_tuple(self, string):
        return_value = list()

        if string[0] == '(':
            data_type = list
        elif string[0] == '[':
            data_type = tuple
        else:
            data_type = None

        items_strings = string[1:-1].split(',')
        if not items_strings[-1]:
            del items_strings[-1]

        new_string = ''
        for item_string in items_strings:
            if new_string == '':
                new_string = item_string.lstrip()
            else:
                new_string += ',' + item_string

            if not new_string:
                continue
            if new_string[0] in self.first_chars:
                if self._matches(new_string.rstrip()):
                    return_value.append(self._parse_value(new_string.rstrip()))
                    new_string = ''
                continue

            return_value.append(self._parse_value(new_string.rstrip()))
            new_string = ''

        if data_type == list:
            return return_value
        elif data_type == tuple:
            return tuple(return_value)
        else:
            return None

    def _parse_dict(self, dict_string):
        new_dict = dict()
        dict_string = dict_string[1:-1]
        new_string = ''
        key_found = False
        for part_string in dict_string.split(','):
            if new_string == '':
                new_string = part_string.lstrip()
                if new_string == '':
                    continue
            else:
                new_string += ',' + part_string

            if not key_found:
                key = new_string.split(':')[0]
                if key[0] != key[-1]:
                    new_key_string = ''
                    for key_part in new_string.split(':'):
                        if new_key_string == '':
                            new_key_string = key_part
                        else:
                            new_key_string += ':' + key_part
                        if new_key_string[0] == new_key_string[-1]:
                            key = new_key_string[1:-1]
                            key_found = True
                            break
                    if not key_found:
                        continue
                else:
                    key = key[1:-1]
                    key_found = True

            value = new_string[len(key)+3:].strip()

            if value[0] in self.first_chars:
                if self._matches(new_string.rstrip()):
                    new_dict[key] = self._parse_value(value)
                    new_string = ''
                    key_found = False
                continue

            new_dict[key] = self._parse_value(value)
            new_string = ''
            key_found = False
        return new_dict

    def _parse_set(self, set_string):
        pass

    def _matches(self, string):
        first, last = string[0], string[-1]
        for i in range(len(self.first_chars)):
            first_char, last_char = self.first_chars[i], self.last_chars[i]
            if first == first_char and last == last_char and string.count(first_char) == string.count(last_char):
                return True
        return False

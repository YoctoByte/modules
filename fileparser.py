FIRST_CHARS = ['[', '{', '(', "'"]
LAST_CHARS = [']', '}', ')', "'"]


def parse_from_string(string):
    string = string.strip()

    first_char = string[0]
    if first_char == '[':
        return _parse_list(string)
    elif first_char == '(':
        return _parse_tuple(string)
    elif first_char == '{':
        return _parse_dict(string)
    elif string == 'True':
        return True
    elif string == 'False':
        return False
    elif string == 'None':
        return None
    elif first_char == "'":
        return string.strip("'")
    else:
        try:
            value = float(string)
            if value.is_integer():
                value = int(value)
            return value
        except ValueError:
            return string.strip("'")


def parse_to_string(data):
    string = ''
    if isinstance(data, str):
        for char in ["'"]:
            data = data.replace(char, '//'+char)
        string = "'" + data + "'"
    elif isinstance(data, dict):
        for key in data:
            value = data[key]
            if string:
                string += ', '
            string += parse_to_string(key) + ': ' + parse_to_string(value)
        string = '{' + string + '}'
    elif type(data) in [list, tuple]:
        for item in data:
            if string:
                string += ', '
            string += parse_to_string(item)
        empty_iter = type(data)()
        string = empty_iter[0] + string + empty_iter[1]
    elif isinstance(data, int) or isinstance(data, float):
        string = str(data)
    else:
        try:
            string = str(data)
        except Exception as e:
            print(e)
    return string


def _parse_list(string):
    new_list = list()
    for item in _split_string(string[1:-1]):
        new_list.append(parse_from_string(item))
    return new_list


def _parse_tuple(string):
    new_tuple = list()
    for item in _split_string(string[1:-1]):
        new_tuple.append(parse_from_string(item))
    return tuple(new_tuple)


def _parse_dict(string):
    new_dict = dict()

    for item in _split_string(string[1:-1]):
        key_string = item.split(':')[0]
        key = parse_from_string(key_string)
        value = item[len(key_string)+2:].strip()
        try:
            if value:
                new_dict[key] = parse_from_string(value)
        except TypeError as e:
            raise TypeError('Parse error: ' + str(e))
    return new_dict


def _parse_set():
    pass


def _split_string(string):
    # If the string used to be a list, dict, tuple, etc.. the brackets from
    # both sides should be removed before passing the string to this function.
    def matches(s):
        s = s.strip()
        # If s is an empty string. This might be the case if two commas succeed each other:
        if not s:
            return True
        first, last = s[0], s[-1]
        # In the following case s must be an unquoted string or value:
        if first not in FIRST_CHARS:
            return True
        # the most general case for lists, dicts, tuples, strings, etc.. :
        for first_char, last_char in zip(FIRST_CHARS, LAST_CHARS):
            if first == first_char and last == last_char and s.count(first_char) == s.count(last_char):
                return True
        # If s is dictionary key-value pair with string key and non-string value:
        if first == "'" and s.find("'", 1) != -1:
            return True
        return False

    full_item = ''
    for item_part in string.split(','):
        full_item += ',' + item_part
        full_item = full_item.lstrip(',')
        if matches(full_item):
            if full_item.strip():
                yield full_item.strip()
            full_item = ''

FIRST_CHARS = ['[', '{', '(', '"', "'"]
LAST_CHARS = [']', '}', ')', '"', "'"]


def parse_string(string):
    if not string:
        return None

    if string[0] == '[':
        return parse_list(string)
    elif string[0] == '(':
        return parse_tuple(string)
    elif string[0] == '{':
        return parse_dict(string)
    elif string == 'True':
        return True
    elif string == 'False':
        return False
    elif string == 'None':
        return None
    elif string[0] in ["'", '"']:
        if string[0] != string[-1]:
            raise ValueError('String is not parsed correctly. First and last characters do not match.')
        return string[1:-1]
    else:
        try:
            value = float(string)
            if value.is_integer():
                value = int(value)
            return value
        except ValueError:
            return string.strip().strip("'")


def parse_to_string(data_dict, sequence=None):
    pass


def parse_list(list_string):
    new_list = list()
    for item in _get_items_from_string(list_string[1:-1]):
        new_list.append(parse_string(item))
    return new_list


def parse_tuple(tuple_string):
    tuple_list = list()
    for item in _get_items_from_string(tuple_string[1:-1]):
        tuple_list.append(parse_string(item))
    return tuple(tuple_list)


def parse_dict(dict_string):
    new_dict = dict()

    for item in _get_items_from_string(dict_string[1:-1]):
        key_string = item.split(':')[0]
        if key_string[0] != key_string[-1]:
            new_key_string = ''
            for key_part in item.split(':'):
                if not new_key_string:
                    new_key_string = key_part
                else:
                    new_key_string += ':' + key_part
                if new_key_string[0] == new_key_string[-1]:
                    key = parse_string(new_key_string)
                    break
        else:
            key = parse_string(key_string)

        value = item[len(key)+3:].strip()
        try:
            new_dict[key] = parse_string(value)
        except TypeError:
            raise TypeError('Parse error: Dictionary key can only be of a hashable type (str, int, float, ...)')
    return new_dict


def parse_set(set_string):
    set_list = list()
    for item in _get_items_from_string(set_string[1:-1]):
        value = parse_string(item)
        if type(value) in [dict, list, set]:
            raise TypeError("Parse error: Set can only contain hashable data types (str, int, float, ...)")
        set_list.append(value)
    return set(set_list)


def _get_items_from_string(string):
    def matches(string_to_test):
        string_to_test = string_to_test.strip()
        first, last = string_to_test[0], string_to_test[-1]
        if first not in FIRST_CHARS:
            return True
        for first_char, last_char in zip(FIRST_CHARS, LAST_CHARS):
            if first == first_char and last == last_char and string_to_test.count(first_char) == string_to_test.count(last_char):
                return True
        return False

    full_item = ''
    for part_of_item in string.split(','):
        if matches(part_of_item):
            yield part_of_item.strip()
        else:
            if not full_item:
                full_item = part_of_item
            else:
                full_item += ',' + part_of_item
            if matches(full_item):
                yield full_item.strip()
                full_item = ''
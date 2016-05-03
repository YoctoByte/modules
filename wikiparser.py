from htmlparser import parse_from_url
from fileparser import parse_from_string


def parse_elements_table():
    page = parse_from_url('https://en.wikipedia.org/wiki/List_of_elements')
    table = page.get_elements('table')[0]
    table.remove(attribute=('style', 'display:none;'))
    table.remove(name='sup')
    table.remove(name='sup')
    table.remove(name='sup')
    table.remove(name='sup')

    elements = list()
    keys = None
    for row in table:
        if row[0].name == 'th' and not keys:
            keys = parse_head_row(row)
            print(keys)
        if row[0].name == 'td':
            vs = parse_body_row(row)
            element = dict()
            for key, value in zip(keys, vs):
                element[key] = value
            elements.append(element)

    with open('files/elements.txt', 'w') as file:
        for element in elements:
            file.write(str(element) + '\n')
        file.close()


def parse_body_row(row):
    values = list()
    for item in row:
        if item.to_text() in ['9e99', '&#160;!a', '−999']:
            return
        value = _parse_value(item.to_text())
        values.append(value)
    return values


def _parse_value(string):
    if string in ['–', '']:
        return None
    old_string = string

    left, right = string.find('('), string.find(')')
    if left != -1 and right != -1:
        if left == 0:
            string == string[1:-1]
        else:
            string = string[0:left-1]
            # todo: significance

    if string[0] == '[' and string[-1] == ']':
        string = string[1:-1]
        # todo: estimate

    try:
        value = float(string)
        if value.is_integer():
            value = int(value)
    except ValueError:
        value = old_string
    return value


def parse_head_row(row):
    keys = list()
    for item in row:
        if item.to_text() == '&#160;':
            return None
        else:
            text = item.to_text(exclude='sup')
            keys.append(text.split('\n', 1)[0])
    return keys

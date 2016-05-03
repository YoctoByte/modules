from htmlparser import parse_from_url  # , parse_from_file


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
    try:
        for char in ['[', ']', '(', ')']:
            string = string.replace(char, ' ')
        value = float(string)
        if value.is_integer():
            value = int(value)
    except ValueError:
        value = string
    if string in ['–', '']:
        value = None
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


parse_elements_table()

# page = parse_from_file('files/test.html')
# print(page)
# page.remove(name='p')
# page.remove(attribute=('charset', 'UTF-8'))
# print(page)

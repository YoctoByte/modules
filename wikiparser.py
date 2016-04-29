from htmlparser import parse_from_url

wiki_url = 'https://en.wikipedia.org/wiki/List_of_elements'


def parse_table(table):
    keys = None
    values = list()
    for row in table:
        if row[0].name == 'th' and not keys:
            keys = parse_head_row(row)
            print(keys)
        if row[0].name == 'td':
            values.append(parse_body_row(row))
    print(len(values))


def parse_body_row(row):
    print(row)
    for item in row:
        pass


def parse_head_row(row):
    keys = list()
    for item in row:
        if item.to_text() == '&#160;':
            return None
        else:
            keys.append(item.to_text(exclude='sup'))
    return keys


page = parse_from_url(wiki_url)
t = page.get_elements('table')[0]
t.remove(attribute=('style', 'display:none;'))
t.remove(name='sup')
parse_table(t)

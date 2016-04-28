from htmlparser import parse_from_url

wiki_url = 'https://en.wikipedia.org/wiki/List_of_elements'


def parse_table(table):
    head = list()
    body = list()
    for row in table:
        if row[0].name == 'th':
            head.append(row)
        if row[0].name == 'td':
            body.append(row)
    print(len(head), len(body))


page = parse_from_url(wiki_url)
table = page.get_elements('table')[0]
parse_table(table)

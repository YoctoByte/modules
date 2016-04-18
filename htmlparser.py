import requests


wiki_url = 'https://en.wikipedia.org/wiki/List_of_elements'  # 'https://en.wikipedia.org/wiki/Hydrogen'  #


class Parser:
    def __init__(self, url):
        self.url = url
        self.content_list = self.get_content()

    def get_content(self):
        page = requests.get(self.url)
        content_string = page.content.decode('utf-8')
        content_list = [line.strip() for line in content_string.split('\n')]
        return content_list

    def _extract(self, keyword):
        items = list()
        start = []
        for i, line in enumerate(self.content_list):
            if line[:len(keyword)+1] == '<' + keyword:
                start.append(i)
            if line[-(len(keyword)+2):] == '/' + keyword + '>':
                if start:
                    end = i+1
                    item = self.content_list[start.pop():end]
                    items.append(item)
                else:
                    pass
        return items

    @staticmethod
    def _extract_from(content_list, keyword):
        items = list()
        start = []
        for i, line in enumerate(content_list):
            if line[:len(keyword)+1] == '<' + keyword:
                start.append(i)
            if line[-(len(keyword)+2):] == '/' + keyword + '>':
                if start:
                    end = i+1
                    item = content_list[start.pop():end]
                    items.append(item)
                else:
                    pass
        return items

    @staticmethod
    def _extract_link(link_string, from_pos=0):
        end = link_string.find('</a>', from_pos)
        if end == -1:
            return ''
        start = 0
        while True:
            new_start = link_string.find('>', start)
            if new_start == -1 or new_start > end:
                break
            start = new_start+1
        return link_string[start:end]

    @staticmethod
    def _extract_text(string):
        string = '>' + string
        text_string = ''
        pos = -1
        while True:
            pos = string.find('>', pos+1)
            if pos != -1:
                previous_pos = pos+1
                pos = string.find('<', pos+1)
                text_string += string[previous_pos:pos]
                if pos == -1:
                    break
            else:
                break
        return text_string


class WikiParser(Parser):
    def __init__(self, url):
        Parser.__init__(self, url)

    def parse_tables(self):
        parsed_tables = list()
        tables = self._extract('table')
        for table in tables:
            parsed_table = self.parse_table(table)
            parsed_tables.append(parsed_table)
        return parsed_tables

    def parse_table(self, raw_table):
        def row_ok(r):
            for seq in ['<th></th>', '<td>−999</td>', '<td>9e99</td>']:
                if seq in r:
                    return False
            return True

        head, body = list(), list()
        rows = [row[1:-1] for row in self._extract_from(raw_table, 'tr')]
        for row in rows:
            if not row_ok(row):
                continue
            if row[0][:3] == '<th':
                head.append(row)
            else:
                body.append(row)

        titles = list()
        if head:
            for string in head[0]:
                if string[:3] == '<th':
                    title = self._extract_text(string)
                    titles.append(title)

        table_list = list()
        for row in body:
            try:
                row_dict = dict()
                for i, item in enumerate(row):
                    row_dict[titles[i]] = self._extract_text(item)
                table_list.append(row_dict)
            except IndexError:
                pass

        return table_list

wiki_parser = WikiParser(wiki_url)
elements_table = wiki_parser.parse_tables()[0]
for r in elements_table:
    print(r)
import requests


wiki_url = 'https://en.wikipedia.org/wiki/List_of_elements'
non_paired_tags = ['area', 'base', 'br', 'col', 'command',
                   'embed', 'hr', 'img', 'input', 'link',
                   'meta', 'param', 'source', 'wbr', 'keygen',
                   'track', 'button']


class HTMLParser:
    def __init__(self, url):
        # self.url = url
        # page = requests.get(self.url)
        # self.content = page.content.decode('utf-8')

        file = open('files/test.html', 'r')
        self.content = file.read()
        file.close()

        # 'compress' the html string to a single line
        new_content = ''
        for line in self.content.split('\n'):
            new_content += line.strip()
        self.content = new_content

        self.remove_comments()
        self.remove_doctype()

        print(self.content)
        self.elements = self._parse()
        print(self.elements)

    def remove_doctype(self):
        left_pos = self.content.find('<')
        right_pos = self.content.find('>')
        first_tag = self.content[left_pos:right_pos+1]
        if first_tag[:9] == '<!DOCTYPE':
            self.content = self.content[right_pos+1:]

    def remove_comments(self):
        content = '-->' + self.content
        new_content = ''
        right_pos = 0
        while True:
            left_pos = content.find('-->', right_pos)+3
            right_pos = content.find('<!--', left_pos)
            if right_pos == -1:
                new_content += content[left_pos:]
                break
            new_content += content[left_pos:right_pos]
        self.content = new_content

    def _parse(self):
        def chunck_gen(seq, n):
            ind = 0
            while True:
                chk = seq[ind:ind+n]
                yield chk
                if not chk:
                    break
                ind += n

        tag = ''
        content = ''
        for chunk in chunck_gen(self.content, 1024):
            pos = -1
            chunk = tag + content + chunk
            while True:
                tag, p = self._get_tag_from_string(chunk[pos+1:])
                if p == -1:
                    content = ''
                    break
                pos += p
                content, p = self._get_content_from_string(chunk[pos:])
                if p == -1:
                    break
                pos += p
                print(tag + content)

    @staticmethod
    def _get_content_from_string(string):
        left_pos = string.find('>')+1
        if left_pos == 0:
            return '', -1
        right_pos = string.find('<', left_pos)
        if right_pos != -1:
            content = string[left_pos:right_pos]
        else:
            content = string[left_pos:]
            return content, -1
        return content, right_pos-2

    @staticmethod
    def _get_tag_from_string(string):
        left_pos = string.find('<')
        if left_pos == -1:
            return '', -1
        right_pos = string.find('>', left_pos)
        if right_pos != -1:
            tag = string[left_pos:right_pos+1]
        else:
            tag = string[left_pos:]
        return tag, right_pos


class Element:
    def __init__(self, name='', depth=-1, attributes=None, content=None):
        self.attributes = dict()
        self.content = list()
        self.name = name
        self.depth = depth
        if attributes:
            self.attributes = attributes
        if content:
            self.content = content

    def get_elements(self, elem_name, recursive=True):
        elements = list()
        for content in (content for content in self.content if isinstance(content, Element)):
            if content.name == elem_name:
                elements.append(content)
            if recursive:
                elements.extend(content.get_elements(elem_name))
        return elements

    def remove_elements(self, elem_name, recursive=True, attribute=None):
        for i, content in enumerate(self.content):
            if isinstance(content, Element):
                if content.name == elem_name and not attribute:
                    del self.content[i]
                    continue
                try:
                    if content.name == elem_name and content.attributes[attribute[0]] == attribute[1]:
                        del self.content[i]
                        continue
                except KeyError:
                    pass
                if recursive:
                    content.remove_elements(elem_name, attribute=attribute)

    def append(self, item):
        self.content.append(item)

    def extend(self, item):
        self.content.extend(item)

    def __iter__(self):
        for item in self.content:
            yield item

    def to_text(self):
        text = ''
        for content in self.content:
            if isinstance(content, str):
                print(content)
                text += content
            if isinstance(content, Element):
                text += content.to_text()
        return text


class WikiParser(HTMLParser):
    def __init__(self, url):
        HTMLParser.__init__(self, url)

    @staticmethod
    def parse_std_list(table):
        def row_ok(r):
            if not isinstance(r, Element):
                return False
            if r.name != 'tr':
                return False
            for seq in ['9e99', '&#160']:
                if seq in str(r):
                    return False
            return True

        table.remove_elements('sup')
        table.remove_elements('span', attribute=('class', 'sortkey'))
        for row in (r for r in table if row_ok(r)):
            print(row)


wiki_parser = WikiParser(wiki_url)

# import requests


wiki_url = 'https://en.wikipedia.org/wiki/List_of_elements'
# non paired tags: area, base, br, col, command, embed, hr, img, input, link, meta, param, source, wbr, keygen, track,
# button


class HTMLParser:
    def __init__(self, url):
        self.url = url
        # page = requests.get(self.url)
        # self.content = page.content.decode('utf-8')
        # self.content.replace('<br>', '\n')
        # self.remove_comments()
        # if self.content[:9] == '<!DOCTYPE':
        #     self.content = self.content.split('\n', 1)[1]
        with open('example2.html', 'r') as file:
            self.content = file.read()
            file.close()
        self.elements = self._parse()

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
        open_tags = dict()  # dict with tagnames as keys and lists containing tags corresponding to that names as values
        awaiting_elements = list()
        depth = 0
        for line in self.content.split('\n'):
            pos = -1
            while True:
                element, pos = self._parse_element(line, pos+1)
                if pos == -1:
                    break

                if element.name[0] == '/':  # if element is closing tag.
                    depth -= 1
                    left_tag = open_tags[element.name[1:]].pop()
                    left_tag.depth = depth

                    indexes_to_remove = list()
                    for i, awaiting_element in enumerate(awaiting_elements):
                        if awaiting_element.depth > depth:
                            left_tag.append(awaiting_element)
                            indexes_to_remove.append(i)
                    for index in sorted(indexes_to_remove, reverse=True):
                        del awaiting_elements[index]

                    if depth == 0:
                        return left_tag
                    else:
                        if not awaiting_elements:
                            awaiting_elements = [left_tag]
                        else:
                            awaiting_elements.append(left_tag)
                else:
                    if not element.paired:  # if element is a non-pairing or self closing tag.
                        element.depth = depth
                        awaiting_elements.append(element)
                    else:
                        depth += 1
                        if element.name in open_tags:
                            open_tags[element.name].append(element)
                        else:
                            open_tags[element.name] = [element]

    @staticmethod
    def _parse_element(string, pos):
        element = Element()

        left_pos = string.find('<', pos)
        space_pos = string.find(' ', left_pos+1)
        right_bracket_pos = string.find('>', left_pos+1)
        if left_pos == -1 or right_bracket_pos == -1:
            return Element(), -1

        content = string[right_bracket_pos+1:string.find('<', right_bracket_pos+1)]
        element.append(content)

        element.paired = False if string[right_bracket_pos-1] in ['/', '-'] else True

        if right_bracket_pos < space_pos or space_pos == -1:
            element.name = string[left_pos+1:right_bracket_pos]
        else:
            attr_string = string[left_pos:right_bracket_pos]
            attr_list = [attr.strip('"') for attr in attr_string.split('" ')]

            try:
                tag_name, first_attr = attr_list[0].split(' ', 1)
                element.name = tag_name[1:]
                attr_list[0] = first_attr
            except ValueError:
                print('E2', attr_list[0])
                return Element(), -1

            tag_attributes = dict()
            for attribute in attr_list:
                if attribute in ['', '/', '/"', '"']:
                    continue
                try:
                    name, value = attribute.split('=', 1)
                    tag_attributes[name] = value.strip('"')
                except ValueError:
                    print('E1', attribute)
            element.attributes = tag_attributes
        return element, right_bracket_pos


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

    def __str__(self):
        text = ''
        for content in self.content:
            if isinstance(content, str):
                print(content)
                text += content
            if isinstance(content, Element):
                text += str(content)
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
html = wiki_parser.elements
table = html.get_elements('table')[0]
wiki_parser.parse_std_list(table)
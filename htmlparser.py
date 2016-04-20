import requests

wiki_url = 'https://en.wikipedia.org/wiki/List_of_elements'
non_paired_tags = ['area', 'base', 'br', 'col', 'command',
                   'embed', 'hr', 'img', 'input', 'link',
                   'meta', 'param', 'source', 'wbr', 'keygen',
                   'track', 'button']

# todo: remove docstring


def parse_from_url(url):
    page = requests.get(url)
    html_string = page.content.decode('utf-8')
    return parse_from_string(html_string)


def parse_from_file(filename):
    with open(filename, 'r') as file:
        html_string = file.read()
        file.close()
    return parse_from_string(html_string)


def parse_from_string(html_string):
    # Compress the string to a single line:
    new_string = ''
    for line in html_string.split('\n'):
        new_string += line.strip()
    html_string = new_string

    chunk_size = 80
    super_chunk = ''
    pos = 0
    for chunk in (html_string[i:i+chunk_size] for i in range(0, len(html_string)+1, chunk_size)):
        super_chunk += chunk
        while pos != -1:
            element, pos = _parse_chunk(super_chunk)
            print(element.name)
            if pos != -1:
                super_chunk = super_chunk[pos:]


def _parse_chunk(chunk):
    left_pos = chunk.find('<')
    right_pos = chunk.find('>', left_pos)+1
    next_left = chunk.find('<', right_pos)

    text = chunk[right_pos:next_left]
    tag_string = chunk[left_pos+1:right_pos-1]
    attribute_strings = tag_string.split(' ')
    tag_name = attribute_strings.pop(0)

    attributes_dict = dict()
    for attribute in attribute_strings:
        try:
            key, value = attribute.split('=', 1)
        except ValueError:
            key, value = attribute, ''
        attributes_dict[key] = value.strip('"')

    element = Element(name=tag_name, text=text, attributes=attributes_dict)
    if element.name == '/html':
        return element, 0
    return element, right_pos


class Element:
    def __init__(self, name='', depth=-1, attributes=None, content=None, paired=None, text=''):
        self.attributes = dict()
        self.content = list()
        self.name = name
        self.depth = depth
        self.paired = paired
        self.text = text
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
        text = self.text
        for content in self.content:
            text += content.to_text()
        return text

    def __str__(self):
        content_string = ''
        for item in self.content:
            content_string += str(item)
        return '<' + self.name + ' ' + str(self.attributes) + '>\n' + content_string


print(parse_from_file('files/test.html'))

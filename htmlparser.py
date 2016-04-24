import requests

wiki_url = 'https://en.wikipedia.org/wiki/List_of_elements'
non_paired_tags = ['area', 'base', 'br', 'col', 'command',
                   'embed', 'hr', 'img', 'input', 'link',
                   'meta', 'param', 'source', 'wbr', 'keygen',
                   'track', 'button']


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
    def to_tag_strings(html_str):
        left_pos = html_str.find('<')
        while left_pos != -1:
            right_pos = html_str.find('>', left_pos)
            if right_pos == -1:
                raise ValueError('String could not be parsed as HTML text. Last tag has no ending')
            tag_str = html_str[left_pos+1:right_pos]
            next_left = html_str.find('<', right_pos)
            content_str = html_str[right_pos+1:next_left]
            yield tag_str, content_str
            left_pos = next_left

    # Compress the string to a single line:
    new_string = ''
    for line in html_string.split('\n'):
        new_string += line.strip()
    html_string = new_string

    depth = 0
    open_tags = dict()
    awaiting_elements = set()
    for tag_string, plain_text in to_tag_strings(html_string):
        element = _parse_to_element(tag_string, plain_text)

        if element.name[0] == '/':  # if element is closing tag
            depth -= 1
            element.name = element.name[1:]
            try:
                starting_element = open_tags[element.name].pop()
            except KeyError:
                raise ValueError('String could not be parsed as HTML text. '
                                 'It contains ending tags without corresponding starting tags')
            starting_element.depth = depth

            for awaiting_element in set(awaiting_elements):
                if awaiting_element.depth > depth:
                    starting_element.content.append(awaiting_element)
                    awaiting_elements.remove(awaiting_element)

            awaiting_elements.add(starting_element)
        else:  # if element is not a closing tag
            if element.name == '!DOCTYPE':
                continue
            if element.paired:
                depth += 1
                if element.name in open_tags:
                    open_tags[element.name].append(element)
                else:
                    open_tags[element.name] = [element]
            else:
                element.depth = depth
                awaiting_elements.add(element)
    return awaiting_elements.pop()


def _parse_to_element(tag_string, text=''):
    attribute_strings = tag_string.split(' ')
    tag_name = attribute_strings.pop(0)

    if tag_name in non_paired_tags:
        paired = False
    else:
        paired = True

    # Parse the attributes of the tag:
    attributes_dict = dict()
    for attribute in attribute_strings:
        try:
            key, value = attribute.split('=', 1)
        except ValueError:
            key, value = attribute, ''
        attributes_dict[key] = value.strip('"')

    return Element(name=tag_name, text=text, attributes=attributes_dict, paired=paired)


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
        return '<' + self.name + ' ' + str(self.attributes) + '>\n' + self.text + content_string + '</' + self.name + '>\n'


# print(parse_from_file('files/test.html'))
print(parse_from_url(wiki_url))

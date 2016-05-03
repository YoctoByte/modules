import requests

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
    awaiting_elements = list()
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

            new_awaiting_elements = list()
            for awaiting_element in awaiting_elements:
                if awaiting_element.depth > depth:
                    starting_element.content.append(awaiting_element)
                else:
                    new_awaiting_elements.append(awaiting_element)
            awaiting_elements = new_awaiting_elements
            awaiting_elements.append(starting_element)
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
                awaiting_elements.append(element)
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
        for content in self.content:
            if content.name == elem_name:
                elements.append(content)
            if recursive:
                elements.extend(content.get_elements(elem_name))
        return elements

    def remove(self, name=None, attribute=None, recursive=True):
        # First some pre-processing of the arguments:
        if not name and not attribute:
            return

        # The function that check whether or not the attribute is in the content item:
        def attr_match(cont_attrs):
            if not attribute:
                return True
            if not cont_attrs:
                return False
            try:
                key, value = attribute[0], attribute[1]
            except IndexError:
                raise ValueError('attributes should be a pair (tuple, list, .. ).')
            if key == '*' and value == '*':
                return True
            if key == '*':
                for k in cont_attrs:
                    if cont_attrs[k] == value:
                        return True
                return False
            else:
                if key in cont_attrs and value == '*':
                    return True
                elif key in cont_attrs:
                    if cont_attrs[key] == value:
                        return True
                    else:
                        return False
                else:
                    return False

        for i, content in enumerate(self.content):
            if (content.name == name or not name) and attr_match(content.attributes):
                del self.content[i]
                continue
            if recursive:
                content.remove(name=name, attribute=attribute, recursive=recursive)

    def append(self, item):
        self.content.append(item)

    def extend(self, item):
        self.content.extend(item)

    def __iter__(self):
        for item in self.content:
            yield item

    def __getitem__(self, index):
        return self.content[index]

    def to_text(self, exclude=None):
        if not exclude:
            exclude = []
        if isinstance(exclude, str):
            exclude = [exclude]

        text = self.text

        if self.name == 'br':
            text = '\n' + text
        if self.name == 'title':
            return ''

        for content in self.content:
            if content.name not in exclude:
                text += content.to_text()
        return text

    @staticmethod
    def _indent(string):
        new_string = ''
        for line in (line for line in string.split('\n') if line):
            line = '    ' + line + '\n'
            new_string += line
        return new_string

    def __str__(self):
        content_string = ''
        for element in self:
            content_string += str(element)
        content_string = self._indent(content_string)

        attr_string = ''
        for attr in self.attributes:
            attr_string += ' ' + attr + '="' + self.attributes[attr] + '"'

        text = self.text

        end_tag = ''
        if self.paired:
            end_tag = '</' + self.name + '>\n'

        return '<' + self.name + attr_string + '>\n' + text + content_string + end_tag

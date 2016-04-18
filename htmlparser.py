import requests
from collections import namedtuple


wiki_url = 'https://en.wikipedia.org/wiki/List_of_elements'  # 'https://en.wikipedia.org/wiki/Hydrogen'  #
Tag = namedtuple('Tag', ['name', 'attributes', 'content', 'depth', 'paired'])


class Parser:
    def __init__(self, url):
        self.url = url
        page = requests.get(self.url)
        self.content = page.content.decode('utf-8')
        self.remove_comments()
        if self.content[:15] == '<!DOCTYPE html>':
            self.content = self.content.split('\n', 1)[1]
        self.tag_structure = self._make_tag_structure()

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

    @staticmethod
    def _parse_tag(string, pos):
        left_pos = string.find('<', pos)
        if left_pos == -1:
            return {}, -1

        space_pos = string.find(' ', left_pos+1)
        right_bracket_pos = string.find('>', left_pos+1)

        content = string[right_bracket_pos+1:string.find('<', right_bracket_pos+1)]
        if content:
            tag_content = [content]
        else:
            tag_content = []

        if string[right_bracket_pos-1] in ['/', '-']:
            paired = False
        else:
            paired = True

        tag_attributes = dict()
        if (right_bracket_pos < space_pos and right_bracket_pos != -1) or space_pos == -1:
            tag_name = string[left_pos+1:right_bracket_pos]
        else:
            attr_string = string[left_pos:right_bracket_pos]
            attr_list = [attr for attr in attr_string.split('" ')]

            try:
                tag_name, first_attr = attr_list[0].split(' ', 1)
                tag_name = tag_name[1:]
                attr_list[0] = first_attr
            except ValueError:
                print('E2 - ', attr_list[0])
                return None, -1

            for attribute in attr_list:
                if attribute not in ['', '/', '/"', '"']:
                    try:
                        name, value = attribute.split('=', 1)
                        tag_attributes[name] = value.strip('"')
                    except ValueError:
                        print('E1 - ', attribute)

        tag = Tag(tag_name, tag_attributes, tag_content, -1, paired)
        return tag, right_bracket_pos

    def _make_tag_structure(self):
        open_tags = dict()
        awaiting_tags = list()
        depth = 0
        for line in self.content.split('\n'):
            pos = -1
            while True:
                tag, pos = self._parse_tag(line, pos+1)
                if pos == -1:
                    break

                if tag.name[0] == '/':
                    depth -= 1
                    left_tag = open_tags[tag.name[1:]].pop()
                    content = left_tag.content
                    for awaiting_tag in awaiting_tags:
                        content.append(awaiting_tag)
                    awaiting_tags = list()
                    tag = Tag(left_tag.name, left_tag.attributes, content, depth, True)
                    if depth == 0:
                        return tag
                    else:
                        awaiting_tags.append(tag)
                else:
                    if not tag.paired:
                        tag = (tag.name, tag.attributes, tag.content, depth, tag.paired)
                        awaiting_tags.append(tag)
                    else:
                        depth += 1
                        if tag.name not in open_tags.keys():
                            open_tags[tag.name] = [tag]
                        else:
                            open_tags[tag.name].append(tag)

    def get_tag(self, tag_structure, tag_name, recursive=True):
        tags = list()
        for content in tag_structure.content:
            if isinstance(content, Tag):
                if content.name == tag_name:
                    tags.append(content)
                if recursive:
                    tags.extend(self.get_tag(content, tag_name))
        return tags

    def remove_tag(self, tag_structure, tag_name, recursive=True):
        tag_content = tag_structure.content
        for i, content in tag_content:
            if isinstance(content, Tag):
                if content.name == tag_name:
                    del tag_content[i]
                elif recursive:
                    tag_content[i] = self.remove_tag(content, tag_name)
        tag = Tag(tag_structure.name, tag_structure.attributes, tag_content, tag_structure.depth, tag_structure.paired)
        return tag

    def get_content_text(self, tag_structure):
        text = ''
        for content in tag_structure.content:
            if isinstance(content, str):
                text += content
            if isinstance(content, Tag):
                text += self.get_content_text(content)
        return text


class WikiParser(Parser):
    def __init__(self, url):
        Parser.__init__(self, url)

    def parse_std_list(self, table):
        def row_ok(r):
            if r.name != 'tr':
                return False
            for seq in ['9e99', '&#160']:
                if seq in self.get_content_text(r):
                    return False
            return True

        table = self.remove_tag(table, 'sup')
        for row in (r for r in table.content if row_ok(r)):
            print(row)


wiki_parser = WikiParser(wiki_url)
html = wiki_parser.tag_structure[0]
# print(html)
body = wiki_parser.get_tag(html, 'body')[0]
main_table = wiki_parser.get_tag(body, 'table')[0]
# for row in main_table['tag_content']:
#    print(wiki_parser.get_content_text(row))
wiki_parser.parse_std_list(main_table)
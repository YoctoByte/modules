import requests


wiki_url = 'https://en.wikipedia.org/wiki/List_of_elements'  # 'https://en.wikipedia.org/wiki/Hydrogen'  #


class HTMLParser:
    def __init__(self, url):
        self.url = url
        page = requests.get(self.url)
        self.content = page.content.decode('utf-8')
        self.remove_comments()
        if self.content[:15] == '<!DOCTYPE html>':
            self.content = self.content.split('\n', 1)[1]
        self.tag_structure = self._parse()

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
        tag = Tag({'name': None})

        left_pos = string.find('<', pos)
        space_pos = string.find(' ', left_pos+1)
        right_bracket_pos = string.find('>', left_pos+1)
        if left_pos == -1 or right_bracket_pos == -1:
            return tag, -1

        content = string[right_bracket_pos+1:string.find('<', right_bracket_pos+1)]
        tag['content'] = [content]

        if string[right_bracket_pos-1] in ['/', '-']:
            tag['non-pair'] = True

        tag_attributes = dict()
        if right_bracket_pos < space_pos or space_pos == -1:
            tag['name'] = string[left_pos+1:right_bracket_pos]
        else:
            attr_string = string[left_pos:right_bracket_pos]
            attr_list = [tag+'"' for tag in attr_string.split('" ')]

            try:
                tag_name, first_attr = attr_list[0].split(' ', 1)
                tag['name'] = tag_name[1:]
                attr_list[0] = first_attr
            except ValueError:
                print('E2', attr_list[0])
                return {}, -1

            for attribute in attr_list:
                if attribute in ['', '/', '/"', '"']:
                    continue
                try:
                    name, value = attribute.split('=', 1)
                    tag_attributes[name] = value.strip('"')
                except ValueError:
                    print('E1', attribute)
        tag['attributes'] = tag_attributes
        return tag, right_bracket_pos

    def _parse(self):
        open_tags = dict()
        awaiting_tags = list()
        depth = 0
        for line in self.content.split('\n'):
            pos = -1
            while True:
                tag, pos = self._parse_tag(line, pos+1)
                if pos == -1:
                    break

                if tag['name'][0] == '/':
                    depth -= 1
                    left_tag = open_tags[tag['name'][1:]].pop()

                    indexes_to_remove = list()
                    for i, awaiting_tag in enumerate(awaiting_tags):
                        if awaiting_tag['depth'] == depth:
                            left_tag['content'].append(awaiting_tag)
                            indexes_to_remove.append(i)
                    for index in sorted(indexes_to_remove, reverse=True):
                        del awaiting_tags[index]

                    left_tag['depth'] = depth
                    if depth == 0:
                        return left_tag
                    else:
                        awaiting_tags.append(left_tag)
                else:
                    if 'non-pair' in tag.keys():
                        del tag['non-pair']
                        tag['depth'] = depth
                        awaiting_tags.append(tag)
                    else:
                        depth += 1
                        if tag['name'] not in open_tags.keys():
                            open_tags[tag['name']] = [tag]
                        else:
                            open_tags[tag['name']].append(tag)


class Tag(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(*args, **kwargs)

    def get_tag(self, tag_name, recursive=True):
        tags = list()
        for content in self['content']:
            if isinstance(content, Tag):
                if content['name'] == tag_name:
                    tags.append(content)
                if recursive:
                    tags.extend(content.get_tag(tag_name))
        return tags

    def remove_tag(self, tag_name, recursive=True):
        for i, content in enumerate(self['tag_content']):
            if isinstance(content, Tag):
                if content['name'] == tag_name:
                    del self['tag_content'][i]
                elif recursive:
                    content.remove_tag(tag_name)

    def str__(self):
        text = ''
        for content in self['content']:
            if isinstance(content, str):
                print(content)
                text += content
            if isinstance(content, Tag):
                text += str(content)
        return text


class WikiParser(HTMLParser):
    def __init__(self, url):
        HTMLParser.__init__(self, url)

    def parse_std_list(self, table):
        def row_ok(r):
            if r['tag_name'] != 'tr':
                return False
            for seq in ['9e99', '&#160']:
                if seq in str(r):
                    return False
            return True

        table.remove_tag('sup')
        for row in (r for r in table['tag_content'] if row_ok(r)):
            print(row)


wiki_parser = WikiParser(wiki_url)
html = wiki_parser.tag_structure
# print(html)
print('test1')
print(wiki_parser.tag_structure)
body = wiki_parser.tag_structure.get_tag('body', recursive=False)
print(body)
print('test2')
for item in body['content']:
    print(item)
# main_table = body.get_tag('table')[0]
# print('test3')
# for row in main_table['tag_content']:
#    print(wiki_parser.get_content_text(row))
# wiki_parser.parse_std_list(main_table)
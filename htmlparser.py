import requests


wiki_url = 'https://en.wikipedia.org/wiki/List_of_elements'  # 'https://en.wikipedia.org/wiki/Hydrogen'  #


class Parser:
    def __init__(self, url):
        self.url = url
        page = requests.get(self.url)
        self.content = page.content.decode('utf-8')
        self.remove_comments()
        if self.content[:15] == '<!DOCTYPE html>':
            self.content = self.content.split('\n', 1)[1]
        self.tag_structure = self.parse_to_dicts()

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
    def get_tag_info(string, pos, line):
        left_pos = string.find('<', pos)
        if left_pos == -1:
            return {}, -1

        space_pos = string.find(' ', left_pos+1)
        right_bracket_pos = string.find('>', left_pos+1)

        tag_dict = dict()
        content = string[right_bracket_pos+1:string.find('<', right_bracket_pos+1)]
        if content:
            tag_dict['tag_content'] = [content]
        else:
            tag_dict['tag_content'] = []

        if string[right_bracket_pos-1] in ['/', '-']:
            tag_dict['non-pair'] = True

        if (right_bracket_pos < space_pos and right_bracket_pos != -1) or space_pos == -1:
            tag_name = string[left_pos+1:right_bracket_pos]
            tag_dict['tag_name'] = tag_name
            return tag_dict, right_bracket_pos
        else:
            tag_dict['tag_attributes'] = dict()
            tag_string = string[left_pos:right_bracket_pos]
            tag_list = [tag+'"' for tag in tag_string.split('" ')]

            try:
                tag_name, first_attr = tag_list[0].split(' ', 1)
                tag_dict['tag_name'] = tag_name[1:]
                tag_list[0] = first_attr
            except ValueError:
                print('E2', line, tag_list[0])
                return {}, -1

            for attribute in tag_list:
                if attribute not in ['', '/', '/"', '"']:
                    try:
                        name, value = attribute.split('=', 1)
                        tag_dict['tag_attributes'][name] = value.strip('"')
                    except ValueError:
                        print('E1', line, attribute)
            return tag_dict, right_bracket_pos

    def parse_to_dicts(self):
        tags = list()
        open_tags = dict()
        awaiting_tags = list()
        depth = 0
        for i, line in enumerate(self.content.split('\n')):
            pos = -1
            while True:
                tag_dict, pos = self.get_tag_info(line, pos+1, i)
                if pos == -1:
                    break
                tag_name = tag_dict['tag_name']
                if tag_name[0] == '/':
                    depth -= 1
                    tag_name = tag_name[1:]
                    tag = open_tags[tag_name].pop()
                    indexes_to_remove = list()
                    for i, awaiting_tag in enumerate(awaiting_tags):
                        if awaiting_tag['depth'] == depth+1:
                            tag['tag_content'].append(awaiting_tag)
                            indexes_to_remove.append(i)
                    for index in sorted(indexes_to_remove, reverse=True):
                        del awaiting_tags[index]
                    tag['depth'] = depth
                    if depth == 0:
                        tags.append(tag)
                    else:
                        awaiting_tags.append(tag)
                else:
                    if 'non-pair' in tag_dict.keys():
                        del tag_dict['non-pair']
                        tag_dict['depth'] = depth
                        awaiting_tags.append(tag_dict)
                    else:
                        depth += 1
                        if tag_name not in open_tags.keys():
                            open_tags[tag_name] = [tag_dict]
                        else:
                            open_tags[tag_name].append(tag_dict)
        return tags

    def get_tag(self, tag_structure, tag_name, recursive=True):
        tags = list()
        for content in tag_structure['tag_content']:
            if isinstance(content, dict):
                if content['tag_name'] == tag_name:
                    tags.append(content)
                if recursive:
                    tags.extend(self.get_tag(content, tag_name))
        return tags

    def remove_tag(self, tag_structure, tag_name, recursive=True):
        for i, content in enumerate(tag_structure['tag_content']):
            if isinstance(content, dict):
                if content['tag_name'] == tag_name:
                    del tag_structure['tag_content'][i]
                elif recursive:
                    tag_structure['tag_content'][i] = self.remove_tag(content, tag_name)
        return tag_structure

    def get_content_text(self, tag_structure):
        text = ''
        for content in tag_structure['tag_content']:
            if isinstance(content, str):
                text += content
            if isinstance(content, dict):
                text += self.get_content_text(content)
        return text


class TagStructure:
    def __init__(self, tag):
        pass


class WikiParser(Parser):
    def __init__(self, url):
        Parser.__init__(self, url)

    def parse_std_list(self, table):
        def row_ok(r):
            if r['tag_name'] != 'tr':
                return False
            for seq in ['9e99', '&#160']:
                if seq in self.get_content_text(r):
                    return False
            return True

        table = self.remove_tag(table, 'sup')
        for row in (r for r in table['tag_content'] if row_ok(r)):
            print(row)


wiki_parser = WikiParser(wiki_url)
html = wiki_parser.tag_structure[0]
# print(html)
body = wiki_parser.get_tag(html, 'body')[0]
main_table = wiki_parser.get_tag(body, 'table')[0]
# for row in main_table['tag_content']:
#    print(wiki_parser.get_content_text(row))
wiki_parser.parse_std_list(main_table)
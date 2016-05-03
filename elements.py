from fileparser import parse_from_string


class Elements:
    pass

new_elements = list()
with open('files/elements.txt') as file:
    for line in file:
        new_element = dict()
        element = parse_from_string(line)
        for key in element:
            if key in ['Origin of name']:
                continue
            if key in ['Melt', 'Boil', 'Heat', 'Neg', 'Abundance', 'Density', 'Atomic weight', 'Period', 'Group']:
                if type(element[key]) not in [int, float] and element[key] is not None:
                    print(element['Element'] + ': ' + key + ' = ' + str(element[key]))
            new_element[key.lower()] = element[key]
        new_elements.append(new_element)
    file.close()

with open('files/new_elements', 'w') as file:
    for element in new_elements:
        file.write(str(element) + '\n')
    file.close()

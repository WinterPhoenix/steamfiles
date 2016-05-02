from collections import OrderedDict

SECTION_START = '{'
SECTION_END = '}'


def loads(content):
    if not isinstance(content, str):
        raise TypeError('can only load a str as an ACF')

    data = OrderedDict()
    current_section = data
    sections = []

    lines = (line.replace('"', '').strip() for line in content.splitlines())
    for line in lines:
        try:
            key, value = line.split(None, 1)
        except ValueError:
            if line == SECTION_START:
                # Initialize the last added section.
                current_section = _prepare_subsection(data, sections)
            elif line == SECTION_END:
                # Remove the last section from the queue.
                sections.pop()
            else:
                # Add a new section to the queue.
                sections.append(line)
            continue

        current_section[key] = value

    return data


def load(fp):
    return loads(fp.read())


def dumps(obj):
    if not isinstance(obj, dict):
        raise TypeError('can only dump a dictionary as an ACF')

    return '\n'.join(_dumps(obj, level=0)) + '\n'


def dump(obj, fp):
    fp.write(dumps(obj))


def _dumps(obj, level):
    lines = []
    indent = '\t' * level

    for key, value in obj.items():
        if isinstance(value, dict):
            # [INDENT]"KEY"
            # [INDENT]{
            line = indent + '"{}"\n'.format(key) + indent + '{'
            lines.append(line)
            # Increase intendation of the nested dict
            lines.extend(_dumps(value, level+1))
            # [INDENT]}
            lines.append(indent + '}')
        else:
            # [INDENT]"KEY"[TAB][TAB]"VALUE"
            lines.append(indent + '"{}"'.format(key) + '\t\t' + '"{}"'.format(value))

    return lines


def _prepare_subsection(data, sections):
    current = data
    for i in sections[:-1]:
        current = current[i]

    current[sections[-1]] = OrderedDict()
    return current[sections[-1]]

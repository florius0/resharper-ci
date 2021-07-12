#!/usr/bin/python3

import os
import re
import sys
import json
import rich

from pathlib import Path
from collections import namedtuple, defaultdict
import xml.etree.ElementTree as et

import rich
from rich.tree import Tree

DRY_RUN = False


def build(settings):
    if settings.build:
        return run(
            f'dotnet build {settings.solution}',
            ' > /dev/null' if settings.hide else ''
        )
    return 0


def inspectcode(settings):
    return run(
        'jb inspectcode',
        settings.solution,
        f'--include={";".join(settings.include)}' if settings.include else '',
        f'--exclude={";".join(settings.exclude)}' if settings.exclude else '',
        f'--severity={settings.severity}' if settings.severity else '',
        '-o=inspection.xml > /dev/null',
        ' > /dev/null' if settings.hide else ''
    )


def process_inspectcode_output(settings):
    END_MARKER = '<END>'

    def issue_object_hook(i):
        v = dict(i.attrib)
        v['File'] = Path(v['File'].replace('\\', '/')).parts
        return dict_to_obj('Issue', v)

    def attach(parts, obj, trunk):
        if len(parts) == 1:
            if(END_MARKER in trunk.keys()):
                trunk[END_MARKER].append((parts[0], obj))
            else:
                trunk[END_MARKER] = [(parts[0], obj)]
        else:
            node, *others = parts
            if node not in trunk:
                trunk[node] = defaultdict(dict)
            attach(others, obj, trunk[node])

    def tree(l, key=lambda x: x):
        main_dict = defaultdict(dict)

        for line in l:
            attach(key(line), line, main_dict)

        return main_dict

    def walk_tree(t, tree):
        def issue_to_str(issue):
            line = getattr(issue, 'Line', '')
            return f"{issue.Message} ({issue.TypeId}):{line}" if line else f"{issue.Message} ({issue.TypeId})o:{issue.Offset}"

        def render_list_of_issues(fname, list):
            tt = Tree(fname)
            for l in list:
                tt.add(issue_to_str(l))

            return tt

        for k, v in t.items():
            if k == END_MARKER:
                d = defaultdict(list)
                [d[kk].append(vv) for kk, vv in v]
                [tree.add(render_list_of_issues(*i)) for i in d.items()]
            else:
                branch = tree.add(k)
                walk_tree(t[k], branch)

    issues = [issue_object_hook(i) for i in et.parse('inspection.xml').findall(
        './Issues/*/Issue') if i.get('TypeId') not in settings.discard_issues]

    def k(x): return x.File
    s = sorted(issues, key=k)

    t = Tree(f"{len(issues)} issues in {settings.solution}")
    walk_tree(tree(s, key=k), t)

    rich.print(t)
    rich.print(t, file=open('inspection.txt', 'w'))

    return len(issues)


def settings_object_hook(d):
    def split_scsv(s):
        return [v for v in re.split(r"\;+\s+", s) if v]

    x = {}
    x['solution'] = d['solution']
    x['include'] = split_scsv(get(d, 'include'))
    x['exclude'] = split_scsv(get(d, 'exclude'))
    x['discard_issues'] = split_scsv(get(d, 'discard-issues'))
    x['severity'] = get(d, 'severity')
    x['build'] = get(d, 'build', True)
    x['hide'] = get(d, 'hide-output', True)
    return dict_to_obj('settings', x)


def dict_to_obj(type, dict):
    return namedtuple(type, dict.keys())(*dict.values())


def run(*command):
    cmd = ' '.join([c for c in command if c])

    if DRY_RUN:
        print(cmd)
        return 0
    else:
        return os.system(cmd)


def get(dictionaty, key, default=''):
    return dictionaty[key] if key in dictionaty.keys() else default


pipeline = [
    build,
    inspectcode,
    process_inspectcode_output,
]

if __name__ == '__main__':
    settings = json.loads(sys.argv[1], object_hook=settings_object_hook)
    sys.exit(max([x(settings) for x in pipeline]) > 1)

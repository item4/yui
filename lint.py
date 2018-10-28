"""
This script provide linting about contents of __all__ tuple and
imported items of __init__ modules.
"""
import ast
import sys
from pathlib import Path

import _ast

# I want to extract from below def stmt
DEFS = (_ast.ClassDef, _ast.FunctionDef, _ast.AsyncFunctionDef)

# I want to ignore them
IGNORES = [
    '__pycache__',
]

# I want to exclude item if part of path has below keywords
EXCLUDES_PART1 = [
    'migrations',
    'templates',
    '__init__.py',
]

# I want to check below modules in yui.apps
INCLUDES_APPS = [
    'models',
    'utils',
]
INCLUDES_APPS += [f'{x}.py' for x in INCLUDES_APPS]


def error(message: str, valid_all_tuple_tuple=None):
    """Print error and shutdown"""

    print(message, file=sys.stderr)
    if valid_all_tuple_tuple:
        print(make_all_tuple_str(valid_all_tuple_tuple), file=sys.stderr)
    raise SystemExit(1)


def make_all_tuple_str(names) -> str:
    """Make __all__ tuple str"""

    return (
        '__all__ = (\n' +
        '\n'.join(f"    '{x}'," for x in names) +
        '\n)\n'
    )


def make_import_stmt_str(module, names):
    """Make import stmt str"""

    return (
        f'from .{module} import (\n' +
        ',\n'.join(
            f'    {x}' for x in sorted(names)
        ) +
        ',\n)\n'
    )


def check_common_module(path: Path):
    """Check common(!=__init__.py) modules"""

    body = ast.parse(path.open().read()).body
    valid_all_tuple = get_names_from_body(body)
    current_all_tuple = get_current_all_tuple_from_body(body)
    if current_all_tuple:
        if valid_all_tuple != current_all_tuple:
            error(f'{path} has wrong __all__ tuple.', valid_all_tuple)
    else:
        error(f'{path} has no __all__ tuple.', valid_all_tuple)


def get_current_all_tuple_from_body(body):
    """Get already-defined __all__ tuple in given source."""

    for node in body:
        if isinstance(node, _ast.Assign):
            for n in node.targets:
                if isinstance(n, _ast.Name):
                    if n.id == '__all__':
                        return tuple(x.s for x in node.value.elts)


def get_parent_module_names_set(path):
    """Get names of sibling module."""

    return {
        x.name.replace('.py', '')
        for x in path.parent.glob('*')
        if x != path and x.name not in IGNORES
    }


def check_init_module(path):
    """Check __init__ modules."""

    parent = path.parent
    body = ast.parse(path.open().read()).body
    current_all_tuple = get_current_all_tuple_from_body(body)
    all_names = get_imported_item_names_from_body(body)
    modules = get_imported_modules_from_body(body)

    # check __init__ was imported all submodules
    family_module_names_set = get_parent_module_names_set(path)
    imported_module_names_set = {x[0] for x in modules}
    if family_module_names_set != imported_module_names_set:
        miss = ', '.join(family_module_names_set ^ imported_module_names_set)
        error(f'{path} did not import some modules: {miss}')

    # check __init__ was import all items in submodules
    valid_all_tuple = tuple(
        sorted(
            [y for x in all_names.values() for y in x.values()] +
            list(get_names_from_body(body))
        )
    )
    for module, c in modules:
        if c:
            current_names = set(all_names[module].keys())
            f = parent / f'{module}.py'
            if f.exists():
                correct_names = set(get_names_from_path(f))
            else:
                f = parent / module / '__init__.py'
                inames = get_imported_item_names_from_body(
                    ast.parse(f.open().read()).body
                )
                correct_names = set(
                    y for x in inames.values() for y in x.values()
                )
            if current_names != correct_names:
                import_stmt = make_import_stmt_str(
                    module,
                    tuple(correct_names),
                )
                error(
                    f'{path} did not import some contents from {module}\n'
                    f'{import_stmt}'
                )

    # check __init__ has correct __all__
    if valid_all_tuple != current_all_tuple:
        if current_all_tuple:
            error(f'{path} has wrong __all__ tuple.', valid_all_tuple)
        else:
            error(f'{path} has no __all__ tuple.', valid_all_tuple)


def get_imported_modules_from_body(body):
    """Get name and status of imported modules."""

    result = []
    for node in body:
        if isinstance(node, _ast.ImportFrom):
            if node.module is None:
                for alias in node.names:
                    result.append((alias.name, False))
            else:
                result.append((node.module, True))
    return result


def get_imported_item_names_from_body(body):
    """Get imported module and item names."""

    result = {}
    for node in body:
        if isinstance(node, _ast.ImportFrom):
            for alias in node.names:
                if alias.asname is None:
                    if node.module not in result:
                        result[node.module] = {}
                    result[node.module][alias.name] = (
                        alias.asname if alias.asname else alias.name
                    )
    return result


def get_names_from_path(path):
    """Get defined variable, class, function names from path."""

    return get_names_from_body(ast.parse(path.open().read()).body)


def get_names_from_body(body):
    """Get defined variable, class, function names from path."""

    result = set()
    for node in body:
        if isinstance(node, DEFS):
            result.add(node.name)
        if isinstance(node, _ast.Assign):
            for n in node.targets:
                if isinstance(n, _ast.Name):
                    result.add(n.id)
        if isinstance(node, _ast.AnnAssign):
            if isinstance(node.target, _ast.Name):
                result.add(node.target.id)
    return tuple(sorted(x for x in result if not x.startswith('_')))


def main():
    for path in Path('yui').glob('**/*.py'):
        if any(p in IGNORES for p in path.parts):
            continue
        if path.parts[1] == 'apps':
            if path.name in INCLUDES_APPS:
                check_common_module(path)
            if any(p in INCLUDES_APPS for p in path.parts):
                check_common_module(path)
        elif path.parts[1] in EXCLUDES_PART1:
            continue
        elif path.name == '__init__.py':
            check_init_module(path)
        else:
            check_common_module(path)


if __name__ == '__main__':
    main()

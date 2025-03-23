import ast
import datetime
import functools
import html
import itertools
import math
import operator
import random
import statistics
from collections.abc import Callable
from typing import Any
from typing import Final

from more_itertools import numeric_range

from ....utils import json
from .exceptions import AsyncComprehensionError
from .exceptions import BadSyntax
from .exceptions import CallableKeywordsError
from .exceptions import NotCallableError
from .exceptions import NotIterableError
from .exceptions import NotSubscriptableError
from .exceptions import UnavailableSyntaxError
from .exceptions import UnavailableTypeError
from .exceptions import error_maker
from .types import Decimal
from .types import PLACEHOLDER
from .types import is_get_subscriptable
from .types import is_iterable
from .types import is_subscriptable

BINOP_TABLE: Final[dict[type[ast.operator], Callable[[Any, Any], Any]]] = {
    ast.Add: operator.add,
    ast.BitAnd: operator.and_,
    ast.BitOr: operator.or_,
    ast.BitXor: operator.xor,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.LShift: operator.lshift,
    ast.MatMult: operator.matmul,
    ast.Mult: operator.mul,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.RShift: operator.rshift,
    ast.Sub: operator.sub,
}
BOOLOP_TABLE: Final[dict[type[ast.boolop], Callable[[Any, Any], Any]]] = {
    ast.And: lambda a, b: a and b,
    ast.Or: lambda a, b: a or b,
}
COMPARE_TABLE: Final[dict[type[ast.cmpop], Callable[[Any, Any], bool]]] = {
    ast.Eq: operator.eq,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.In: lambda a, b: a in b,
    ast.Is: operator.is_,
    ast.IsNot: operator.is_not,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.NotEq: operator.ne,
    ast.NotIn: lambda a, b: a not in b,
}
UNARYOP_TABLE: Final[dict[type[ast.unaryop], Callable[[Any], Any]]] = {
    ast.Invert: operator.invert,
    ast.Not: operator.not_,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


class ScopeStack:
    stack: list[dict[str, Any]]

    def __init__(self) -> None:
        self.stack = [{}]

    def create_new_scope(self):
        self.stack.append({})

    def remove_top_scope(self):
        self.stack.pop()

    def __getitem__(self, item: str) -> Any:
        for scope in reversed(self.stack):
            try:
                return scope[item]
            except KeyError:
                continue
        raise NameError(item)

    def keys(self):
        yield from {key for scope in self.stack for key in scope}

    def items(self):
        for key in self.keys():
            yield key, self[key]

    def __bool__(self) -> bool:
        return any(self.keys())

    def __iter__(self):
        return self.keys()

    def __setitem__(self, key: str, value: Any) -> None:
        self.stack[-1][key] = value

    def __delitem__(self, key: str) -> None:
        try:
            self.stack[-1].pop(key)
        except KeyError as e:
            raise NameError(key) from e

    def __contains__(self, item: str) -> bool:
        return any(item in x for x in self.stack)

    def __enter__(self) -> None:
        self.create_new_scope()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.remove_top_scope()


class Evaluator:
    last_dump: str

    def __init__(self, *, decimal_mode: bool = False) -> None:
        self.decimal_mode = decimal_mode
        self.allowed_modules = {
            functools: {"reduce"},
            html: {"escape", "unescape"},
            itertools: {
                "accumulate",
                "chain",
                "chain.from_iterable",
                "compress",
                "dropwhile",
                "filterfalse",
                "groupby",
                "starmap",
                "takewhile",
                "tee",
                "zip_longest",
                "product",
                "permutations",
                "combinations",
                "combinations_with_replacement",
            },
            math: {
                "acos",
                "acosh",
                "asin",
                "asinh",
                "atan",
                "atan2",
                "atanh",
                "ceil",
                "copysign",
                "cos",
                "cosh",
                "degrees",
                "erf",
                "erfc",
                "exp",
                "expm1",
                "fabs",
                "factorial",
                "floor",
                "fmod",
                "frexp",
                "fsum",
                "gamma",
                "gcd",
                "hypot",
                "isclose",
                "isfinite",
                "isinf",
                "isnan",
                "ldexp",
                "lgamma",
                "log",
                "log1p",
                "log10",
                "log2",
                "modf",
                "pow",
                "radians",
                "sin",
                "sinh",
                "sqrt",
                "tan",
                "tanh",
                "trunc",
                "pi",
                "e",
                "tau",
                "inf",
                "nan",
            },
            operator: {
                "lt",
                "le",
                "eq",
                "ne",
                "ge",
                "gt",
                "not_",
                "truth",
                "is_",
                "is_not",
                "add",
                "and_",
                "floordiv",
                "index",
                "inv",
                "invert",
                "lshift",
                "mod",
                "mul",
                "matmul",
                "neg",
                "or_",
                "pos",
                "pow",
                "rshift",
                "sub",
                "truediv",
                "xor",
                "concat",
                "contains",
                "countOf",
                "delitem",
                "getitem",
                "indexOf",
                "setitem",
                "length_hint",
                "itemgetter",
            },
            random: {
                "randrange",
                "randint",
                "choice",
                "choices",
                "shuffle",
                "sample",
                "random",
                "uniform",
                "triangular",
                "betavariate",
                "expovariate",
                "gammavariate",
                "gauss",
                "lognormvariate",
                "normalvariate",
                "vonmisesvariate",
                "paretovariate",
                "weibullvariate",
            },
            statistics: {
                "mean",
                "harmonic_mean",
                "median",
                "median_low",
                "median_high",
                "median_grouped",
                "mode",
                "pstdev",
                "pvariance",
                "stdev",
                "variance",
            },
            json: {"dumps", "loads"},
        }
        self.allowed_class_properties = {
            bytes: {"fromhex", "maketrans"},
            datetime.date: {
                "today",
                "fromtimestamp",
                "fromordinal",
                "fromisoformat",
                "min",
                "max",
                "resolution",
            },
            datetime.datetime: {
                "today",
                "now",
                "utcnowfromtimestamp",
                "utcfromtimestamp",
                "fromordinal",
                "combine",
                "fromisoformat",
                "strptime",
                "min",
                "max",
                "resolution",
            },
            datetime.time: {"min", "max", "resolution", "fromisoformat"},
            datetime.timedelta: {"min", "max", "resolution"},
            datetime.timezone: {"utc"},
            dict: {"fromkeys"},
            float: {"fromhex"},
            int: {"from_bytes"},
            str: {"maketrans"},
        }
        self.allowed_instance_properties = {
            bytes: {
                "hex",
                "count",
                "decode",
                "endswith",
                "find",
                "index",
                "join",
                "partition",
                "replace",
                "rfind",
                "rindex",
                "rpartition",
                "startswith",
                "translate",
                "center",
                "ljust",
                "lstrip",
                "rjust",
                "rsplit",
                "rstrip",
                "split",
                "strip",
                "capitalize",
                "expandtabs",
                "isalnum",
                "isalpha",
                "isdigit",
                "islower",
                "isspace",
                "istitle",
                "isupper",
                "lower",
                "splitlines",
                "swapcase",
                "title",
                "upper",
                "zfill",
            },
            datetime.date: {
                "year",
                "month",
                "day",
                "replace",
                "timetuple",
                "toordinal",
                "weekday",
                "isoweekday",
                "isocalendar",
                "isoformat",
                "ctime",
                "strftime",
            },
            datetime.datetime: {
                "year",
                "month",
                "dayhour",
                "minute",
                "second",
                "microsecond",
                "tzinfo",
                "fold",
                "date",
                "time",
                "timetz",
                "replace",
                "astimezone",
                "dst",
                "tzname",
                "timetuple",
                "utctimetuple",
                "toordinal",
                "timestamp",
                "weekday",
                "isoweekday",
                "isocalendar",
                "isoformat",
                "ctime",
                "strftime",
            },
            datetime.time: {
                "hour",
                "minute",
                "second",
                "microsecond",
                "tzinfo",
                "fold",
                "replace",
                "isoformat",
                "strftime",
                "utcoffset",
                "dst",
                "tzname",
            },
            datetime.timedelta: {"total_seconds"},
            datetime.timezone: {"utcoffset", "tzname", "dst", "fromutc"},
            datetime.tzinfo: {"utcoffset", "dst", "tzname", "fromutc"},
            dict: {
                "copy",
                "get",
                "items",
                "keys",
                "pop",
                "popitem",
                "setdefault",
                "update",
                "values",
            },
            float: {"as_integer_ratio", "is_integer", "hex"},
            int: {"bit_length", "to_bytes"},
            list: {
                "index",
                "count",
                "append",
                "clear",
                "copy",
                "extend",
                "insert",
                "pop",
                "remove",
                "reverse",
                "sort",
            },
            range: {"start", "stop", "step"},
            numeric_range: {"start", "stop", "step"},
            str: {
                "capitalize",
                "casefold",
                "center",
                "count",
                "encode",
                "endswith",
                "expandtabs",
                "find",
                "format",
                "format_map",
                "index",
                "isalnum",
                "isalpha",
                "isdecimal",
                "isdigit",
                "isidentifier",
                "islower",
                "isnumeric",
                "isprintable",
                "isspace",
                "istitle",
                "isupper",
                "join",
                "ljust",
                "lower",
                "lstrip",
                "partition",
                "replace",
                "rfind",
                "rindex",
                "rjust",
                "rpartition",
                "rsplit",
                "rstrip",
                "split",
                "splitlines",
                "swapcase",
                "startswith",
                "strip",
                "title",
                "translate",
                "upper",
                "zfill",
            },
            set: {
                "isdisjoint",
                "issubset",
                "issuperset",
                "union",
                "intersection",
                "difference",
                "symmetric_difference",
                "copy",
                "update",
                "intersection_update",
                "difference_update",
                "symmetric_difference_update",
                "add",
                "remove",
                "discard",
                "pop",
                "clear",
            },
            tuple: {
                "index",
                "count",
                "append",
                "clear",
                "copy",
                "extend",
                "insert",
                "pop",
                "remove",
                "reverse",
            },
        }
        self.global_symbol_table: dict[str, Any] = {
            # builtin func
            "abs": abs,
            "all": all,
            "any": any,
            "ascii": ascii,
            "bin": bin,
            "bool": bool,
            "bytes": bytes,
            "chr": chr,
            "complex": complex,
            "dict": dict,
            "divmod": divmod,
            "enumerate": enumerate,
            "filter": filter,
            "float": float,
            "format": format,
            "frozenset": frozenset,
            "hex": hex,
            "int": int,
            "isinstance": isinstance,
            "issubclass": issubclass,
            "len": len,
            "list": list,
            "map": map,
            "max": max,
            "min": min,
            "oct": oct,
            "ord": ord,
            "pow": pow,
            "range": numeric_range if self.decimal_mode else range,
            "numeric_range": numeric_range,
            "repr": repr,
            "reversed": reversed,
            "round": round,
            "set": set,
            "slice": slice,
            "sorted": sorted,
            "str": str,
            "sum": sum,
            "tuple": tuple,
            "zip": zip,
            # additional type
            "Decimal": Decimal,
            # math shortcut
            "acos": math.acos,
            "acosh": math.acosh,
            "asin": math.asin,
            "asinh": math.asinh,
            "atan": math.atan,
            "atan2": math.atan2,
            "atanh": math.atanh,
            "ceil": math.ceil,
            "copysign": math.copysign,
            "cos": math.cos,
            "cosh": math.cosh,
            "degrees": math.degrees,
            "erf": math.erf,
            "erfc": math.erfc,
            "exp": math.exp,
            "expm1": math.expm1,
            "fabs": math.fabs,
            "factorial": math.factorial,
            "floor": math.floor,
            "fmod": math.fmod,
            "frexp": math.frexp,
            "fsum": math.fsum,
            "gamma": math.gamma,
            "gcd": math.gcd,
            "hypot": math.hypot,
            "isclose": math.isclose,
            "isfinite": math.isfinite,
            "isinf": math.isinf,
            "isnan": math.isnan,
            "ldexp": math.ldexp,
            "lgamma": math.lgamma,
            "log": math.log,
            "log1p": math.log1p,
            "log10": math.log10,
            "log2": math.log2,
            "modf": math.modf,
            "radians": math.radians,
            "sin": math.sin,
            "sinh": math.sinh,
            "sqrt": math.sqrt,
            "tan": math.tan,
            "tanh": math.tanh,
            "trunc": math.trunc,
            "pi": math.pi,
            "e": math.e,
            "tau": math.tau,
            "inf": math.inf,
            "nan": math.nan,
            # module level injection
            "functools": functools,
            "html": html,
            "itertools": itertools,
            "json": json,
            "math": math,
            "operator": operator,
            "random": random,
            "statistics": statistics,
        }
        self.scope = ScopeStack()
        self.current_interrupt: ast.Break | ast.Continue | None = None

    def run(self, expr: str):
        h = ast.parse(expr, mode="exec")
        self.last_dump = ast.dump(h)
        return self._run(h)

    def _run(self, node):
        if node is None:
            return None

        return getattr(
            self,
            f"visit_{node.__class__.__name__.lower()}",
            self.no_impl,
        )(node)

    def assign(self, node, val):
        if isinstance(node, ast.Name):
            self.scope[node.id] = val
        elif isinstance(node, (ast.Tuple, ast.List)):
            if not is_iterable(val):
                error_maker(NotIterableError, val)
            for telem, tval in itertools.zip_longest(
                node.elts,
                val,
                fillvalue=PLACEHOLDER,
            ):
                if telem == PLACEHOLDER:
                    error = "not enough values to unpack"
                    raise ValueError(error)
                if tval == PLACEHOLDER:
                    error = "too many values to unpack"
                    raise ValueError(error)
                self.assign(telem, tval)
        elif isinstance(node, ast.Subscript):
            sym = self._run(node.value)
            xslice = self._run(node.slice)
            if not is_subscriptable(sym):
                error_maker(NotSubscriptableError, sym)
            sym[xslice] = val
        else:
            error = "This assign method is not allowed"
            raise BadSyntax(error)

    def delete(self, node):
        if isinstance(node, ast.Name):
            del self.scope[node.id]
        elif isinstance(node, ast.Tuple):
            for elt in node.elts:
                self.delete(elt)

    def no_impl(self, node):
        raise NotImplementedError

    def visit_annassign(self, node: ast.AnnAssign):
        error_maker(UnavailableSyntaxError, node)

    def visit_assert(self, node: ast.Assert):
        error_maker(UnavailableSyntaxError, node)

    def visit_assign(self, node: ast.Assign):  # targets, value, type_comment
        value = self._run(node.value)
        for tnode in node.targets:
            self.assign(tnode, value)

    def visit_asyncfor(self, node: ast.AsyncFor):
        error_maker(UnavailableSyntaxError, node)

    def visit_asyncfunctiondef(self, node: ast.AsyncFunctionDef):
        error_maker(UnavailableSyntaxError, node)

    def visit_asyncwith(self, node: ast.AsyncWith):
        error_maker(UnavailableSyntaxError, node)

    def visit_attribute(self, node: ast.Attribute):  # value, attr, ctx
        value = self._run(node.value)
        t = type(value)
        try:
            if value in self.allowed_modules:
                if node.attr in self.allowed_modules[value]:
                    return getattr(value, node.attr)
                error = f"You can not access `{node.attr}` attribute"
                raise BadSyntax(error)
            if value in self.allowed_class_properties:
                if node.attr in self.allowed_class_properties[value]:
                    return getattr(value, node.attr)
                error = f"You can not access `{node.attr}` attribute"
                raise BadSyntax(error)
        except TypeError:
            pass
        if t in self.allowed_instance_properties:
            if node.attr in self.allowed_instance_properties[t]:
                return getattr(value, node.attr)
            error = f"You can not access `{node.attr}` attribute"
            raise BadSyntax(error)
        error = f"You can not access attributes of {t}"
        raise BadSyntax(error)

    def visit_augassign(self, node: ast.AugAssign):  # target, op, value
        value = self._run(node.value)
        target = node.target
        op_cls = node.op.__class__
        error = "This assign method is not allowed"

        if isinstance(target, ast.Name):
            target_id = target.id
            self.scope[target_id] = BINOP_TABLE[op_cls](
                self.scope[target_id],
                value,
            )
        elif isinstance(target, ast.Subscript):
            sym = self._run(target.value)
            if not is_subscriptable(sym):
                error_maker(NotSubscriptableError, sym)
            xslice = self._run(target.slice)
            if not isinstance(target.slice, (ast.Tuple, ast.Slice)):
                sym[xslice] = BINOP_TABLE[op_cls](
                    sym[xslice],
                    value,
                )
            else:
                raise BadSyntax(error)
        else:
            raise BadSyntax(error)

    def visit_await(self, node: ast.Await):
        error_maker(UnavailableSyntaxError, node)

    def visit_binop(self, node: ast.BinOp):  # left, op, right
        op = BINOP_TABLE.get(node.op.__class__)

        if op:
            return op(self._run(node.left), self._run(node.right))
        raise NotImplementedError

    def visit_boolop(self, node: ast.BoolOp):  # op, values
        op = BOOLOP_TABLE.get(node.op.__class__)

        if op:
            result = self._run(node.values[0])
            for x in node.values[1:]:
                result = op(result, self._run(x))
            return result
        raise NotImplementedError

    def visit_break(self, node: ast.Break):
        self.current_interrupt = node

    def visit_call(self, node: ast.Call):  # func, args, keywords
        func = self._run(node.func)
        args = [self._run(x) for x in node.args]
        keywords = {}
        for x in node.keywords:
            if not isinstance(x.arg, str):
                error_maker(CallableKeywordsError)
            keywords[x.arg] = self._run(x.value)
        if callable(func):
            return func(*args, **keywords)
        return error_maker(NotCallableError, func)

    def visit_compare(self, node: ast.Compare):  # left, ops, comparators
        lval = self._run(node.left)
        out = True
        for op, rnode in zip(node.ops, node.comparators, strict=True):
            rval = self._run(rnode)
            cmpop = COMPARE_TABLE.get(op.__class__)
            if cmpop:
                out = cmpop(lval, rval)
                lval = rval
            else:
                raise NotImplementedError
        return out

    def visit_constant(self, node: ast.Constant):  # value, kind
        if isinstance(node.value, complex):
            error_maker(UnavailableTypeError, node.value)
        if (
            self.decimal_mode
            and isinstance(node.value, (int, float))
            and not isinstance(node.value, bool)
        ):
            return Decimal(str(node.value))
        return node.value

    def visit_continue(self, node: ast.Continue):
        self.current_interrupt = node

    def visit_classdef(self, node: ast.ClassDef):
        error_maker(UnavailableSyntaxError, node)

    def visit_delete(self, node: ast.Delete):  # targets
        error = "This delete method is not allowed"
        for target in node.targets:
            if isinstance(target, ast.Name):
                del self.scope[target.id]
            elif isinstance(target, ast.Subscript):
                sym = self._run(target.value)
                if not is_subscriptable(sym):
                    error_maker(NotSubscriptableError, sym)
                xslice = self._run(target.slice)
                if not isinstance(
                    target.slice,
                    (ast.Tuple, ast.Slice),
                ):
                    del sym[xslice]
                else:
                    raise BadSyntax(error)
            else:
                raise BadSyntax(error)

    def visit_dict(self, node: ast.Dict):  # keys, values
        return {
            self._run(k): self._run(v)
            for k, v in zip(node.keys, node.values, strict=True)
        }

    def visit_dictcomp(self, node: ast.DictComp):  # key, value, generators
        result: dict = {}
        current_gen = node.generators[0]
        if isinstance(current_gen, ast.comprehension):
            if current_gen.is_async:
                error_maker(AsyncComprehensionError, node)
            with self.scope:
                it = self._run(current_gen.iter)
                if not is_iterable(it):
                    error_maker(NotIterableError, it)
                for val in it:
                    self.assign(current_gen.target, val)
                    add = True
                    for cond in current_gen.ifs:
                        add = add and self._run(cond)
                    if add:
                        if len(node.generators) > 1:
                            r = self.visit_dictcomp(
                                ast.DictComp(
                                    key=node.key,
                                    value=node.value,
                                    generators=node.generators[1:],
                                ),
                            )
                            result.update(r)
                        else:
                            key = self._run(node.key)
                            value = self._run(node.value)
                            result[key] = value
                    self.delete(current_gen.target)
        return result

    def visit_expr(self, node: ast.Expr):  # value,
        return self._run(node.value)

    def visit_functiondef(self, node: ast.FunctionDef):
        error_maker(UnavailableSyntaxError, node)

    def visit_for(
        self,
        node: ast.For,
    ):  # target, iter, body, orelse, type_comment
        it = self._run(node.iter)
        if not is_iterable(it):
            error_maker(NotIterableError, it)
        for val in it:
            self.assign(node.target, val)
            self.current_interrupt = None
            for tnode in node.body:
                self._run(tnode)
                if self.current_interrupt is not None:
                    break
            if isinstance(self.current_interrupt, ast.Break):
                break
        else:
            for tnode in node.orelse:
                self._run(tnode)

        self.current_interrupt = None

    def visit_formattedvalue(self, node: ast.FormattedValue):
        # value, conversion, format_spec
        value = self._run(node.value)
        format_spec = self._run(node.format_spec)
        if format_spec is None:
            format_spec = ""
        return format(value, format_spec)

    def visit_generatorexp(self, node: ast.GeneratorExp):
        error_maker(UnavailableSyntaxError, node)

    def visit_global(self, node: ast.Global):
        error_maker(UnavailableSyntaxError, node)

    def visit_if(self, node: ast.If):  # test, body, orelse
        stmts = node.body if self._run(node.test) else node.orelse
        for stmt in stmts:
            self._run(stmt)

    def visit_ifexp(self, node: ast.IfExp):  # test, body, orelse
        return self._run(node.body if self._run(node.test) else node.orelse)

    def visit_import(self, node: ast.Import):
        error_maker(UnavailableSyntaxError, node)

    def visit_importfrom(self, node: ast.ImportFrom):
        error_maker(UnavailableSyntaxError, node)

    def visit_joinedstr(self, node: ast.JoinedStr):  # values,
        return "".join(str(self._run(x)) for x in node.values)

    def visit_lambda(self, node: ast.Lambda):
        error_maker(UnavailableSyntaxError, node)

    def visit_list(self, node: ast.List):  # elts, ctx
        return [self._run(x) for x in node.elts]

    def visit_listcomp(self, node: ast.ListComp):  # elt, generators
        result: list = []
        current_gen = node.generators[0]
        if isinstance(current_gen, ast.comprehension):
            if current_gen.is_async:
                error_maker(AsyncComprehensionError, node)
            with self.scope:
                it = self._run(current_gen.iter)
                if not is_iterable(it):
                    error_maker(NotIterableError, it)
                for val in it:
                    self.assign(current_gen.target, val)
                    add = True
                    for cond in current_gen.ifs:
                        add = add and self._run(cond)
                    if add:
                        if len(node.generators) > 1:
                            r = self.visit_listcomp(
                                ast.ListComp(
                                    elt=node.elt,
                                    generators=node.generators[1:],
                                ),
                            )
                            result += r
                        else:
                            r = self._run(node.elt)
                            result.append(r)
                    self.delete(current_gen.target)
        return result

    def visit_match(self, node: ast.Match):
        error_maker(UnavailableSyntaxError, node)

    def visit_module(self, node: ast.Module):  # body,
        last = None
        for body_node in node.body:
            last = self._run(body_node)
        return last

    def visit_name(self, node: ast.Name):  # id, ctx
        if node.id in self.scope:
            return self.scope[node.id]
        if node.id in self.global_symbol_table:
            return self.global_symbol_table[node.id]
        raise NameError(str(node.id))

    def visit_namedexpr(self, node: ast.NamedExpr):
        error_maker(UnavailableSyntaxError, node)

    def visit_nonlocal(self, node: ast.Nonlocal):
        error_maker(UnavailableSyntaxError, node)

    def visit_pass(self, node: ast.Pass):
        return

    def visit_raise(self, node: ast.Raise):
        error_maker(UnavailableSyntaxError, node)

    def visit_return(self, node: ast.Return):
        error_maker(UnavailableSyntaxError, node)

    def visit_set(self, node: ast.Set):  # elts,
        return {self._run(x) for x in node.elts}

    def visit_setcomp(self, node: ast.SetComp):  # elt, generators
        result = set()
        current_gen = node.generators[0]
        if isinstance(current_gen, ast.comprehension):
            if current_gen.is_async:
                error_maker(AsyncComprehensionError, node)
            with self.scope:
                it = self._run(current_gen.iter)
                if not is_iterable(it):
                    error_maker(NotIterableError, it)
                for val in it:
                    self.assign(current_gen.target, val)
                    add = True
                    for cond in current_gen.ifs:
                        add = add and self._run(cond)
                    if add:
                        if len(node.generators) > 1:
                            r = self.visit_setcomp(
                                ast.SetComp(
                                    elt=node.elt,
                                    generators=node.generators[1:],
                                ),
                            )
                            result |= r
                        else:
                            r = self._run(node.elt)
                            result.add(r)
                    self.delete(current_gen.target)
        return result

    def visit_slice(self, node: ast.Slice):  # lower, upper, step
        return slice(
            self._run(node.lower),
            self._run(node.upper),
            self._run(node.step),
        )

    def visit_subscript(self, node: ast.Subscript):  # value, slice, ctx
        value = self._run(node.value)
        if not is_get_subscriptable(value):
            error_maker(NotSubscriptableError, value)
        xslice = self._run(node.slice)
        return value[xslice]

    def visit_try(self, node: ast.Try):
        error_maker(UnavailableSyntaxError, node)

    def visit_trystar(self, node: ast.TryStar):
        error_maker(UnavailableSyntaxError, node)

    def visit_tuple(self, node: ast.Tuple):  # elts, ctx
        return tuple(self._run(x) for x in node.elts)

    def visit_typealias(self, node):  # name, type_params, value
        error_maker(UnavailableSyntaxError, node)

    def visit_unaryop(self, node: ast.UnaryOp):  # op, operand
        op = UNARYOP_TABLE.get(node.op.__class__)
        if op:
            return op(self._run(node.operand))
        raise NotImplementedError

    def visit_while(self, node: ast.While):  # test, body, orelse
        while self._run(node.test):
            self.current_interrupt = None
            for tnode in node.body:
                self._run(tnode)
                if self.current_interrupt is not None:
                    break
            if isinstance(self.current_interrupt, ast.Break):
                break
        else:
            for tnode in node.orelse:
                self._run(tnode)

        self.current_interrupt = None

    def visit_with(self, node: ast.With):
        error_maker(UnavailableSyntaxError, node)

    def visit_yield(self, node: ast.Yield):
        error_maker(UnavailableSyntaxError, node)

    def visit_yieldfrom(self, node: ast.YieldFrom):
        error_maker(UnavailableSyntaxError, node)

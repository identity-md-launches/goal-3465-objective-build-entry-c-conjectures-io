"""Static rules a submission must pass before anything runs. Three layers:

1. Text: no #include / #pragma / _Pragma / attributes; size cap.
2. AST (clang JSON, RV32 target): no floating point anywhere; no state that survives a call (every
   file-scope or `static` variable is const); no volatile, atomics, asm, function pointers,
   pointer/integer casts, plain `char` or `long` (they differ between targets and the x86-64 host);
   only the entry points (eik_sigmoid, eik_tanh, eik_exp) are non-static; calls only to functions defined in the file, to
   memcpy/memset/memmove, or to whitelisted builtins; no recursion.
3. Object file, per target: no writable data, undefined symbols only from an allowlist of integer
   compiler-rt helpers (so no soft-float routine can appear), and code+tables within the cap.
"""
import re
from pathlib import Path

from elftools.elf.constants import SH_FLAGS
from elftools.elf.elffile import ELFFile

from . import config as K
from . import toolchain as T
from . import stack as STACK

PRELUDE_FUNCS = {"memcpy", "memset", "memmove"} | K.ENTRY_POINTS
BUILTINS = {"__builtin_clz", "__builtin_clzll", "__builtin_ctz", "__builtin_ctzll", "__builtin_expect",
            "__builtin_unreachable", "__builtin_popcount"}
BANNED_KINDS = {"GCCAsmStmt", "MSAsmStmt", "FloatingLiteral", "ImaginaryLiteral", "AtomicExpr",
                "IndirectGotoStmt", "AddrLabelExpr", "BlockExpr", "StringLiteral"}
BANNED_TYPE = re.compile(r"\b(float|double|_Complex|__fp16|_Float\d*|__bf16|__int128|volatile|_Atomic)\b")
PLAIN_CHAR = re.compile(r"(?<!signed )(?<!unsigned )\bchar\b")
PLAIN_LONG = re.compile(r"(?<!long )\blong\b(?! long)")
# integer helpers clang/compiler-rt may call on RV32IM and ARMv6-M/v7E-M; counted in the score
RUNTIME_OK = {
    "memcpy", "memset", "memmove",
    "__mulsi3", "__muldi3", "__divsi3", "__udivsi3", "__modsi3", "__umodsi3", "__divdi3", "__udivdi3",
    "__moddi3", "__umoddi3", "__udivmoddi4", "__divmoddi4", "__ashldi3", "__lshrdi3", "__ashrdi3",
    "__clzsi2", "__clzdi2", "__ctzsi2", "__ctzdi2", "__popcountsi2", "__popcountdi2", "__cmpdi2", "__ucmpdi2",
    "__aeabi_lmul", "__aeabi_uidiv", "__aeabi_uidivmod", "__aeabi_idiv", "__aeabi_idivmod",
    "__aeabi_uldivmod", "__aeabi_ldivmod", "__aeabi_llsl", "__aeabi_llsr", "__aeabi_lasr",
    "__aeabi_lcmp", "__aeabi_ulcmp", "__aeabi_memcpy", "__aeabi_memcpy4", "__aeabi_memcpy8",
    "__aeabi_memset", "__aeabi_memset4", "__aeabi_memset8", "__aeabi_memclr", "__aeabi_memclr4",
    "__aeabi_memclr8", "__aeabi_memmove", "__aeabi_memmove4", "__aeabi_memmove8",
}


class Reject(Exception):
    def __init__(self, stage, reasons):
        super().__init__(f"{stage}: " + "; ".join(reasons))
        self.stage, self.reasons = stage, reasons


# Directives an entry may use. Everything else is refused, whatever its spelling: #include,
# #include_next, #import, #embed, #pragma, #line, #error, #warning, #ident, #assert, GNU line markers.
ALLOWED_DIRECTIVES = {"define", "undef", "if", "ifdef", "ifndef", "elif", "else", "endif"}
# Identifiers refused anywhere in the source: compiler control, inline assembly, and probes of the
# file system or the compiler (the AST check and the preprocessing checks back these up).
BANNED_IDENTIFIERS = {"_Pragma", "__pragma", "__attribute__", "__attribute", "__declspec", "asm", "__asm",
                      "__asm__", "__has_include", "__has_include_next", "__has_embed"}
_TRIGRAPH = re.compile(r"\?\?[=/'()!<>\-]")
_SPLICE = re.compile(r"\\[ \t\f\v]*\r?\n")  # gcc and clang also splice when spaces follow the backslash
_LITERAL = re.compile(r"""(?:u8|[uUL])?(?:"(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*')""")


def _strip_comments(text: str) -> str:
    """Translation phase 3: every comment becomes one space; string and character literals are kept,
    so a comment opener inside one is not a comment. A multi-line /* comment */ does not end the
    line it starts on, as in C."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == "/" and text.startswith("/*", i):
            j = text.find("*/", i + 2)
            if j < 0:
                raise ValueError("unterminated /* comment")
            out.append(" ")
            i = j + 2
        elif c == "/" and text.startswith("//", i):
            j = text.find("\n", i)
            out.append(" ")
            i = n if j < 0 else j
        elif c in "\"'":
            m = _LITERAL.match(text, i)
            if m is None:
                raise ValueError(f"unterminated {'string' if c == chr(34) else 'character'} literal")
            out.append(m.group())
            i = m.end()
        else:
            out.append(c)
            i += 1
    return "".join(out)


def check_text(src: Path):
    """The source as the preprocessor reads it (translation phases 1-3: no trigraphs, line splices
    joined, comments removed), then: only the allowed directives, in either spelling (# or the
    digraph %:), and none of the banned identifiers."""
    raw = Path(src).read_bytes()
    reasons = []
    if len(raw) > K.CAP_SOURCE_BYTES:
        raise Reject("text", [f"source larger than {K.CAP_SOURCE_BYTES} bytes"])
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        raise Reject("text", [f"source is not UTF-8 (byte {e.start})"])
    if "\0" in text:
        reasons.append("source contains a NUL byte")
    if _TRIGRAPH.search(text):
        reasons.append("trigraphs (??= ??/ ...) are not allowed: C11 replaces them before anything else, "
                       "so they can hide directives and line splices")
    try:
        clean = _strip_comments(_SPLICE.sub("", text))
    except ValueError as e:
        raise Reject("text", reasons + [str(e)])
    for line in clean.split("\n"):
        m = re.match(r"[ \t\f\v\r]*(?:#|%:)[ \t\f\v\r]*(\S*)", line)
        if not m:
            continue
        word = re.match(r"[A-Za-z_]\w*", m.group(1) or "")
        name = word.group() if word else m.group(1)
        if name and name not in ALLOWED_DIRECTIVES:
            reasons.append(f"directive '#{name}' is not allowed (only #{', #'.join(sorted(ALLOWED_DIRECTIVES))}; "
                           "the prelude eik.h is the only header)")
    code = _LITERAL.sub(" ", clean)
    for ident in sorted(set(re.findall(r"[A-Za-z_$][\w$]*", code)) & BANNED_IDENTIFIERS):
        reasons.append(f"'{ident}' is not allowed")
    if re.search(r"\[\s*\[|<:\s*<:", code):
        reasons.append("'[[' attributes are not allowed")
    if reasons:
        raise Reject("text", sorted(set(reasons)))


def check_preprocessing(src: Path):
    """What the preprocessor actually produced. Nothing may survive as a directive (a _Pragma that a
    macro assembled by token pasting comes out as #pragma), and every real build -- each target's
    clang and the host's sanitizer gcc, with their own flags -- must see the same tokens. Otherwise
    the entry depends on predefined macros (__clang__, __riscv, __x86_64__, __SANITIZE_ADDRESS__,
    __STDC_HOSTED__, ...) and the host's full check would verify different code from the targets'."""
    reasons = []
    for line in T.preprocess(src).splitlines():
        if line.lstrip().startswith(("#", "%:")):
            reasons.append(f"'{line.strip()[:60]}' survives preprocessing (built by a macro?)")
    streams = {b: _TOKEN.findall(text) for b, text in T.preprocessed_builds(src).items()}
    differ = [b for b, toks in streams.items() if toks != streams["rv32im"]]
    if differ:
        reasons.append(f"the entry preprocesses to different code for {', '.join(differ)} than for rv32im: it "
                       "depends on predefined macros; every build must compile the same code")
    if reasons:
        raise Reject("preprocess", sorted(set(reasons)))


_WIDE = re.compile(r"^(?:const )?(?:unsigned )?long(?: int)?$")        # size_t, ptrdiff_t on LP64
_WIDER = re.compile(r"^(?:const )?(?:unsigned )?long long(?: int)?$")  # int64_t, uint64_t
# On values that agree modulo 2^32, these give the same low 32 bits at either width, so a later
# narrowing makes them agree; every other operator can expose the upper 32 bits.
_MODULAR = {"+", "*", "=", ",", "+=", "*="}


def _type_names(node):
    t = node.get("type") or {}
    return [q for q in (t.get("desugaredQualType"), t.get("qualType")) if q]


def _wide(node) -> bool:
    call = node
    while call.get("kind") == "ParenExpr" and call.get("inner"):
        call = call["inner"][0]
    if call.get("kind") == "CallExpr" and _callee(call) == EXPECT:
        return False  # long, but check_ast admits it only on a 32-bit value used as a truth value
    return any(_WIDE.match(q) for q in _type_names(node))


def _is_sizeof(node) -> bool:
    while node.get("kind") in ("ParenExpr", "ImplicitCastExpr") and node.get("inner"):
        node = node["inner"][0]
    return node.get("kind") == "UnaryExprOrTypeTraitExpr"


def check_host_widths(src: Path):
    """The host's full check compiles the entry for LP64, where sizeof results and pointer
    differences (size_t, ptrdiff_t) are 64-bit; on the 32-bit targets they are 32-bit. Most uses agree
    anyway: + and * are the same modulo 2^32, and so is storing the result in a 32-bit variable. What
    can disagree is an operation that exposes the upper bits -- subtraction (x - sizeof y wraps
    differently), shifts, division and remainder, comparisons, bitwise operators, ~ and unary minus,
    or widening the value to a 64-bit type. Those are refused on the host's AST, except a pointer
    difference itself and sizeof / sizeof (an array's length). The fix is a cast: (uint32_t)sizeof x."""
    reasons = []
    for top in T.ast_json(src, T.HOST_TRIPLE).get("inner", []):
        if top.get("isImplicit") or top.get("loc", {}).get("includedFrom"):
            continue
        for node, _, fn in _walk(top):
            kind, op = node.get("kind"), node.get("opcode")
            kids = node.get("inner") or []
            if kind in ("ImplicitCastExpr", "CStyleCastExpr") and kids and _wide(kids[0]) \
                    and any(_WIDER.match(q) for q in _type_names(node)):
                reasons.append(f"a size_t/sizeof or pointer-difference value widened to {_type_names(node)[-1]} "
                               f"(in {fn}) is 64-bit on the host and 32-bit on the targets; cast it to uint32_t first")
                continue
            if kind not in ("BinaryOperator", "CompoundAssignOperator", "UnaryOperator"):
                continue
            if not (_wide(node) or any(_wide(k) for k in kids)) or op in _MODULAR:
                continue
            if kind == "UnaryOperator" and op in ("&", "*", "!"):
                continue  # address-of, dereference, and a zero test agree at either width
            if op == "-" and len(kids) == 2 and all("*" in (k.get("type") or {}).get("qualType", "") for k in kids):
                continue  # p - q: the difference itself
            if op == "/" and len(kids) == 2 and all(_is_sizeof(k) for k in kids):
                continue  # sizeof a / sizeof a[0]
            reasons.append(f"'{op}' on a size_t/sizeof or pointer-difference value (in {fn}) can differ between the "
                           "64-bit host and the 32-bit targets; cast it to uint32_t first")
    if reasons:
        raise Reject("ast:host", sorted(set(reasons)))


def _walk(node, parent=None, fn=None):
    yield node, parent, fn
    if node.get("kind") == "FunctionDecl":
        fn = node.get("name")
    for ch in node.get("inner", []) or []:
        yield from _walk(ch, node, fn)


def _types(node):
    t = node.get("type")
    if isinstance(t, dict):
        yield t.get("qualType", ""), t.get("desugaredQualType", "")


def _is_const_object(qt: str) -> bool:
    qt = qt.strip()
    if "*" in qt:
        return qt.endswith("const")      # a const pointer; the pointee must be const too
    return qt.startswith("const ")


# __builtin_expect is declared `long (long, long)`: it converts its value to long, which is 64-bit on
# the host and 32-bit on the targets (a 64-bit value is truncated on the targets). Its value agrees
# everywhere only when it holds at most 32 bits and is used only as a truth value, so that is the one
# form allowed. The call's own long-typed nodes are then exempt from the long rule.
EXPECT = "__builtin_expect"
_NARROW = re.compile(r"^(?:const )?(?:(?:signed|unsigned) )?(?:char|short|int|_Bool)$")
# The child that is a truth value: statement conditions, the ?: test, and operands of ! && ||.
_CONDITION_CHILD = {"IfStmt": 0, "WhileStmt": 0, "ForStmt": 2, "DoStmt": -1, "ConditionalOperator": 0}


def _strip(node):
    while node.get("kind") in ("ParenExpr", "ImplicitCastExpr") and node.get("inner"):
        node = node["inner"][0]
    return node


def _used_as_truth_value(path) -> bool:
    """path ends with a node; True if that node's value is only tested against zero."""
    child = path[-1]
    for anc in reversed(path[:-1]):
        kind, kids = anc.get("kind"), anc.get("inner") or []
        if kind == "ParenExpr":
            child = anc
            continue
        if kind in _CONDITION_CHILD:
            i = _CONDITION_CHILD[kind]
            return -len(kids) <= i < len(kids) and kids[i] is child
        return (kind == "UnaryOperator" and anc.get("opcode") == "!") or \
            (kind == "BinaryOperator" and anc.get("opcode") in ("&&", "||"))
    return False


def _expect_calls(top):
    """ids of the long-typed nodes that belong to __builtin_expect calls, and reasons for the calls
    that are not in the allowed form."""
    exempt, reasons, path = set(), [], []

    def visit(node, fn):
        path.append(node)
        if node.get("kind") == "FunctionDecl":
            fn = node.get("name")
        if node.get("kind") == "CallExpr" and _callee(node) == EXPECT:
            kids = node.get("inner") or []
            exempt.add(id(node))
            callee = kids[0] if kids else {}
            while callee.get("kind") in ("ImplicitCastExpr", "ParenExpr"):
                exempt.add(id(callee))
                callee = (callee.get("inner") or [{}])[0]
            args = kids[1:]
            for a in args:
                if a.get("kind") == "ImplicitCastExpr" and a.get("castKind") == "IntegralCast":
                    exempt.add(id(a))
            # The value before its conversion to long; with no conversion it is already long or wider.
            value = (args[0].get("inner") or [{}])[0] if args and id(args[0]) in exempt else {}
            vt = value.get("type") or {}
            narrow = bool(_NARROW.match(vt.get("desugaredQualType") or vt.get("qualType") or ""))
            literal = len(args) == 2 and _strip(args[1]).get("kind") == "IntegerLiteral"
            for anc in reversed(path[:-1]):  # parentheses around the call have its long type too
                if anc.get("kind") != "ParenExpr":
                    break
                exempt.add(id(anc))
            if not (narrow and literal and _used_as_truth_value(path)):
                reasons.append(f"{EXPECT} (in {fn}) is allowed only as a condition (if/while/for/do, the ?: test, "
                               "or an operand of ! && ||), on a value of 32 bits or less, with a literal hint: "
                               "its long result differs between the 64-bit host and the 32-bit targets")
        for ch in node.get("inner", []) or []:
            visit(ch, fn)
        path.pop()

    visit(top, None)
    return exempt, reasons


def check_ast(src: Path) -> dict:
    tu = T.ast_json(src)
    reasons, defined, calls = [], {}, {}
    for top in tu.get("inner", []):
        if top.get("isImplicit"):
            continue  # compiler-provided declarations (vector and builtin types)
        expect_nodes, expect_reasons = _expect_calls(top)
        reasons += expect_reasons
        for node, parent, fn in _walk(top):
            kind = node.get("kind", "")
            if kind in BANNED_KINDS or (kind.endswith("Attr") and not node.get("isImplicit")
                                         and kind not in {"ConstAttr", "PureAttr"}):
                reasons.append(f"{kind} is not allowed" + (f" (in {fn})" if fn else ""))
            for qt, dq in _types(node):
                for s in (qt, dq):
                    m = BANNED_TYPE.search(s)
                    if m:
                        reasons.append(f"type '{s}' uses '{m.group(1)}'" + (f" (in {fn})" if fn else ""))
                if PLAIN_CHAR.search(qt):
                    reasons.append(f"plain char ('{qt}') differs in signedness between targets; use int8_t/uint8_t")
                if PLAIN_LONG.search(qt) and id(node) not in expect_nodes:
                    reasons.append(f"long ('{qt}') differs in width between targets; use int32_t/int64_t")
                if "(*)" in qt and kind in ("VarDecl", "ParmVarDecl", "FieldDecl", "TypedefDecl", "CStyleCastExpr"):
                    reasons.append(f"function pointer type '{qt}' is not allowed")
            if kind in ("CStyleCastExpr", "ImplicitCastExpr") and node.get("castKind") in (
                    "PointerToIntegral", "IntegralToPointer"):
                reasons.append(f"pointer/integer cast is not allowed (in {fn})")
            if kind == "VarDecl":
                at_file = parent is top or parent is None or parent.get("kind") == "TranslationUnitDecl"
                sc = node.get("storageClass")
                qt = node.get("type", {}).get("qualType", "")
                if top is node:
                    at_file = True
                if at_file or sc == "static":
                    if sc == "extern":
                        reasons.append(f"extern variable '{node.get('name')}'")
                    elif not _is_const_object(qt):
                        reasons.append(f"variable '{node.get('name')}' ({qt}) would keep state between calls; "
                                       "file-scope and static variables must be const")
                    elif at_file and sc != "static":
                        reasons.append(f"file-scope variable '{node.get('name')}' must be static")
            if kind == "CallExpr":
                ref = _callee(node)
                if ref is None:
                    reasons.append(f"indirect call (in {fn})")
                else:
                    calls.setdefault(fn, set()).add(ref)
        if top.get("kind") == "FunctionDecl":
            name = top.get("name")
            has_body = any(c.get("kind") == "CompoundStmt" for c in top.get("inner", []) or [])
            if has_body:
                defined[name] = top
                if name in K.ENTRY_POINTS:
                    if top.get("type", {}).get("qualType") != "uint32_t (uint32_t)":
                        reasons.append(f"{name} must have type uint32_t (uint32_t)")
                    if top.get("storageClass") == "static":
                        reasons.append(f"{name} must not be static")
                elif top.get("storageClass") != "static":
                    reasons.append(f"function '{name}' must be static (only the entry points are exported)")
        elif top.get("kind") not in ("TypedefDecl", "VarDecl", "FunctionDecl", "RecordDecl", "EnumDecl",
                                     "StaticAssertDecl", "EmptyDecl"):
            reasons.append(f"top-level {top.get('kind')} is not allowed")
    for ep in sorted(K.ENTRY_POINTS - defined.keys()):
        reasons.append(f"entry point {ep} is not defined")
    for fn, callees in calls.items():
        for c in callees:
            if c not in defined and c not in PRELUDE_FUNCS and c not in BUILTINS:
                reasons.append(f"call to '{c}' (in {fn}): only functions defined in the file, memcpy/memset/memmove "
                               "and whitelisted builtins")
    cyc = _cycle({f: {c for c in cs if c in defined} for f, cs in calls.items()})
    if cyc:
        reasons.append("recursion: " + " -> ".join(cyc))
    if reasons:
        raise Reject("ast", sorted(set(reasons)))
    return {"functions": len(defined)}


def _callee(call):
    first = (call.get("inner") or [None])[0]
    while first is not None:
        if first.get("kind") == "DeclRefExpr":
            return first.get("referencedDecl", {}).get("name")
        if first.get("kind") in ("ImplicitCastExpr", "ParenExpr"):
            first = (first.get("inner") or [None])[0]
            continue
        return None
    return None


def _cycle(g):
    state, stack = {}, []

    def dfs(u):
        state[u] = 1
        stack.append(u)
        for v in g.get(u, ()):
            if state.get(v) == 1:
                return stack[stack.index(v):] + [v]
            if not state.get(v):
                r = dfs(v)
                if r:
                    return r
        state[u] = 2
        stack.pop()
        return None

    for u in list(g):
        if not state.get(u):
            r = dfs(u)
            if r:
                return r
    return None


def check_object(obj: Path, target: str) -> dict:
    reasons, size = [], 0
    with open(obj, "rb") as f:
        elf = ELFFile(f)
        for sec in elf.iter_sections():
            fl = sec["sh_flags"]
            if fl & SH_FLAGS.SHF_ALLOC:
                size += sec["sh_size"]
                if fl & SH_FLAGS.SHF_WRITE and sec["sh_size"] > 0:
                    reasons.append(f"writable section {sec.name} ({sec['sh_size']} bytes): no state allowed")
        st = elf.get_section_by_name(".symtab")
        for s in st.iter_symbols():
            if not s.name or s["st_info"]["type"] in ("STT_FILE", "STT_SECTION"):
                continue
            if s["st_shndx"] == "SHN_UNDEF":
                if s.name not in RUNTIME_OK:
                    reasons.append(f"calls '{s.name}', which is not an allowed integer runtime helper"
                                   + (" (soft-float!)" if re.search(r"__aeabi_[fd]|sf|df", s.name) else ""))
            elif s["st_info"]["bind"] == "STB_GLOBAL" and s.name not in K.ENTRY_POINTS:
                reasons.append(f"exports '{s.name}'")
    if size > K.CAP_CODE_BYTES:
        reasons.append(f"code + tables {size} bytes > cap {K.CAP_CODE_BYTES} on {target}")
    if reasons:
        raise Reject(f"object:{target}", reasons)
    return {"bytes": size}


C_KEYWORDS = frozenset("""
    auto break case char const continue default do double else enum extern float for goto if inline
    int long register restrict return short signed sizeof static struct switch typedef union unsigned
    void volatile while _Alignas _Alignof _Atomic _Bool _Complex _Generic _Imaginary _Noreturn
    _Static_assert _Thread_local
""".split())
_TOKEN = re.compile(r"[A-Za-z_]\w*|\.?\d[\w.]*|'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"|\S")


def _prelude_names() -> frozenset:
    """Every identifier the prelude (harness/eik.h) defines or mentions: types, macros, the memory
    functions and the entry points. They mean the same in every entry, so they are never renamed."""
    text = re.sub(r"/\*.*?\*/", " ", (K.HARNESS / "eik.h").read_text(), flags=re.S)
    return frozenset(re.findall(r"[A-Za-z_]\w*", text)) | PRELUDE_FUNCS | BUILTINS


def normalised_hash(src: Path) -> str:
    """Duplicate check. The preprocessed source (macros expanded, comments gone) as a token stream,
    with every identifier the entry declares renamed by order of first appearance (`_0`, `_1`, ...).
    Whitespace, comments, macro wrappers and renaming therefore do not make a copy new. Keywords,
    the prelude's names, the entry points and the allowed builtins are kept."""
    import hashlib
    keep = C_KEYWORDS | _prelude_names()
    names: dict = {}
    out = []
    for tok in _TOKEN.findall(T.preprocess(src)):
        if (tok[0].isalpha() or tok[0] == "_") and tok not in keep:
            tok = names.setdefault(tok, f"_{len(names)}")
        out.append(tok)
    return hashlib.sha256(" ".join(out).encode()).hexdigest()


def check_all(src: Path) -> dict:
    """Text, AST, and every target's object file. Raises Reject; returns sizes per target."""
    check_text(src)
    info = check_ast(src)
    check_preprocessing(src)
    check_host_widths(src)
    sizes, stacks = {}, {}
    for t in K.TARGETS:
        try:
            obj = T.object_file(src, t)
        except T.BuildError as e:
            raise Reject(f"build:{t}", [str(e)])
        sizes[t] = check_object(obj, t)["bytes"]
        try:
            stacks[t] = STACK.bound(T.guest_image(src, t), obj, t)
        except STACK.UnboundedStack as exc:
            raise Reject(f"stack:{t}", [str(exc)]) from exc
        if stacks[t] > K.CAP_STACK_BYTES:
            raise Reject(f"stack:{t}", [f"static stack bound {stacks[t]} > {K.CAP_STACK_BYTES} bytes"])
    info["bytes"] = sizes
    info["stack_bound"] = stacks
    return info

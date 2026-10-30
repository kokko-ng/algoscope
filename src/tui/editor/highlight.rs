//! A small Python lexer for syntax colouring. Line based, with state for triple-quoted strings.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Tok {
    Text,
    Keyword,
    Builtin,
    Str,
    Number,
    Comment,
    Func,
    Decorator,
}

const KEYWORDS: &[&str] = &[
    "False", "None", "True", "and", "as", "assert", "async", "await", "break", "case", "class", "continue", "def",
    "del", "elif", "else", "except", "finally", "for", "from", "global", "if", "import", "in", "is", "lambda",
    "match", "nonlocal", "not", "or", "pass", "raise", "return", "try", "while", "with", "yield",
];

const BUILTINS: &[&str] = &[
    "abs", "all", "any", "bool", "dict", "divmod", "enumerate", "filter", "float", "frozenset", "hash", "int",
    "isinstance", "iter", "len", "list", "map", "max", "min", "next", "object", "ord", "chr", "print", "range",
    "reversed", "round", "self", "set", "sorted", "str", "sum", "super", "tuple", "type", "zip", "float",
];

/// Token kind for each char of each line.
pub fn highlight(lines: &[String]) -> Vec<Vec<Tok>> {
    let mut out = Vec::with_capacity(lines.len());
    let mut in_triple: Option<char> = None;
    for line in lines {
        let chars: Vec<char> = line.chars().collect();
        let mut toks = vec![Tok::Text; chars.len()];
        let mut i = 0;
        let mut after_def = false;
        if let Some(q) = in_triple {
            match find_triple(&chars, 0, q) {
                Some(end) => {
                    toks[..end].fill(Tok::Str);
                    i = end;
                    in_triple = None;
                }
                None => {
                    toks.fill(Tok::Str);
                    out.push(toks);
                    continue;
                }
            }
        }
        while i < chars.len() {
            let c = chars[i];
            if c == '#' {
                toks[i..].fill(Tok::Comment);
                break;
            }
            if c == '"' || c == '\'' {
                if i + 2 < chars.len() && chars[i + 1] == c && chars[i + 2] == c {
                    match find_triple(&chars, i + 3, c) {
                        Some(end) => {
                            toks[i..end].fill(Tok::Str);
                            i = end;
                        }
                        None => {
                            toks[i..].fill(Tok::Str);
                            in_triple = Some(c);
                            i = chars.len();
                        }
                    }
                    continue;
                }
                let start = i;
                i += 1;
                while i < chars.len() && chars[i] != c {
                    if chars[i] == '\\' {
                        i += 1;
                    }
                    i += 1;
                }
                let end = (i + 1).min(chars.len());
                toks[start..end].fill(Tok::Str);
                i = end;
                continue;
            }
            if c == '@' && chars[..i].iter().all(|x| x.is_whitespace()) {
                let start = i;
                i += 1;
                while i < chars.len() && (chars[i].is_alphanumeric() || chars[i] == '_' || chars[i] == '.') {
                    i += 1;
                }
                toks[start..i].fill(Tok::Decorator);
                continue;
            }
            if c.is_ascii_digit() || (c == '.' && chars.get(i + 1).is_some_and(|d| d.is_ascii_digit())) {
                let prev_word = i > 0 && (chars[i - 1].is_alphanumeric() || chars[i - 1] == '_');
                let start = i;
                while i < chars.len() && (chars[i].is_ascii_alphanumeric() || chars[i] == '.' || chars[i] == '_') {
                    i += 1;
                }
                if !prev_word {
                    toks[start..i].fill(Tok::Number);
                }
                continue;
            }
            if c.is_alphabetic() || c == '_' {
                let start = i;
                while i < chars.len() && (chars[i].is_alphanumeric() || chars[i] == '_') {
                    i += 1;
                }
                let word: String = chars[start..i].iter().collect();
                let is_attr = start > 0 && chars[start - 1] == '.';
                let kind = if after_def {
                    after_def = false;
                    Tok::Func
                } else if KEYWORDS.contains(&word.as_str()) && !is_attr {
                    if word == "def" || word == "class" {
                        after_def = true;
                    }
                    Tok::Keyword
                } else if BUILTINS.contains(&word.as_str()) && !is_attr {
                    Tok::Builtin
                } else {
                    Tok::Text
                };
                toks[start..i].fill(kind);
                continue;
            }
            i += 1;
        }
        out.push(toks);
    }
    out
}

fn find_triple(chars: &[char], from: usize, q: char) -> Option<usize> {
    let mut i = from;
    while i + 3 <= chars.len() {
        if chars[i] == q && chars[i + 1] == q && chars[i + 2] == q {
            return Some(i + 3);
        }
        i += 1;
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;

    fn kinds(src: &str) -> Vec<Vec<Tok>> {
        highlight(&src.lines().map(str::to_owned).collect::<Vec<_>>())
    }

    #[test]
    fn keywords_strings_numbers_comments() {
        let k = kinds("def solve(nums):\n    x = 'a#b' + 12  # note");
        assert_eq!(k[0][0], Tok::Keyword);
        assert_eq!(k[0][4], Tok::Func);
        let line = "    x = 'a#b' + 12  # note";
        let at = |s: &str| line.find(s).unwrap();
        assert_eq!(k[1][at("'a#b'")], Tok::Str);
        assert_eq!(k[1][at("#b") ], Tok::Str);
        assert_eq!(k[1][at("12")], Tok::Number);
        assert_eq!(k[1][at("# note")], Tok::Comment);
    }

    #[test]
    fn triple_quotes_span_lines() {
        let k = kinds("x = \"\"\"start\nmiddle\nend\"\"\" + y");
        assert!(k[1].iter().all(|t| *t == Tok::Str));
        assert_eq!(k[2][0], Tok::Str);
        assert_eq!(*k[2].last().unwrap(), Tok::Text);
    }
}

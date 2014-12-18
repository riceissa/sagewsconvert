
def old_tex_escape(s):
    return s.replace( "\\","{\\textbackslash}" ).replace( "_","\\_" ).replace( "{\\textbackslash}$","\\$" ).replace('%','\\%').replace('#','\\#').replace("&","\\&").replace("^", "{\\textasciicircum}")

class Token(object):
    def __init__(self, _type, _seq):
        self.type = _type
        self.seq = _seq

    def __add__(self, other):
        if self.type == other.type:
            return Token(self.type, self.seq + other.seq)
        else:
            raise ValueError("cannot add two tokens with distinct types")

    def __str__(self):
        return "({type}, '{seq}')".format(type=self.type, seq=self.seq)
    def __repr__(self):
        return "Token({type}, '{seq}')".format(type=self.type, seq=self.seq)

def lex(s):
    tokens = []
    at_backslash_escape = False
    in_math = False
    for char in s:
        if in_math:
            if at_backslash_escape:
                if char == '$':
                    tokens.append(Token("math", "\\$"))
                    at_backslash_escape = False
                else:
                    tokens.extend([Token("math", "\\"), Token("math", char)])
                    at_backslash_escape = False
            else:
                if char == '\\':
                    at_backslash_escape = True
                elif char == '$':
                    in_math = False
                else:
                    tokens.append(Token("math", char))
        else:
            if at_backslash_escape:
                # so we want to backslash escape this character
                if char == '$':
                    tokens.append(Token("literal", '$'))
                    at_backslash_escape = False
                else:
                    # it wasn't an escapable character, so fallback to
                    # literal backslash and the character
                    tokens.extend([Token("literal", "\\"), Token("literal", char)])
                    at_backslash_escape = False
            else:
                if char == '$':
                    in_math = True
                elif char == '\\':
                    at_backslash_escape = True
                else:
                    tokens.append(Token("literal", char))
    return tokens

def merge(tokens, token):
    if tokens == []:
        tokens.append(token)
    elif tokens[-1].type == token.type:
        tokens[-1] += token
    else:
        tokens.append(token)

def par(tokens):
    cleaned = []
    for t in tokens:
        merge(cleaned, t)
    result = ""
    for t in cleaned:
        if t.type == "literal":
            result += old_tex_escape(t.seq)
        else:
            # so this is math
            result += "$" + t.seq + "$"
    return result

def tex_escape(s):
    return par(lex(s))

if __name__ == "__main__":
    assert tex_escape(r"hello $a + b$") == "hello $a + b$"
    assert tex_escape(r'foo \ bar') == r"foo {\textbackslash} bar"
    print tex_escape(r"$\alpha + \beta$") , r"$\alpha + \beta$"
    assert tex_escape(r"!@#%^&*()_+") == r"!@\#\%{\textasciicircum}\&*()\_+"
    assert tex_escape(r"$\alpha + \beta$") == r"$\alpha + \beta$"
    print("all done!")
    #print(tex_escape("hello $a + b$"))

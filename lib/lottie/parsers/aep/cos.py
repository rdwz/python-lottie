import io
import enum


class TokenType(enum.Enum):
    # /foo
    Identifier = enum.auto()
    # 123
    Number = enum.auto()
    # (foo)
    String = enum.auto()
    # <f000>
    HexString = enum.auto()
    # true
    Boolean = enum.auto()
    # <<
    ObjectStart = enum.auto()
    # >>
    ObjectEnd = enum.auto()
    # [
    ArrayStart = enum.auto()
    # ]
    ArrayEnd = enum.auto()
    # null
    Null = enum.auto()
    # end of file
    Eof = enum.auto()


class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value


class CosParser:
    def __init__(self, file, max_pos):
        self.file = file
        self.max_pos = max_pos
        self.lookahead = None
        self.next_char = None

    def parse(self):
        self.lex()
        if self.lookahead.type == TokenType.Identifier:
            return self.parse_dict_content()
        return self.parse_value()

    def parse_value(self):
        if (
            self.lookahead.type == TokenType.String or
            self.lookahead.type == TokenType.Number or
            self.lookahead.type == TokenType.HexString or
            self.lookahead.type == TokenType.Null or
            self.lookahead.type == TokenType.Boolean or
            self.lookahead.type == TokenType.Identifier
        ):
            val = self.lookahead.value
            self.lex()
            return val

        if self.lookahead.type == TokenType.Eof:
            raise SyntaxError("Expected COS value")

        if self.lookahead.type == TokenType.ObjectStart:
            self.lex()
            val = self.parse_dict_content()
            self.expect(TokenType.ObjectEnd)
            self.lex()
            return val

        if self.lookahead.type == TokenType.ArrayStart:
            self.lex()
            val = self.parse_array_content()
            self.expect(TokenType.ArrayEnd)
            self.lex()
            return val

    def parse_dict_content(self):
        value = {}
        while True:
            if self.lookahead.type == TokenType.Eof or self.lookahead.type == TokenType.ObjectEnd:
                break

            self.expect(TokenType.Identifier)
            key = self.lookahead.value
            self.lex()
            val = self.parse_value()
            value[key] = val

        return value

    def parse_array_content(self):
        value = []
        while True:
            if self.lookahead.type == TokenType.Eof or self.lookahead.type == TokenType.ArrayEnd:
                break
            value.append(self.parse_value())
        return value

    def expect(self, token_type):
        if self.lookahead.type != token_type:
            raise SyntaxError("Expected %s, got %s" % (token_type, self.lookahead.type))

    def lex(self):
        self.lookahead = self.lex_token()

    def lex_token(self):
        while True:
            char = self.get_char()
            if char is None:
                return Token(TokenType.Eof)
            elif char == b"%":
                self.lex_comment()
            elif not char.isspace():
                break

        # <<
        if char == b"<":
            char = self.get_char()
            if char == b"<":
                return Token(TokenType.ObjectStart)
            elif char is None:
                self.raise_lex(b"<")
            elif self.is_hex(char):
                return self.lex_hex_string(char)
            else:
                self.raise_lex(b"<" + char)

        # >>
        if char == b">":
            self.expect_char(b">", char)
            return Token(TokenType.ObjectEnd)

        # [
        if char == b"[":
            return Token(TokenType.ArrayStart)

        # ]
        if char == b"]":
            return Token(TokenType.ArrayEnd)

        # /foo
        if char == b"/":
            return self.lex_identifier()

        if char == b"(":
            return self.lex_string()

        # Keyword
        if char.isalpha():
            return self.lex_keyword(char)

        # Number
        if char.isdigit() or char in b".+-":
            return self.lex_number(char)

        self.raise_lex(char)

    def expect_char(self, exp, head):
        char = self.get_char()
        if char != exp:
            self.raise_lex(head+char, head+exp)

    def raise_lex(self, token, exp=None):
        msg = "Unknown COS token %s" % token
        if exp is not None:
            msg += ", expected %s" % exp
        raise SyntaxError(msg)

    def get_char(self):
        if self.max_pos is not None and self.max_pos <= 0:
            return None

        char = self.file.read(1)
        self.max_pos -= 1
        return char

    def unget(self):
        self.file.seek(-1, io.SEEK_CUR)
        self.max_pos += 1

    # Skip until newline
    def lex_comment(self):
        while True:
            char = self.get_char()
            if char == b'\n':
                break
            elif char is None:
                break

    def lex_number(self, char):
        if char == b'.':
            return self.lex_num_fract(self.get_char(), char)
        elif char == b'+' or char == b'-':
            return self.lex_num_int(self.get_char(), char)
        else:
            return self.lex_num_int(char, b'')

    def lex_num_int(self, char, head):
        while True:
            if char == b'.':
                return self.lex_num_fract(self.get_char(), head + char)
            elif char is None:
                break
            elif char.isdigit():
                head += char
                char = self.get_char()
            else:
                self.unget()
                break
        return Token(TokenType.Number, int(head))

    def lex_num_fract(self, char, head):
        while True:
            if char is None:
                break
            elif char.isdigit():
                head += char
                char = self.get_char()
            else:
                self.unget()
                break
        return Token(TokenType.Number, float(head))

    def lex_keyword(self, char):
        kw = char
        while True:
            char = self.get_char()
            if char is None:
                break
            elif char.isalpha():
                kw += char
            else:
                self.unget()
                break

        if kw == b"true":
            return Token(TokenType.Boolean, True)
        elif kw == b"false":
            return Token(TokenType.Boolean, False)
        elif kw == b"null":
            return Token(TokenType.Boolean, None)
        else:
            raise SyntaxError("Unknown keyword %s" % kw)

    def lex_string(self):
        string = b''
        encoding = "utf-8"

        for i in range(2):
            char = self.lex_string_char()
            if char is None:
                break
            string += char

        bom = string
        if bom == b'\xfe\xff':
            encoding = "utf-16-be"
        elif bom == b'\xff\xfe':
            encoding = "utf-16-le"

        while True:
            char = self.lex_string_char()
            if char is None:
                break
            string += char

        try:
            return Token(TokenType.String, string.decode(encoding))
        except UnicodeDecodeError:
            return Token(TokenType.String, bom + string)

    def lex_string_char(self):
        char = self.get_char()
        if char is None:
            raise SyntaxError("Unterminated string")
        elif char == b')':
            return None
        elif char == b'\\':
            return self.lex_string_escape()
        elif char == b'\r':
            if self.get_char() != b'\n':
                self.unget()
            return b'\n'
        elif char == b'\n':
            if self.get_char() != b'\r':
                self.unget()
            return b'\n'
        else:
            return char

    def lex_string_escape(self):
        char = self.get_char()
        if char is None:
            raise SyntaxError("Unterminated string")

        if char == b'n':
            return b'\n'
        elif char == b'r':
            return b'\r'
        elif char == b'b':
            return b'\b'
        elif char == b'f':
            return b'\f'
        elif char == b'(':
            return b'('
        elif char == b')':
            return b')'
        elif char == b'\\':
            return b'\\'
        elif self.is_octal(char):
            octal = char[0] - b'0'[0]
            for i in range(2):
                char = self.get_char()
                if char is None:
                    break
                elif not self.is_octal(char):
                    self.unget()
                    break
                octal = octal*8 + char - b'0'[0]
            return octal.to_bytes(1, "big")

        raise SyntaxError("Invalid Escape sequence")

    def is_octal(self, char):
        return b'0' <= char <= b'8'

    def is_hex(self, char):
        return char.isdigit() or b'a' <= char <= b'f' or b'A' <= char <= b'F'

    def lex_hex_string(self, hstr):
        while True:
            char = self.get_char()
            if char is None:
                raise SyntaxError("Unterminated hex string")
            elif char.is_hex():
                hstr += char
            elif char == b'>':
                break
            elif not char.isspace():
                raise SyntaxError("Invalid character in hex string %s" % char)

        if len(hstr) % 2:
            hstr += b'0'

        data = b''
        for i in range(0, len(hstr), 2):
            data += int(hstr[i:i+1], 16).to_bytes(1, "big")

        return Token(TokenType.HexString, data)

    def lex_identifier(self):
        ident = ""
        while True:
            char = self.get_char()
            if char is None:
                break
            elif char < b'!' or char > b'~':
                self.unget()
                break
            elif char == b'#':
                hexstr = b''
                for i in range(2):
                    char = self.get_char()
                    if char is None or not self.is_hex(char):
                        raise SyntaxError("Invalid identifier")
                    hexstr += char
                ident += chr(int(hexstr, 16))
            else:
                ident += chr(char[0])

        return Token(TokenType.Identifier, ident)

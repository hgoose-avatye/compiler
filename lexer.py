from dataclasses import dataclass

@dataclass
class Token:
    type: str    # 'NUMBER', 'IDENT', 'PLUS', 'LET', ...
    value: str
    line: int

KEYWORDS = {"let", "if", "else", "while", "print"}

def tokenize(src: str) -> list[Token]:
    tokens = []
    i = 0
    line = 1

    while i < len(src):
        ch = src[i]

        # TODO: 공백/개행 처리 (개행이면 line += 1)
        if ch == '\n':
            line += 1
            i+=1
        elif ch.isspace():
            i+=1
        
        # TODO: 숫자 (연속된 숫자를 한 토큰으로)
        elif ch.isdigit():
            num = ''
            while i < len(src) and src[i].isdigit():
                num += src[i]
                i += 1
            tokens.append(Token('NUMBER', num, line))
        
        # TODO: 식별자/키워드 (글자로 시작, 글자/숫자 계속)
        # 첫글자는 '_' 또는 글자
        elif ch.isalpha() or ch == '_':
            var_name = ''
            while i < len(src) and src[i].isalnum() or src[i] == '_':
                var_name += src[i]
                i += 1
            if var_name in KEYWORDS:
                tokens.append(Token(var_name.upper(), var_name, line))
            else:
                tokens.append(Token("IDENT", var_name, line))
        
        # TODO: 연산자와 기호 (+ - * / ( ) { } ; = == != < > <= >=)
        # 한 글자, 두 글자 가능성 
        # 두글자 : ==, !=, <=, >=
        elif ch in '+-*/(){};=!<>':
            oper = ''
            if ch in '=!<>':
                if i + 1 < len(src) and src[i + 1] == '=':
                    oper = ch + '='
                    i += 2
                elif ch == '!':
                    raise Exception(f"{line}번째 줄, '!' 다음에는 '='가 필요합니다")
                else:
                    oper = ch
                    i += 1
            else:
                oper = ch
                i += 1

            if oper == '+':
                tok_type = 'PLUS'
            elif oper == '-':
                tok_type = 'MINUS'
            elif oper == '*':
                tok_type = 'STAR'
            elif oper == '/':
                tok_type = 'SLASH'
            elif oper == '(':
                tok_type = 'LPAREN'
            elif oper == ')':
                tok_type = 'RPAREN'
            elif oper == '{':
                tok_type = 'LBRACE'
            elif oper == '}':
                tok_type = 'RBRACE'
            elif oper == ';':
                tok_type = 'SEMI'
            elif oper == '=':
                tok_type = 'EQ'
            elif oper == '==':
                tok_type = 'EQEQ'
            elif oper == '!=':
                tok_type = 'NEQ'
            elif oper == '<':
                tok_type = 'LT'
            elif oper == '<=':
                tok_type = 'LE'
            elif oper == '>':
                tok_type = 'GT'
            else:
                tok_type = 'GE'
            tokens.append(Token(tok_type, oper, line))


        # TODO: 알 수 없는 문자는 줄 번호와 함께 에러 발생
        else:
            raise Exception(f"{line}번째 줄, 알 수 없는 문자 '{ch}'")

    tokens.append(Token("EOF", "", line))
    return tokens

if __name__ == "__main__":
    for t in tokenize("let x = 1 + 23;"):
        print(t)
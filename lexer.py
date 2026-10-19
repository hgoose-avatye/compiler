from dataclasses import dataclass

# 토큰: 소스 코드에서 잘라 낸 "의미 있는 한 조각".
# line을 함께 들고 다니는 이유는 파서가 에러를 낼 때 몇 번째 줄인지 알려 주기 위해서다.
@dataclass
class Token:
    type: str    # 'NUMBER', 'IDENT', 'PLUS', 'LET', ...
    value: str
    line: int

# 예약어 목록. 변수 이름과 구별하기 위해 따로 모아 둔다.
KEYWORDS = {"let", "if", "else", "while", "print"}

def tokenize(src: str) -> list[Token]:
    # 역할: 소스 코드 문자열을 한 글자씩 읽어 "토큰" 목록으로 잘라 준다.
    #       (컴파일러의 첫 단계. 글자 덩어리에 이름표(NUMBER, IDENT...)를 붙이는 일)
    # 문법: program_text -> (공백 | 숫자 | 식별자/키워드 | 연산자·기호)* EOF
    # 호출 순서 예시: "let x = 1;" -> LET, IDENT(x), EQ, NUMBER(1), SEMI, EOF
    #
    # 왜 먼저 자르는가: 파서가 글자 하나하나가 아니라 "단어 단위"로 문법을 판단하게 해서
    # 파서 코드를 훨씬 단순하게 만들기 위해서다. 이 함수에는 재귀가 없고 반복문 하나로 끝까지 읽는다.
    tokens = []
    i = 0        # 지금 읽고 있는 글자의 위치
    line = 1     # 에러 메시지에 줄 번호를 알려 주기 위해 개행마다 센다

    while i < len(src):
        ch = src[i]    # 이번 반복에서 판단할 글자. 어떤 종류인지에 따라 아래 분기 중 하나가 처리한다

        # TODO: 공백/개행 처리 (개행이면 line += 1)
        if ch == '\n':
            line += 1    # 줄이 바뀌었으니 번호를 올린다 (이후 토큰/에러에 새 줄 번호가 붙는다)
            i+=1         # 개행은 토큰이 아니므로 버리고 다음 글자로 간다
        elif ch.isspace():
            i+=1         # 공백/탭도 의미가 없어 건너뛴다 (단, 단어 사이를 구분하는 역할은 위 루프가 이미 한다)
        
        # TODO: 숫자 (연속된 숫자를 한 토큰으로)
        elif ch.isdigit():
            num = ''
            # 123 이 1, 2, 3 세 토큰으로 쪼개지지 않도록 숫자가 끝날 때까지 이어 붙인다
            while i < len(src) and src[i].isdigit():    # i < len(src) 를 먼저 검사해야 끝 글자에서 IndexError가 나지 않는다
                num += src[i]
                i += 1
            tokens.append(Token('NUMBER', num, line))
        
        # TODO: 식별자/키워드 (글자로 시작, 글자/숫자 계속)
        # 첫글자는 '_' 또는 글자
        elif ch.isalpha() or ch == '_':
            var_name = ''
            # 첫 글자는 위 조건(글자 또는 _)으로 이미 확인했고, 이후에는 숫자도 허용한다 (예: x1)
            while i < len(src) and (src[i].isalnum() or src[i] == '_'):
                var_name += src[i]
                i += 1
            # 먼저 끝까지 읽은 뒤에 키워드인지 확인한다. "letter"처럼 키워드로 시작하는
            # 이름이 let + ter 로 잘못 쪼개지는 것을 막기 위해서다.
            if var_name in KEYWORDS:
                tokens.append(Token(var_name.upper(), var_name, line))
            else:
                tokens.append(Token("IDENT", var_name, line))
        
        # TODO: 연산자와 기호 (+ - * / ( ) { } ; = == != < > <= >=)
        # 한 글자, 두 글자 가능성 
        # 두글자 : ==, !=, <=, >=
        elif ch in '+-*/(){};=!<>':
            oper = ''
            # '=', '!', '<', '>' 는 뒤에 '='가 붙으면 두 글자 연산자(==, !=, <=, >=)가 된다.
            # 한 글자만 보고 확정하면 "<="가 "<"와 "="로 갈라지므로 다음 글자를 미리 확인한다.
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

            # 읽은 글자(oper)를 토큰 이름으로 바꾸는 표. 파서는 '+' 대신 'PLUS' 같은 이름으로 판단한다.
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
                tok_type = 'GE'    # 위에서 모두 걸러졌으므로 남은 경우는 '>=' 뿐이다
            tokens.append(Token(tok_type, oper, line))    # 종류(tok_type)와 원래 글자(oper)를 함께 저장한다


        # TODO: 알 수 없는 문자는 줄 번호와 함께 에러 발생
        else:
            raise Exception(f"{line}번째 줄, 알 수 없는 문자 '{ch}'")

    # 끝 표시(EOF)를 붙이는 이유: 파서가 "더 읽을 토큰이 있는지"를 따로 검사하지 않고
    # peek()로 EOF만 확인하면 되게 해서, 목록 끝을 넘어 읽는 실수를 막는다.
    tokens.append(Token("EOF", "", line))
    return tokens

# 이 파일을 직접 실행했을 때만 동작하는 간단한 확인용 코드 (import 될 때는 실행되지 않는다)
if __name__ == "__main__":
    for t in tokenize("let x = 1 + 23;"):
        print(t)
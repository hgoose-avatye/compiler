# lexer.py에서 만든 토큰 목록(tokenize)을 받아 쓰기 위해 가져온다. (Token은 타입 참고용)
from lexer import Token, tokenize
# 노드를 "값만 담는 상자"로 짧게 만들기 위해 dataclass를 쓴다. (__init__, 출력 함수를 자동 생성)
from dataclasses import dataclass

# ---------- AST 노드 ----------
# AST(추상 구문 트리): 프로그램을 "트리 모양의 데이터"로 바꾼 것.
# 예) 1 + 2 * 3 -> BinOp(1, '+', BinOp(2, '*', 3))
# 트리로 만들어 두면 인터프리터는 글자를 다시 해석하지 않고 트리만 따라가며 실행하면 된다.

# 숫자 하나. 트리의 "잎(끝)"이라서 더 이상 아래로 내려가지 않는다.
@dataclass
class Number:
    value: int

# 변수 사용(읽기). 값은 실행할 때 알 수 있으므로 이름만 들고 있는다.
@dataclass
class Var:
    name: str

# 두 값 사이의 연산. 산술(+ - * /)과 비교(< > <= >= == !=)를 한 노드로 처리한다.
# left/right 타입이 object인 이유: Number일 수도, 또 다른 BinOp일 수도 있어서(트리가 중첩됨).
@dataclass
class BinOp:
    left: object
    op: str       # '+', '-', '*', '/', '<', '>', '<=', '>=', '==', '!='
    right: object

# let x = 값;  (새 변수 만들기)
@dataclass
class Let:
    name: str
    value: object

# print(값);  (화면에 출력)
@dataclass
class Print:
    value: object

# x = 값;  (이미 있는 변수의 값 바꾸기)
@dataclass
class Assign:
    name: str
    value: object

# { ... }  (문장 여러 개를 하나로 묶은 것. while/if의 본문으로 쓰인다)
@dataclass
class Block:
    statements: list      # { ... } 안의 문장들

# while (조건) { ... }
@dataclass
class While:
    cond: object
    body: object          # Block

# if (조건) { ... } else { ... }
@dataclass
class If:
    cond: object
    then_body: object     # Block
    else_body: object     # Block 또는 None (else가 없을 때)


# ---------- Parser ----------
# 재귀 하강 파서: 문법 규칙 하나를 함수 하나로 만든 파서.
# 규칙 안에 다른 규칙이 들어 있으면 함수가 다른 함수(때로는 자기 자신)를 부르는 식으로 읽는다.
# 우선순위가 낮은 규칙일수록 위(먼저 호출) 단계, 높은 규칙일수록 아래 단계에 둔다.
#   statement -> comparison -> expression -> term -> factor
class Parser:
    def __init__(self, tokens):
        # 역할: 토큰 목록과 "읽는 위치"를 저장해 파서를 준비한다.
        # 문법: (없음 - 준비 단계)
        # 호출 순서 예시: Parser(tokenize(src)) -> program() 으로 읽기 시작
        self.tokens = tokens  # 렉서가 만든 토큰 목록 (마지막은 항상 EOF)
        self.pos = 0          # 지금 보고 있는 토큰의 위치 (Lexer의 i와 같은 역할)

    def peek(self):
        # 역할: 현재 토큰을 "보기만" 한다 (위치는 그대로).
        # 문법: (없음 - 보조 함수)
        # 호출 순서 예시: term()에서 peek()로 '*'인지 확인 -> 맞으면 advance()
        # 왜 따로 두는가: 다음 토큰을 먹기 전에 어떤 규칙으로 읽을지 판단해야 하기 때문이다.
        # TODO: 현재 위치의 토큰을 돌려준다 (pos는 움직이지 않음)
        return self.tokens[self.pos]

    def advance(self):
        # 역할: 현재 토큰을 돌려주고 위치를 한 칸 앞으로 옮긴다 ("먹는다").
        # 문법: (없음 - 보조 함수)
        # 호출 순서 예시: peek()로 확인 -> advance()로 소비 -> 다음 토큰으로 이동
        # 왜 현재 토큰을 돌려주는가: 소비하면서 그 값(숫자, 이름, 연산자)을 바로 쓰기 위해서다.
        # TODO: 현재 토큰을 돌려주고, pos를 한 칸 앞으로 옮긴다
        cur = self.tokens[self.pos]   # 옮기기 "전"의 토큰을 먼저 저장해 둔다
        self.pos += 1                 # 다음 토큰을 가리키게 한다

        return cur

    def expect(self, tok_type):
        # 역할: "반드시 이 토큰이어야 한다"고 검사하고 먹는다. 아니면 에러를 낸다.
        # 문법: (없음 - 보조 함수. 예: ')' 나 ';' 가 꼭 있어야 하는 자리에서 사용)
        # 호출 순서 예시: let 문에서 expect('SEMI') -> ';' 가 없으면 줄 번호와 함께 에러
        # 왜 바로 에러를 내는가: 문법이 틀린 채로 계속 읽으면 엉뚱한 곳에서 에러가 나서 찾기 어렵다.
        # TODO: 현재 토큰의 type이 tok_type이면 advance하고 돌려준다
        #       아니면 줄 번호가 들어간 에러를 낸다
        tok = self.peek()
        if tok.type == tok_type:
            return self.advance()    # 맞으면 먹고, 그 토큰을 호출한 쪽에서 쓸 수 있게 돌려준다
        else:
            raise Exception(f"{tok.line}번째 줄: {tok_type} 필요, {tok.type} 발견")


    def factor(self):
        # 역할: 식의 가장 작은 단위(숫자, 변수, 괄호로 묶은 식)를 읽는다.
        # 문법: factor -> NUMBER | IDENT | '(' comparison ')'
        # 호출 순서 예시: "(1 + 2) * 3" -> term -> factor('(' 발견) -> comparison -> ... -> factor(3)
        # 왜 가장 아래 단계인가: 곱셈/덧셈보다 먼저 묶여야 하는 것(괄호 포함)을 여기서 처리한다.
        # TODO: NUMBER  -> Number 노드
        #       IDENT   -> Var 노드
        #       LPAREN  -> expression()을 부르고 RPAREN을 expect
        #       그 외   -> 에러
        if self.peek().type == 'NUMBER':
            tok = self.advance()
            return Number(int(tok.value))    # 토큰 값은 문자열이므로 int로 바꿔 숫자 노드를 만든다

        elif self.peek().type == 'IDENT':
            tok = self.advance()
            return Var(name = tok.value)     # 값은 실행 때 찾으므로 이름만 담는다

        elif self.peek().type == 'LPAREN':
            self.advance()    # '(' 는 묶음 표시일 뿐 트리에 필요 없어서 버린다
            # 여기서 comparison을 다시 부르는 이유(간접 재귀): 괄호 안에는 또 하나의 "완전한 식"이
            # 들어갈 수 있다. 식을 읽는 최상위 규칙을 처음부터 다시 적용해야 ((1+2)*3) 같은 중첩이 된다.
            node = self.comparison()    # (x < 3) 처럼 괄호 안 비교식도 허용
            self.expect('RPAREN')       # 여는 괄호가 있으면 닫는 괄호도 반드시 있어야 한다
            return node                 # 괄호 자체는 노드로 만들지 않고 안쪽 식을 그대로 돌려준다

        else:
            # 숫자/이름/'(' 중 어느 것도 아니면 식을 시작할 수 없는 토큰이므로 에러
            raise Exception(f"{self.peek().line}번째 줄: 예상치 못한 토큰 {self.peek().type}")



     # 곱셈(*)과 나눗셈(/)을 묶어 주는 함수
    def term(self):
        # 역할: 곱셈(*)과 나눗셈(/)으로 이어진 식을 왼쪽부터 묶어 BinOp 트리로 만든다.
        # 문법: term -> factor (('*' | '/') factor)*
        # 호출 순서 예시: "2 * 3 / 6" -> factor(2) -> '*' -> factor(3) -> '/' -> factor(6)
        # 왜 expression 아래 단계인가: 2 + 3 * 4 에서 곱셈이 먼저 계산되도록(우선순위) 하기 위해서다.
        # 왜 while로 왼쪽부터 묶는가: 10 / 5 / 2 를 (10/5)/2 로 읽는 "왼쪽 결합"을 지키기 위해서다.
        # TODO: factor를 먼저 읽고, STAR 또는 SLASH가 이어지는 동안
        #       반복해서 BinOp로 묶는다

        left = self.factor()    # 일단 첫 피연산자를 읽는다
        while self.peek().type in ('STAR', 'SLASH'):
            op = self.advance()        # 연산자 토큰('*' 또는 '/')을 먹는다
            right = self.factor()      # 오른쪽 피연산자를 읽는다
            left = BinOp(left, op.value, right)    # 지금까지 읽은 것을 통째로 left로 삼아 계속 이어 묶는다

        return left


    def expression(self):
        # 역할: 덧셈(+)과 뺄셈(-)으로 이어진 식을 왼쪽부터 묶어 BinOp 트리로 만든다.
        # 문법: expression -> term (('+' | '-') term)*
        # 호출 순서 예시: "1 + 2 * 3" -> term(1) -> '+' -> term(2 * 3) -> BinOp(1, '+', BinOp(2,'*',3))
        # 왜 term을 부르는가: 피연산자를 term으로 읽으면 곱셈이 자동으로 먼저 묶인다.
        # 왜 while로 왼쪽부터 묶는가: 10 - 3 - 2 가 (10-3)-2 = 5 가 되게 하려는 것이다.
        # TODO: term을 먼저 읽고, PLUS 또는 MINUS가 이어지는 동안
        #       반복해서 BinOp로 묶는다

        left = self.term()    # 첫 피연산자 (곱셈/나눗셈은 term 안에서 이미 묶여 있다)
        while self.peek().type in ('PLUS', 'MINUS'):
            tok_type = self.peek().type

            op = self.advance()        # '+' 또는 '-' 를 먹는다
            right = self.term()        # 오른쪽도 term으로 읽어야 "1 + 2 * 3"에서 곱셈이 먼저 묶인다
            left = BinOp(left, op.value, right)    # 왼쪽부터 차례로 묶어 올라간다

        return left

    def comparison(self):
        # 역할: 덧셈/뺄셈 식 두 개를 <, >, <=, >=, ==, != 로 비교해 BinOp로 묶는다.
        # 문법: comparison -> expression (('<'|'>'|'<='|'>='|'=='|'!=') expression)*
        # 호출 순서 예시: "x > 0" -> comparison -> expression(x) -> '>' -> expression(0)
        #
        # 왜 expression보다 "위" 단계인가: 1 + 2 < 4 가 (1+2) < 4 로 읽히려면
        # 산술이 비교보다 먼저(더 강하게) 묶여야 하기 때문이다. 우선순위가 낮을수록 위 단계에 둔다.
        left = self.expression()    # 여기서 expression을 부르는 이유: 비교의 양쪽은 산술식이기 때문
        while self.peek().type in ('LT', 'GT', 'LE', 'GE', 'EQEQ', 'NEQ'):
            op = self.advance()
            right = self.expression()
            left = BinOp(left, op.value, right)
        return left

    def block(self):
        # 역할: { 문장들 } 을 읽어 Block 노드로 만든다.
        # 문법: block -> '{' statement* '}'
        # 호출 순서 예시: while (...) { print(x); } -> statement -> block -> statement(print)
        self.expect('LBRACE')
        statements = []
        while self.peek().type not in ('RBRACE', 'EOF'):
            # 여기서 statement를 다시 부르는 이유: 블록 안에도 let/print/while/if/{}가
            # 그대로 올 수 있어서, 문장 읽는 규칙을 재사용하면 중첩이 공짜로 된다.
            statements.append(self.statement())
        self.expect('RBRACE')    # EOF에서 멈췄다면 여기서 "} 필요" 에러가 난다
        return Block(statements)

    def while_statement(self):
        # 역할: while (조건) { ... } 한 문장을 읽는다.
        # 문법: while_stmt -> 'while' '(' comparison ')' block
        # 호출 순서 예시: statement -> while_statement -> comparison -> block -> statement...
        self.expect('WHILE')
        self.expect('LPAREN')
        cond = self.comparison()
        self.expect('RPAREN')
        body = self.block()    # 본문도 block 규칙으로 읽는다 (재귀: block 안에서 다시 statement)
        return While(cond, body)

    def if_statement(self):
        # 역할: if (조건) { ... } [else { ... }] 한 문장을 읽는다.
        # 문법: if_stmt -> 'if' '(' comparison ')' block ('else' block)?
        # 호출 순서 예시: statement -> if_statement -> comparison -> block -> (else면) block
        self.expect('IF')
        self.expect('LPAREN')
        cond = self.comparison()
        self.expect('RPAREN')
        then_body = self.block()
        else_body = None    # else는 있어도 되고 없어도 되므로 기본값은 None
        if self.peek().type == 'ELSE':
            self.advance()
            else_body = self.block()
        return If(cond, then_body, else_body)

    def statement(self):
        # 역할: 문장 하나(let, print, 대입, 블록, while, if)를 읽어 노드로 만든다.
        # 문법: statement -> let_stmt | print_stmt | assign_stmt | block | while_stmt | if_stmt
        # 호출 순서 예시: "let x = 5;" -> program -> statement -> LET 분기 -> comparison
        # 왜 첫 토큰만 보고 고르는가: 문장마다 시작이 let, print, 이름, '{', while, if 로
        #   서로 달라서 한 토큰만 봐도 어떤 문장인지 알 수 있기 때문이다.
        # 재귀: 블록/while/if 본문 안에서 statement가 다시 불린다 (block 함수 참고).
        # TODO: 현재 토큰이 LET이면
        tok = self.peek()    # 먹지 않고 보기만 한다. 어떤 문장인지 고른 뒤에 각 분기에서 먹는다
        if tok.type == 'LET':
        #   1) LET 소비 (expect)
            self.expect('LET')
        #   2) IDENT를 expect해서 이름 토큰을 받는다
            val = self.expect('IDENT')
        #   3) EQ expect
            self.expect('EQ')
        #   4) value = self.expression()
            value = self.comparison()    # let b = x < 3; 허용
        #   5) SEMI expect
            self.expect('SEMI')
        #   6) return Let(이름, value)
            return Let(val.value, value)

        # TODO: 현재 토큰이 PRINT면
        elif tok.type == 'PRINT':
        #   1) PRINT 소비
            self.expect('PRINT')
        #   2) LPAREN expect
            self.expect('LPAREN')
        #   3) value = self.expression()
            value = self.comparison()    # print(x < 3); 허용
        #   4) RPAREN expect
            self.expect('RPAREN')
        #   5) SEMI expect
            self.expect('SEMI')
        #   6) return Print(value)
            return Print(value)

        # 새로 추가한 문장들: 대입(x = ...;), 블록, while, if
        elif tok.type == 'IDENT':
            # 이름이 맨 앞에 오면 대입문이다. (이름만 쓰는 문장은 이 언어에 없다)
            self.advance()                  # 이름 토큰을 먹는다 (tok에 이미 저장해 두었다)
            self.expect('EQ')               # 이름 다음에는 반드시 '=' 가 와야 한다
            value = self.comparison()
            self.expect('SEMI')
            return Assign(tok.value, value)
        elif tok.type == 'LBRACE':
            return self.block()             # '{' 로 시작하면 블록 하나가 곧 문장이다
        elif tok.type == 'WHILE':
            return self.while_statement()
        elif tok.type == 'IF':
            return self.if_statement()
        # TODO: 그 외면 에러 (줄 번호와 토큰 type 포함)
        else:
            raise Exception(f"{self.peek().line}번째 줄: 예상치 못한 토큰 {self.peek().type}")


    def program(self):
        # 역할: 파일 전체를 읽어 "문장 리스트"로 만든다. 파싱의 시작점이다.
        # 문법: program -> statement* EOF
        # 호출 순서 예시: program -> statement -> statement -> ... (EOF를 만나면 종료)
        # 왜 EOF까지 반복하는가: 문장이 몇 개인지 미리 알 수 없어서 끝 표시가 나올 때까지 읽는다.
        # TODO: statements = []
        #       현재 토큰이 EOF가 아닌 동안 statement()를 호출해 리스트에 추가
        statements = []
        while(self.peek().type != 'EOF'):
            statements.append(self.statement())    # 문장 하나를 읽을 때마다 pos가 전진하므로 언젠가 EOF에 닿는다
        return statements


# 직접 실행했을 때만 도는 확인용 코드 (파서가 만든 트리를 눈으로 볼 수 있다)
if __name__ == "__main__":
    for src in ["1 + 2 * 3", "(1 + 2) * 3", "10 - 3 - 2", "x + 1"]:
        print(src)
        print(Parser(tokenize(src)).expression())

    src = "let x = 5; print(x * 2 + 1);"
    print(Parser(tokenize(src)).program())

# 파서가 만든 노드 종류를 알아야 isinstance로 구별할 수 있으므로 모두 가져온다.
from parser import Number, Var, BinOp, Let, Print, Assign, Block, While, If, Parser
# 소스 문자열 -> 토큰 변환용. 아래 확인용 코드에서 쓴다.
from lexer import tokenize


# 트리 순회 인터프리터: 파서가 만든 AST를 위에서 아래로 따라가며 바로 실행한다.
# 값을 "계산"하는 일은 eval, 변화를 "일으키는" 일(저장/출력/반복)은 execute가 맡는다.
class Interpreter:
    def __init__(self):
        # 역할: 변수 저장소를 빈 상태로 만든다.
        # 문법: (없음 - 준비 단계)
        # 호출 순서 예시: Interpreter() -> run(문장들) 중에 let/대입이 self.vars를 채운다
        # 왜 인스턴스마다 따로 두는가: 프로그램 하나가 실행될 때만 변수가 유지되고,
        #   다른 실행에 값이 새어 나가지 않게 하려는 것이다.
        self.vars = {}    # 변수 저장소 (이름 -> 값)

    def eval(self, node):
        # 역할: 식(Number, Var, BinOp)을 계산해서 "값 하나"로 돌려준다.
        # 문법: expr -> Number | Var | BinOp(left, op, right)   (비교 결과는 1 또는 0)
        # 호출 순서 예시: BinOp(1,'+',BinOp(2,'*',3)) -> eval(왼쪽 1) -> eval(오른쪽: 2*3 -> 6) -> 7
        # 왜 execute가 아니라 eval인가: 식은 값을 만들 뿐 화면 출력이나 저장 같은 부수 효과가 없다.
        # TODO: node의 종류에 따라 값을 계산해서 돌려준다
        #   Number -> node.value
        if isinstance(node, Number):
            return node.value    # 숫자는 이미 값이라 계산할 것이 없다 (재귀의 끝)
        #   Var    -> self.vars에서 node.name을 찾아 돌려준다 (없으면 에러)
        if isinstance(node, Var):
            if node.name in self.vars:
                return self.vars[node.name]    # 저장소에서 현재 값을 꺼낸다 (재귀의 끝)
            else:
                # 만든 적 없는 이름을 조용히 0으로 취급하면 오타를 못 찾으므로 바로 에러
                raise Exception(f"정의되지 않은 변수 : {node.name}")
        #   BinOp  -> 왼쪽과 오른쪽을 eval로 계산한 뒤 node.op에 맞게 연산
        if isinstance(node, BinOp):
            # 여기서 eval을 다시 부르는 이유(재귀): 왼쪽/오른쪽도 숫자일 수도, 또 다른 BinOp일 수도 있다.
            # 트리의 맨 끝(Number, Var)에 닿을 때까지 같은 규칙을 반복해야 전체 값이 정해진다.
            left = self.eval(node.left)
            right = self.eval(node.right)
            if node.op == '+':
                return left + right
            elif node.op == '-':
                return left - right
            elif node.op == '*':
                return left * right
            elif node.op == '/':
                if right == 0:
                    # 0으로 나누면 파이썬 에러 메시지가 나오는데, 이 언어 사용자가 이해하도록 직접 안내한다
                    raise Exception(f"0으로 나누면 에러 : {node.right}")
        #             ('/'는 정수 나눗셈 //, 0으로 나누면 에러)
                else:
                    return left // right    # // 는 소수점을 버리는 정수 나눗셈 (이 언어엔 정수만 있다)
            # 비교 연산: 파이썬의 True/False 대신 1/0으로 돌려준다.
            # 이 언어에는 숫자밖에 없어서, 조건식 결과도 숫자로 통일해야 계산에 다시 쓸 수 있다.
            elif node.op == '<':
                return 1 if left < right else 0
            elif node.op == '>':
                return 1 if left > right else 0
            elif node.op == '<=':
                return 1 if left <= right else 0
            elif node.op == '>=':
                return 1 if left >= right else 0
            elif node.op == '==':
                return 1 if left == right else 0
            elif node.op == '!=':
                return 1 if left != right else 0


    def execute(self, stmt):
        # 역할: 문장 하나(Let, Print, Assign, Block, While, If)를 실행한다.
        # 문법: stmt -> Let | Print | Assign | Block | While | If
        # 호출 순서 예시: While -> eval(조건) -> execute(본문 Block) -> run -> execute(Print) ...
        # 왜 isinstance로 나누는가: 노드 종류마다 해야 할 일이 달라서, 종류를 확인한 뒤 해당 처리를 한다.
        # 재귀: Block/While/If는 안에 또 문장을 품고 있어서 execute가 execute를 다시 부른다.
        # TODO: 문장의 종류에 따라 실행한다
        #   Let   -> 값을 eval해서 self.vars[이름]에 저장
        if isinstance(stmt, Let):
            # 오른쪽 식을 먼저 계산(eval)한 뒤 그 "값"을 저장한다. 같은 이름이면 덮어쓴다.
            self.vars[stmt.name] = self.eval(stmt.value)
        #   Print -> 값을 eval해서 print
        if isinstance(stmt, Print):
            print(self.eval(stmt.value))    # 식 자체가 아니라 계산 결과를 출력해야 하므로 eval을 거친다

        # 대입: let과 달리 이미 있는 변수만 바꿀 수 있다.
        # 오타로 새 변수가 조용히 생기는 것을 막기 위해 없으면 에러를 낸다.
        if isinstance(stmt, Assign):
            if stmt.name not in self.vars:
                raise Exception(f"정의되지 않은 변수 : {stmt.name}")
            self.vars[stmt.name] = self.eval(stmt.value)

        # 블록: 안의 문장을 순서대로 실행한다. run()이 하는 일과 같으므로 재사용한다.
        if isinstance(stmt, Block):
            self.run(stmt.statements)

        # while: 조건이 0이 아닌 동안 본문을 반복한다.
        # 조건을 "매 반복마다 다시" eval하는 것이 핵심이다. 한 번만 계산하면
        # 값이 바뀌어도 알 수 없어서 영원히 돌거나 아예 안 돈다.
        # 예) let x = 3; while (x > 0) { print(x); x = x - 1; }
        #   1회전: x=3, 3>0 → 1(참) → 3 출력, x = 3-1 = 2
        #   2회전: x=2, 2>0 → 1(참) → 2 출력, x = 2-1 = 1
        #   3회전: x=1, 1>0 → 1(참) → 1 출력, x = 1-1 = 0
        #   4회전: x=0, 0>0 → 0(거짓) → 반복 종료
        # 즉 x는 3 → 2 → 1 → 0 으로 변하고, 0이 되는 순간 조건이 거짓이 되어 멈춘다.
        if isinstance(stmt, While):
            while self.eval(stmt.cond) != 0:
                # 여기서 execute를 다시 부르는 이유: 본문(Block) 안에 또 while/if가
                # 올 수 있어서, 문장 실행 규칙(execute)을 그대로 재사용한다.
                self.execute(stmt.body)

        # if: 조건이 0이 아니면 then, 0이고 else가 있으면 else를 실행한다.
        # 여기서도 execute를 다시 부르는 이유는 while과 같다 (본문 안에 중첩 문장 가능).
        if isinstance(stmt, If):
            if self.eval(stmt.cond) != 0:
                self.execute(stmt.then_body)
            elif stmt.else_body is not None:
                self.execute(stmt.else_body)


    def run(self, statements):
        # 역할: 문장 리스트를 처음부터 끝까지 차례로 실행한다.
        # 문법: program -> statement*   /   block -> '{' statement* '}'
        # 호출 순서 예시: run([Let, While]) -> execute(Let) -> execute(While) -> (본문) run([...])
        # 왜 Block도 이 함수를 쓰는가: "문장 목록을 순서대로 실행"하는 일은 프로그램 전체나
        #   블록 안이나 똑같기 때문에 하나로 재사용한다. (Block -> execute -> run: 간접 재귀)
        # TODO: 문장 리스트를 순서대로 execute
        for s in statements:
            self.execute(s)    # 앞 문장이 끝나야 다음 문장을 실행한다 (let으로 만든 변수를 뒤에서 쓰기 때문)



# 직접 실행했을 때만 도는 확인용 코드: 11이 출력되면 정상
if __name__ == "__main__":
    src = "let x = 5; print(x * 2 + 1);"    # 5*2+1 = 11
    # 소스 문자열 -> tokenize(토큰) -> Parser.program(트리) -> run(실행) 순서로 흘러간다
    Interpreter().run(Parser(tokenize(src)).program())    # 11이 출력되어야 함

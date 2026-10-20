# emitter(코드 생성기) 스켈레톤 - TODO를 채워 가며 직접 완성해 보자.
#
# interpreter는 AST를 따라가며 "값"을 계산했다.
# emitter는 같은 AST를 따라가며 "C 코드 문자열"을 만들어 낸다. (Lexer, Parser는 그대로 쓴다)
#
#   소스 -> Lexer -> Parser -> [Emitter] -> C 코드(문자열) -> gcc 로 컴파일 -> 실행
#
# 생각해 볼 질문 하나: interpreter.py 의 eval/execute 와 구조가 거의 같다.
#   다른 점은 "돌려주는 것이 값이 아니라 문자열"이라는 것뿐이다. 어디가 같고 어디가 다른지 찾아보자.
from parser import Number, Var, BinOp, Let, Print, Assign, Block, While, If, Parser
from lexer import tokenize

INDENT = "    "    # C 코드를 읽기 좋게 들여쓰기 한 단계 (공백 4칸)


class Emitter:
    def __init__(self):
        # TODO: 이미 C에서 선언한 변수 이름을 모아 둘 저장소를 만들어라 (self.declared)
        #   힌트: 이 언어는 `let x = 1; let x = 2;` 가 가능하지만, C에서 `int x` 를 두 번 쓰면
        #         컴파일 에러다. 이름이 "이미 선언됐는지" 기억해야 하는데 어떤 자료구조가 좋을까?
        # SET을 작성하여 변수를 저장한다.
        pass

    def emit_expr(self, node):
        # 식 노드를 C 식 "문자열"로 바꿔 돌려준다. (interpreter의 eval과 같은 구조)
        #
        # TODO: Number -> 숫자를 문자열로            예) Number(5)   -> "5"
        # TODO: Var    -> 변수 이름 그대로            예) Var("x")    -> "x"
        # TODO: BinOp  -> 왼쪽/오른쪽을 emit_expr 로 문자열로 만든 뒤 "(왼쪽 연산자 오른쪽)" 로 묶는다
        #         예) 1 + 2 * 3 의 트리 -> "(1 + (2 * 3))"
        #   생각해 볼 것 1) 왜 emit_expr 이 자기 자신을 다시 불러야 할까? (eval 의 BinOp 와 비교)
        #   생각해 볼 것 2) 왜 항상 괄호로 감쌀까? 괄호를 빼면 (1 + 2) * 3 은 어떻게 될까?
        #   생각해 볼 것 3) 비교 연산자(< > <= >= == !=)는 따로 변환이 필요할까?
        #                   (힌트: C 에서 비교의 결과는 무엇인가)
        # 위에 없는 노드가 들어오면 에러를 내자 (raise Exception)
        pass

    def emit_stmt(self, stmt, level):
        # 문장 노드 하나를 C 코드 "줄(문자열)들의 리스트"로 바꿔 돌려준다. (interpreter의 execute와 같은 구조)
        # level 은 들여쓰기 단계다. 줄 앞에 INDENT * level 을 붙인다.
        #
        # TODO: Let    -> "int 이름 = 식;"            예) int x = 5;
        #                 단, 이미 선언된 이름이면 "이름 = 식;" 만 (int 없이)
        #                 처음 선언하면 self.declared 에 이름을 기록하는 것도 잊지 말자
        # TODO: Assign -> "이름 = 식;"                예) x = (x - 1);
        # TODO: Print  -> printf 로 출력               예) printf("%d\n", x);
        #   생각해 볼 것) %d 는 무슨 뜻이고, \n 은 왜 필요할까? 파이썬의 print 와 어떻게 맞출까?
        #   주의) 파이썬 문자열 안에서 \n 을 C 코드 글자로 남기려면 어떻게 써야 할까? ("\\n")
        # TODO: Block  -> "{" 줄, 안쪽 문장들(들여쓰기 level + 1), "}" 줄
        #   생각해 볼 것) 안쪽 문장들을 만들 때 emit_stmt 를 다시 부르게 된다. 왜일까?
        # TODO: While  -> "while (조건)" 줄 + 본문 Block
        #   생각해 볼 것) interpreter 는 파이썬 while 로 반복을 "직접 돌렸다".
        #                 emitter 는 반복을 돌리지 않는다. 대신 무엇을 만들어 낼까?
        #                 x = 3 → 2 → 1 → 0 은 언제, 누가 계산하게 될까?
        # TODO: If     -> "if (조건)" 줄 + then 본문, else 가 있으면 "else" 줄 + else 본문
        #   힌트) else_body 가 None 인지 확인해야 한다
        # 위에 없는 문장이 들어오면 에러를 내자
        pass

    def emit_program(self, statements):
        # 문장 리스트 전체를 "컴파일 가능한 C 프로그램 한 편"(문자열)으로 만든다.
        #
        # TODO: 아래 틀을 완성해라
        #       #include <stdio.h>
        #
        #       int main(void) {
        #           (모든 문장을 emit_stmt 로 변환한 줄들, level 은 1부터)
        #           return 0;
        #       }
        #   생각해 볼 것) 왜 main 함수와 #include 로 감싸야 할까? C 는 함수 밖에 문장을 쓸 수 있을까?
        #   힌트) 줄 리스트를 만든 뒤 "\n".join(...) 으로 한 문자열로 합치면 편하다
        pass


# 직접 실행했을 때만 도는 확인용 코드: 소스 -> 토큰 -> 트리 -> C 코드 순서로 흘러간다
if __name__ == "__main__":
    src = """
    let x = 3;
    while (x > 0) {
      print(x);
      x = x - 1;
    }
    """
    print(Emitter().emit_program(Parser(tokenize(src)).program()))
    # 완성되면 이 출력을 out.c 로 저장해서 확인해 보자:
    #   python3 emitter.py > out.c && gcc out.c -o out && ./out     # 3, 2, 1 이 나와야 한다

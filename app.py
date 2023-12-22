import pathlib
from functools import reduce
import operator as op


class MiniLisp:

    def __init__(self):
        pass

    def interpret(self, test_string: str):
        test_string = test_string.replace('\n', ' ')
        test_string = test_string.replace('(', ' ( ')
        test_string = test_string.replace(')', ' ) ')
        test_string = f"( {test_string} )"

        tokens = test_string.split()
        stacks = self.dfs(tokens)
        operation_table = Env()

        for expression in stacks:
            MiniLisp.solve(expression, operation_table)

    def dfs(self, tokens):
        token = tokens.pop(0)
        if token == "(":
            L = []
            while tokens[0] != ")":
                L.append(self.dfs(tokens))
            tokens.pop(0)
            return L
        else:
            try:
                return int(token)
            except:
                return token

    @staticmethod
    def solve(expression, operation_table):
        if isinstance(expression, str):
            return operation_table.locate(expression)[expression]

        if isinstance(expression, int):
            return expression

        operation, *args = expression

        if operation == "define":
            operation_table[args[0]] = MiniLisp.solve(args[1], operation_table)
            return

        if operation == "fun":
            fun_name, *fun_stack = args
            return Function(fun_name, fun_stack, operation_table)

        if operation == "if":
            if_statement, true_expression, false_expression = args

            result = MiniLisp.solve(if_statement, operation_table)
            assert isinstance(result, bool), TypeError("if test-exp didn't return bool")

            if result:
                return MiniLisp.solve(true_expression, operation_table)
            else:
                return MiniLisp.solve(false_expression, operation_table)

        return MiniLisp.solve(operation, operation_table)(*[MiniLisp.solve(arg, operation_table) for arg in args])


class Operator:
    @staticmethod
    def n_argument_error(n, lens):
        return TypeError(f"Need {n} arguments, but got {lens}.")

    @staticmethod
    def add(*args):
        assert len(args) >= 2, Operator.n_argument_error(2, len(args))
        Operator.check_type(args, int)
        return reduce(op.add, args)

    @staticmethod
    def sub(*args):
        assert len(args) == 2, Operator.n_argument_error(2, len(args))
        Operator.check_type(args, int)
        return op.sub(*args)

    @staticmethod
    def mul(*args):
        assert len(args) >= 2, Operator.n_argument_error(2, len(args))
        Operator.check_type(args, int)
        return reduce(op.mul, args)

    @staticmethod
    def div(*args):
        assert len(args) == 2, Operator.n_argument_error(2, len(args))
        Operator.check_type(args, int)
        return op.floordiv(*args)

    @staticmethod
    def mod(*args):
        assert len(args) == 2, Operator.n_argument_error(2, len(args))
        Operator.check_type(args, int)
        return op.mod(*args)

    @staticmethod
    def equal(*args):
        assert len(args) >= 2, Operator.n_argument_error(2, len(args))
        Operator.check_type(args, int)
        return all(bool(args[0] == arg) for arg in args)

    @staticmethod
    def less_than(*args):
        assert len(args) == 2, Operator.n_argument_error(2, len(args))
        Operator.check_type(args, int)
        return op.lt(*args)

    @staticmethod
    def greater_than(*args):
        assert len(args) == 2, Operator.n_argument_error(2, len(args))
        Operator.check_type(args, int)
        return op.gt(*args)

    @staticmethod
    def and_operator(*args):
        assert len(args) >= 2, Operator.n_argument_error(2, len(args))
        Operator.check_type(args, bool)
        return bool(reduce(op.and_, args))

    @staticmethod
    def or_operator(*args):
        assert len(args) >= 2, Operator.n_argument_error(2, len(args))
        Operator.check_type(args, bool)
        return bool(reduce(op.or_, args))

    @staticmethod
    def not_operator(*args):
        assert len(args) == 1, Operator.n_argument_error(1, len(args))
        Operator.check_type(args, bool)
        return op.not_(*args)

    @staticmethod
    def check_type(args, check_typing):
        for i in args:
            if type(i) != check_typing:
                if check_typing == int:
                    raise TypeError(f"syntax error, unexpected {i}")
                elif check_typing == bool:
                    raise TypeError(f"syntax error, unexpected {i}")


class Function:
    def __init__(self, params, stacks, operation_table):
        self.params = params
        self.stacks = stacks
        self.operation_table = operation_table

    def __call__(self, *args):
        n_operation_table = Env(self.params, args, self.operation_table)

        res = None
        for expression in self.stacks:
            res = MiniLisp.solve(expression, n_operation_table)

        return res


class Env(dict):
    def __init__(self, params=None, args=None, outer=None):

        params = params or {}
        args = args or {}

        self.outer = outer
        super().__init__(self)
        std_env = {
            "#t": True,
            "#f": False,
            "+": Operator.add,
            "-": Operator.sub,
            "*": Operator.mul,
            "/": Operator.div,
            "mod": Operator.mod,
            "=": Operator.equal,
            ">": Operator.greater_than,
            "<": Operator.less_than,
            "and": Operator.and_operator,
            "or": Operator.or_operator,
            "not": Operator.not_operator,
            "print-num": print,
            "print-bool": lambda x: print("#t" if x else "#f"),
        }
        self.update(std_env)
        self.update(zip(params, args))

    def locate(self, var):
        if var in self:
            return self
        elif self.outer:
            return self.outer.locate(var)
        else:
            raise Exception(f"Variable not found: {var}")


if __name__ == "__main__":
    lsp_files = list(pathlib.Path("public_test_data").glob("*.lsp"))
    ML = MiniLisp()
    lsp_file_contents = []

    for lsp_file in lsp_files:
        with open(lsp_file, 'r') as f:
            lsp_file_contents.append(f.read())

    for lsp_file, lsp_file_content in zip(lsp_files, lsp_file_contents):
        print(f"{lsp_file=}")
        try:
            ML.interpret(lsp_file_content)
        except Exception as e:
            print(e)

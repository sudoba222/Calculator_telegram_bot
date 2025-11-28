import ast
import operator as op

OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}

class SafeEval(ast.NodeVisitor):
    def visit(self, node):
        if isinstance(node, ast.Expression):
            return self.visit(node.body)
        elif isinstance(node, ast.BinOp):
            left = self.visit(node.left)
            right = self.visit(node.right)
            oper = OPERATORS.get(type(node.op))
            if oper is None:
                raise ValueError("Unsupported operator")
            return oper(left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = self.visit(node.operand)
            oper = OPERATORS.get(type(node.op))
            if oper is None:
                raise ValueError("Unsupported unary operator")
            return oper(operand)
        elif isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Unsupported constant")
        elif isinstance(node, ast.Num):  # Python <3.8
            return node.n
        else:
            raise ValueError("Unsupported expression")

def safe_eval(expr: str):
    """
    Safely evaluate arithmetic expressions.
    Allowed: + - * / % **, parentheses, unary +/-
    """
    expr = expr.strip()
    if not expr:
        raise ValueError("Empty expression")
    try:
        tree = ast.parse(expr, mode="eval")
        evaluator = SafeEval()
        return evaluator.visit(tree)
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")
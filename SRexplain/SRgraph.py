from sympy import sympify

operators = {''}

def get_graph(equation):
    args = equation.args
    if len(args) == 0:
        return str(equation)
    elif len(args) == 1:
        get_graph()
import re
import optimizer
import nf_convertor
import resolution

PRECEDENCE = {'!' : 4 , 'not' : 4 , 'and' : 3 , 'or' : 2 , '=>' : 1 , '<=>' : 1}

def tokenize(s):
    token_pattern = re.compile(r'not|and|or|<=>|=>|⇔|⇒|∧|∨|¬|[()!⊤⊥]|[a-zA-Z][a-zA-Z0-9_]*')
    tokens = token_pattern.findall(s)
    return tokens

def parse_expression(s):
    tokens = tokenize(s)
    if not tokens:
        raise ValueError("Empty expression!")

    output_queue = []
    op_stack = []
    normalized_tokens = []

    for token in tokens:
        if token == '¬':
            normalized_tokens.append('not')
        elif token == '∧':
            normalized_tokens.append('and')
        elif token == '∨':
            normalized_tokens.append('or')
        elif token == '⇒':
            normalized_tokens.append('=>')
        elif token == '⇔':
            normalized_tokens.append('<=>')
        else:
            normalized_tokens.append(token)
                    
    tokens = normalized_tokens

    for token in tokens:

        if (token[0].isalpha() and token not in PRECEDENCE) or token in {'⊤' , '⊥'}:
            output_queue.append(token)
        elif token in PRECEDENCE:
            while(op_stack and op_stack[-1] != '(' and (op_stack[-1] in PRECEDENCE and (PRECEDENCE[op_stack[-1]] > PRECEDENCE[token]))):
                output_queue.append(op_stack.pop())
            op_stack.append(token)
        elif token == '(':
            op_stack.append(token)
        elif token == ')':
            while op_stack and op_stack[-1] != '(':
                output_queue.append(op_stack.pop())
            if not op_stack:
                raise ValueError("Mismatched parenthesis")
            op_stack.pop()

    while op_stack:
        op = op_stack.pop()
        if op in {'(' , ')'}:
            raise ValueError("Mismatched parenthesis")
        output_queue.append(op)

    ast_stack = []
    for token in output_queue:
        if (token[0].isalpha() and token not in PRECEDENCE) or token in {'⊤' ,'⊥'}:
            ast_stack.append(token)
        elif token in {'!' , 'not'}:
            if not ast_stack:
                raise ValueError("Invalid syntax")
            sub = ast_stack.pop()
            ast_stack.append(('not' , sub))
        elif token in ('and' , 'or' , '=>' , '<=>'):
            if len(ast_stack) < 2:
                raise ValueError("Invalid syntax")
            right = ast_stack.pop()
            left = ast_stack.pop()
            ast_stack.append((token , left , right))
        else:
            raise ValueError(f"Unkown token : {token}")
    if len(ast_stack) != 1:
        raise ValueError("Invalid syntax")

    return ast_stack[0]

def is_valid_expression(s):
    try:
        parse_expression(s)
        return True
    except ValueError:
        return False

def evaluate_expression(syntax_tree , interpretation):
    if type(syntax_tree) is str:
        if syntax_tree == '⊤':
            return True
        if syntax_tree == '⊥':
            return False
        return interpretation[syntax_tree]

    op = syntax_tree[0]

    if op == "not":
        return not evaluate_expression(syntax_tree[1] , interpretation)
    elif op == "and":
            return evaluate_expression(syntax_tree[1] , interpretation) and evaluate_expression(syntax_tree[2] , interpretation)
    elif op == "or":
        return evaluate_expression(syntax_tree[1] , interpretation) or evaluate_expression(syntax_tree[2] , interpretation)
    elif op == "=>":
        return (not evaluate_expression(syntax_tree[1] , interpretation)) or evaluate_expression(syntax_tree[2] , interpretation)
    elif op == "<=>":
        return evaluate_expression(syntax_tree[1] , interpretation) == evaluate_expression(syntax_tree[2] , interpretation)

    raise ValueError("Unknown operation!")

def tree_print(node , prefix = "" , is_tail = True):
    if type(node) is str:
        if is_tail:
            conn = "└──"
        else:
            conn = "├──"
        print(prefix + conn + node)
        return

    op = node[0]
    if is_tail:
        conn = "└──"
    else:
        conn = "├──"

    print(prefix + conn + op)

    if is_tail:
        extension = "   "
    else:
        extension = "│  "

    new_prefix = prefix + extension

    if op == "not":
        tree_print(node[1] , new_prefix , is_tail = True)
    else:
        tree_print(node[1] , new_prefix , is_tail = False)
        tree_print(node[2] , new_prefix , is_tail = True)

def generate_valuations(variables , index = 0 , current_val = None , all_val = None):
    if all_val is None:
        all_val = []
    if current_val is None:
        current_val = []

    if index == variables:
        all_val.append(current_val.copy())
        return all_val

    
    current_val.append(False)
    generate_valuations(variables , index + 1 , current_val , all_val)
    current_val.pop()

    current_val.append(True)
    generate_valuations(variables , index + 1 , current_val , all_val)
    current_val.pop()
    
    return all_val

def get_variables(node):
    if type(node) is str:
        if node in {'⊤', '⊥'}:
            return set()
        return {node}
    op = node[0]
    if op == "not":
        return get_variables(node[1])
    else:
        return get_variables(node[1]).union(get_variables(node[2]))

def generate_interpretations(variables , valuations):
    interpretations = []
    vars = list(variables)
    for val in valuations:
        interpretation = {}
        for i , var in enumerate(vars):
            interpretation[var] = val[i]
        interpretations.append(interpretation)
    return interpretations

def ast_to_string(node):
    if type(node) is str:
        return node
    op = node[0]
    if op == "not":
        sub_str = ast_to_string(node[1])
        if type(node[1]) is str:
            return f"!{sub_str}"
        else:
            return f"!({sub_str})"
    else:
        left_str = ast_to_string(node[1])
        right_str = ast_to_string(node[2])

        if type(node[1]) is tuple and node[1][0] not in ('not' , op):
            left_str = f"({left_str})"

        if type(node[2]) is tuple and node[2][0] not in ('not' , op):
            right_str = f"({right_str})"

        return f"{left_str} {op} {right_str}"

def get_sub_trees(node , sub_list = None):
    if sub_list is None:
        sub_list = []
    if type(node) is str:
        return sub_list
    op = node[0]
    if op == "not":
        get_sub_trees(node[1] , sub_list)
    else:
        get_sub_trees(node[1] , sub_list)
        get_sub_trees(node[2] , sub_list)

    if node not in sub_list:
        sub_list.append(node)
    return sub_list

def truth_table(s):
    ast = parse_expression(s)
    variables = sorted(list(get_variables(ast)))

    sub_trees = get_sub_trees(ast)
    sub_headers = [ast_to_string(st) for st in sub_trees]

    all_columns = variables + sub_headers
    col_widths = [max(len(col), 3) for col in all_columns]
    result_width = max(len("Result"), 6)

    formatted_header = [all_columns[i].center(col_widths[i]) for i in range(len(all_columns))]
    header = " | ".join(formatted_header) + " || " + "Result".center(result_width)
    print(header)
    print("-" * len(header))

    final_results = []
    valuations = generate_valuations(variables)

    for val in valuations:
        interpretation = {variables[i] : val[i] for i in range (len(variables))}
        p_vals = ["T" if interpretation[i] else "F" for i in variables]
        st_vals = []
        
        for st in sub_trees:
            res = evaluate_expression(st , interpretation)
            st_vals.append("T" if res else "F")

        all_row_vals = p_vals + st_vals
        final_res = evaluate_expression(ast , interpretation)
        final_results.append(final_res)

        formatted_row = [all_row_vals[i].center(col_widths[i]) for i in range(len(all_row_vals))]
        row = " | ".join(formatted_row)
        res = ("T" if final_res else "F").center(result_width)
        print(f"{row} || {res}")

    print("-" * len(header))

    if all(final_results):
        print("Valid (Tautology)")
    elif not any(final_results):
        print("Unsatisfiable (Contradiction)")
    else:
        print("Satisfiable & Invalid")

    return all(final_results)

def generate_formula(variables , truth_values):
    if len(truth_values) != 2 ** len(variables):
        raise ValueError("Number of truth values must be exactly 2^n.")

    true_clauses = []
    valuations = generate_valuations(variables)

    for i in range(len(truth_values)):
        if truth_values[i]:
            curr_val = valuations[i]
            parts = []

            for j in range(len(variables)):
                if curr_val[j]:
                    parts.append(variables[j])
                else:
                    parts.append(f"¬{variables[j]}")

            true_clauses.append("(" + " ∧ ".join(parts) + ")")

    if not true_clauses:
        return "⊥"

    return " ∨ ".join(true_clauses)    

def check_equivalence(s):
    f , g = s.split('~')
    f = f.strip()
    g = g.strip()
    expr = f"({f}) <=> ({g})"

    return is_tautology(expr)

def check_consequence(s):
    if "⊨" in s:
        left , conclusion = s.split("⊨")
    else:
        left , conclusion = s.split("|=")
    conclusion = conclusion.strip()
    premises = [p.strip() for p in left.split(',') if p.strip()]

    if not premises:
        expr = conclusion
    else:
        p = " and ".join([f"({premise})" for premise in premises])
        expr = f"({p}) => ({conclusion})"

    return is_tautology(expr)

def is_tautology(s):
    ast = parse_expression(s)
    variables = list(get_variables(ast))
    valuations = generate_valuations(variables)

    for val in valuations:
        interpretation = {variables[i]: val[i] for i in range(len(variables))}
        if not evaluate_expression(ast , interpretation):
            return False

    return True

def is_satisfiable(s):
    ast = parse_expression(s)
    variables = list(get_variables(ast))
    valuations = generate_valuations(variables)

    for val in valuations:
        interpretation = {variables[i]: val[i] for i in range(len(variables))}
        if evaluate_expression(ast , interpretation):
            return True

    return False

def is_contradiction(s):
    return not is_satisfiable(s)

if __name__ == "__main__":

    # p1)

    premises = [
        "A and W => P",
        "not A => I",
        "not W => M",
        "not P",
        "E => (not I and not M)",
        "E"
    ]
    clause_set = set()
    for p in premises:
        formula = parse_expression(p)
        cnf = ast_to_string(nf_convertor.to_CNF(formula))
        clause_set.update(resolution.get_clause_set(cnf))
    print("Solution using DP\n")
    resolution.dp_solver(clause_set , print_steps = True)
    print()
    print("Solution using DPLL\n")
    resolution.dpll_solver(clause_set , print_steps = True)
    print()

    # p2)

    p2 = [[
        frozenset({'A' , '!B' , 'C'}),
        frozenset({'B' , 'C'}),
        frozenset({'!A' , 'C'}),
        frozenset({'B' , '!C'}),
        frozenset({'!B'})
    ],
            [
        frozenset({'A' , '!B'}),
        frozenset({'A' , 'C'}),
        frozenset({'!B' , 'C'}),
        frozenset({'!A' , 'B'}),
        frozenset({'B' , '!C'}),
        frozenset({'!A' , '!C'})
    ]]

    for p in p2:
        print("The corresponding formula is: ")
        s = resolution.get_corresponding_formula(p)
        print(s + '\n')
        print("Solution using DP\n")
        resolution.dp_solver(p , print_steps = True)
        print()
        print("Solution using DPLL\n")
        resolution.dpll_solver(p , print_steps = True)
        print()

    # p3)

    p = {
        frozenset({'P' , 'Q' , '!R'}),
        frozenset({'!P' , 'R'}),
        frozenset({'P' , '!Q' , 'S'}),
        frozenset({'!P' , '!Q' , '!R'}),
        frozenset({'P' , '!S'})
    }

    print("Solution using DP\n")
    resolution.dp_solver(p , print_steps = True)
    print()
    print("Solution using DPLL\n")
    resolution.dpll_solver(p , print_steps = True)
    
    # p4)

    p = "not ((((P1 => (P2 or P3)) and (not P1 => (P3 or P4))) and ((P3 => not P6) and (not P3 => (P4 => P1))) and (not (P2 and P5) and (P2 => P5))) => not (P3 => P6))"
    ast = parse_expression(p)
    nnf = nf_convertor.simplify_nnf(nf_convertor.to_nnf(ast))
    formula = ast_to_string(nf_convertor.to_cnf(nnf))
    print(formula)
    clause_set = resolution.get_clause_set(formula)

    print("Solution using DP\n")
    resolution.dp_solver(clause_set , print_steps = True)
    print()
    print("Solution using DPLL\n")
    resolution.dpll_solver(clause_set , print_steps = True)
    
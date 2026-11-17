def remove_implications(node):
    if type(node) is str:
        return node

    op = node[0]
    if op == 'not':
        return ('not' , remove_implications(node[1]))
    elif op in ('and' , 'or'):
        return (op , remove_implications(node[1]) , remove_implications(node[2]))
    elif op == '=>':
        left = remove_implications(node[1])
        right = remove_implications(node[2])
        return ('or' , ('not' , left) , right)
    elif op == '<=>':
        left = remove_implications(node[1])
        right = remove_implications(node[2])
        return ('and' , ('or' , ('not' , left) , right) , ('or' , ('not' , right) , left))

def push_neg(node):
    if type(node) is str:
        return node

    op = node[0]
    if op in ('and' , 'or'):
        return (op , push_neg(node[1]) , push_neg(node[2]))
    elif op == 'not':
        child = node[1]
        
        if type(child) is str:
            if child == '⊤': return '⊥'
            if child == '⊥': return '⊤'
            return node
        
        child_op = child[0]
        if child_op == 'not':
            return push_neg(child[1])
        elif child_op == 'and':
            return ('or' , push_neg(('not' , child[1])) , push_neg(('not' , child[2])))
        elif child_op == 'or':
            return ('and' , push_neg(('not' , child[1])) , push_neg(('not' , child[2])))

def to_nnf(node):
    node = remove_implications(node)
    return push_neg(node)

def get_operands(node , target_op):
    if type(node) is tuple and node[0] == target_op:
        return get_operands(node[1] , target_op) + get_operands(node[2] , target_op)
    return [node]

def build_tree(op , operands):
    if not operands:
        return '⊤' if op == 'and' else '⊥'
    if len(operands) == 1:
        return operands[0]
    return (op , operands[0] , build_tree(op , operands[1:]))

def simplify_nnf(node):
    if type(node) is str:
        return node
    if node[0] == 'not':
        return node

    op = node[0]
    left = simplify_nnf(node[1])
    right = simplify_nnf(node[2])

    operands = get_operands((op , left , right) , op)
    unique_operands = []
    for opnd in operands:
        if opnd not in unique_operands:
            unique_operands.append(opnd)

    for opnd in unique_operands:
        if op == 'and':
            if ('not' , opnd) in unique_operands or (type(opnd) is tuple and opnd[0] == 'not' and opnd[1] in unique_operands) or opnd == '⊥':
                return '⊥'
        elif op == 'or':
            if ('not' , opnd) in unique_operands or (type(opnd) is tuple and opnd[0] == 'not' and opnd[1] in unique_operands) or opnd == '⊤':
                return '⊤'

    if op == 'and':
        unique_operands = [x for x in unique_operands if x != '⊤']
    elif op == 'or':
        unique_operands = [x for x in unique_operands if x != '⊥']

    if len(unique_operands) > 1:
        inner_op = 'and' if op == 'or' else 'or'
        opnd_sets = [set(get_operands(x , inner_op)) for x in unique_operands]
        final_operands = []

        for i , A in enumerate(opnd_sets):
            is_absorbed = False
            for j , B in enumerate(opnd_sets):
                if i != j:
                    if B.issubset(A):
                        if B == A and i < j:
                            continue
                        is_absorbed = True
                        break
            if not is_absorbed:
                final_operands.append(unique_operands[i])

        unique_operands = final_operands

    return build_tree(op , unique_operands)

def distribute_and(A , B):
    if type(A) is tuple and A[0] == 'or':
        left = distribute_and(A[1] , B)
        right = distribute_and(A[2] , B)
        return simplify_nnf(('or' , left , right))
    elif type(B) is tuple and B[0] == 'or':
        left = distribute_and(A , B[1])
        right = distribute_and(A , B[2])
        return simplify_nnf(('or' , left , right))
    else:
        return simplify_nnf(('and' , A , B))

def to_dnf(node):
    if type(node) is str:
        return node
    if node[0] == 'not':
        return node

    op = node[0]

    if op == 'or':
        left = to_dnf(node[1])
        right = to_dnf(node[2])
        return simplify_nnf(('or' , left , right))
    elif op == 'and':
        left = to_dnf(node[1])
        right = to_dnf(node[2])
        return distribute_and(left , right)

def distribute_or(A , B):
    if type(A) is tuple and A[0] == 'and':
        left = distribute_or(A[1] , B)
        right = distribute_or(A[2] , B)
        return simplify_nnf(('and' , left , right))
    elif type(B) is tuple and B[0] == 'and':
        left = distribute_or(A , B[1])
        right = distribute_or(A , B[2])
        return simplify_nnf(('and' , left , right))
    else:
        return simplify_nnf(('or' , A , B))

def to_cnf(node):
    if type(node) is str:
        return node
    if node[0] == 'not':
        return node

    op = node[0]

    if op == 'and':
        left = to_cnf(node[1])
        right = to_cnf(node[2])
        return simplify_nnf(('and' , left , right))
    elif op == 'or':
        left = to_cnf(node[1])
        right = to_cnf(node[2])
        return distribute_or(left , right)
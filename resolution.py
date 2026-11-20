def negate(literal):
    if literal[0] == '!':
        return literal[1:]
    return '!' + literal

def resolve(c1 , c2):
    complements = []
    for lit in c1:
        if negate(lit) in c2:
            complements.append(lit)
    if len(complements) == 1:
        comp = complements[0]
        resolvent = set(c1).union(set(c2))
        resolvent.remove(comp)
        resolvent.remove(negate(comp))
        return frozenset(resolvent)
    return None

def resolution_solver(clause_set , print_steps):
    initial = []
    for clause in set(clause_set):
        if len(clause) == 0:
            if print_steps:
                print("Initial clause set contains the empty set")
                print("UNSATISFIABLE!")
            return False
        if not any(negate(lit) in clause for lit in clause):
            initial.append(clause)
    clauses = initial
    seen_clauses = set(initial)
    step = 1
    start_index = 0

    if print_steps:
        print("Initial clause set K:")
        for i , c in enumerate(clauses):
            print(f"{i + 1}. {set(c)}")
        print()

    while True:
        end_index = len(clauses)
        added_clause = False

        for i in range(end_index):
            start = start_index if i < start_index else i + 1
            for j in range(start , end_index):
                c1 = clauses[i]
                c2 = clauses[j]

                res = resolve(c1 , c2)

                if res is not None and res not in seen_clauses:

                    useless = False
                    for clause in seen_clauses:
                        if clause.issubset(res):
                            useless = True

                    if useless:
                        continue

                    if print_steps:
                        print(f"Step {step}: Resolved {set(c1)} and {set(c2)}")

                    if len(res) == 0:
                        if print_steps:
                            print("New clause: {}")
                            print("Generated the empty set!")
                            print("Result: UNSATISFIABLE")
                        return False

                    if len(res) == 1:
                        lit = list(res)[0]
                        neg_lit = negate(lit)
                        if frozenset({neg_lit}) in seen_clauses:
                            if print_steps:
                                print(f"New clause: {set(res)}")
                                print(f"Step {step + 1}: Resolved {set(res)} and {{'{neg_lit}'}}")
                                print("New clause: {}")
                                print("Generated the empty set!")
                                print("Result: UNSATISFIABLE")
                            return False

                    if print_steps:
                        print(f"New clause: {set(res)}")
                    
                    clauses.append(res)
                    seen_clauses.add(res)
                    step += 1
                    added_clause = True

        if not added_clause:
            if print_steps:
                print("Exhausted all combinations. Result: SATISFIABLE")
            return True
        
        start_index = end_index

def sort_literal(literal):
    if literal[0] == '!':
        base = literal[1:]
        is_neg = 1
    else:
        base = literal
        is_neg = 0

    return (base , is_neg)

def get_corresponding_formula(clause_set):
    clauses = []
    for clause in clause_set:
        literals = sorted(list(clause) , key = sort_literal)
        clauses.append("(" + " ∨ ".join(literals) + ")")
    return " ∧ ".join(clauses)

def get_clause_set(formula):
    if formula == '⊤':
        return set()
    if formula == '⊥':
        return {frozenset()}
    clause_set = set()
    clauses = formula.split(' and ')
    for clause in clauses:
        clean_clause = clause.strip('() ')
        literals = clean_clause.split(' or ')
        clean_literals = {lit.strip() for lit in literals}
        clause_set.add(frozenset(clean_literals))
    return clause_set
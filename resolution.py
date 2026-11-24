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

def eliminate_literal(clauses , lit , print_steps , rule_name , state = None):
    neg_lit = negate(lit)
    new_clauses = set()
    for clause in clauses:
        if lit in clause:
            continue
        elif neg_lit in clause:
            new_clauses.add(clause - {neg_lit})
        else:
            new_clauses.add(clause)

    if print_steps:
        prefix = f"Step {state['step']}: " if state is not None else ""
        print(f"{prefix}Applied {rule_name} on {lit}")
        print()
        print("Updated clause set K':")
        for i , c in enumerate(new_clauses):
            if len(c) == 0:
                print(f"{i + 1}. " + "{}")
            else:
                print(f"{i + 1}. {set(c)}")
        print()

    if state is not None:
        state["step"] += 1

    return new_clauses

def apply_dp_rules(clauses , print_steps , state = None):
    while True:
        if len(clauses) == 0:
            return clauses , True
        if frozenset() in clauses:
            return clauses , False

        unit_lit = None
        for clause in clauses:
            if len(clause) == 1:
                unit_lit = list(clause)[0]
                break
        if unit_lit is not None:
            clauses = eliminate_literal(clauses , unit_lit , print_steps , "The one literal rule" , state)
            continue

        lits = {lit for clause in clauses for lit in clause}
        pure_lit = None
        for lit in lits:
            if negate(lit) not in lits:
                pure_lit = lit
                break
        if pure_lit is not None:
            clauses = eliminate_literal(clauses , pure_lit , print_steps , "The pure literal rule" , state)
            continue

        return clauses , None

def dp_solver(clause_set , print_steps):
    state = {'step': 1}
    clauses = set()
    for clause in clause_set:
        if len(clause) == 0:
            if print_steps:
                print("Initial clause set contains the empty set")
                print("UNSATISFIABLE!")
            return False
        if not any(negate(lit) in clause for lit in clause):
            clauses.add(clause)

    if print_steps:
        print("Initial clause set K:")
        for i , c in enumerate(clauses):
            print(f"{i + 1}. {set(c)}")
        print()

    step = 1
    while True:

        clauses , status = apply_dp_rules(clauses , print_steps , state)

        if status == True:
            if print_steps:
                print("Clause set is empty. Result: SATISFIABLE")
                print(f"Total step count: {state['step'] - 1}")
            return True

        if status == False:
            if print_steps:
                print("Generated the empty set. Result: UNSATISFIABLE")
                print(f"Total step count: {state['step'] - 1}")
            return False

        clause_list = sorted(clauses , key = len)
        resolvent = None

        for i in range(len(clause_list)):
            for j in range(i + 1 , len(clause_list)):
                res = resolve(clause_list[i] , clause_list[j])
                if res is not None and res not in clauses:
                    if any(existing.issubset(res) for existing in clauses):
                        continue

                    resolvent = res
                    if print_steps:
                        print(f"Step {state['step']}: Resolved {set(clause_list[i])} and {set(clause_list[j])}")
                        print(f"New clause: {set(resolvent)}")
                    state["step"] += 1
                    break
            if resolvent is not None:
                break

        if resolvent is None:
            if print_steps:
                print(f"Total step count: {state['step']}")
                print("Exhausted all combinations. Result: SATISFIABLE")
            return True

        if len(resolvent) == 0:
            if print_steps:
                print(f"Total step count: {state['step']}")
                print("Generated the empty set! Result: UNSATISFIABLE")
            return False

        clauses.add(resolvent)

def _dpll(clauses , print_steps , state , depth = 0):

    clauses , status = apply_dp_rules(clauses , print_steps , state)

    if status == True:
        if print_steps:
            print(f"== [Depth {depth}] Satisfied ==")
            print()
        return True
    
    if status == False:
        if print_steps:
            print(f"== [Depth {depth}] Conflict -> Backtracking ==")
            print()
        return False

    smallest_clause = min(clauses , key = len)
    chosen_lit = list(smallest_clause)[0]
    neg_lit = negate(chosen_lit)

    if print_steps:
        print(f"[Depth {depth}] Branch 1: Splitting on {chosen_lit}")
    left_clauses = eliminate_literal(clauses , chosen_lit , print_steps , "split" , state)
    if _dpll(left_clauses , print_steps , state , depth + 1):
        return True
    
    if print_steps:
        print(f"[Depth {depth}] Branch 2: Splitting on {neg_lit}")
    right_clauses = eliminate_literal(clauses , neg_lit , print_steps , "split" , state)
    return _dpll(right_clauses , print_steps , state , depth + 1)

def dpll_solver(clause_set , print_steps):
    state = {"step": 1}
    clauses = set()
    for clause in clause_set:
        if len(clause) == 0:
            if print_steps:
                print("Initial clause set contains the empty set")
                print("UNSATISFIABLE!")
            return False
        if not any(negate(lit) in clause for lit in clause):
            clauses.add(clause)
    
    if print_steps:
        print("Initial clause set K:")
        for i , c in enumerate(clauses):
            print(f"{i + 1}. {set(c)}")
        print()

    result = _dpll(clauses ,  print_steps , state)
    if print_steps:
        print(f"Result is {'SATISFIABLE' if result else 'UNSATISFIABLE'}")
        print(f"Total step count: {state['step'] - 1}")
    return result
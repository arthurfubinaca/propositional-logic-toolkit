def get_initial_groups(variables , truth_values):
    groups = {}
    num_vars = len(variables)
    for i in range(len(truth_values)):
        if truth_values[i]:
            binary_str = format(i , f"0{num_vars}b")
            weight = binary_str.count('1')
            if weight not in groups:
                groups[weight] = set()
            groups[weight].add(binary_str)
    return groups

def merge_strings(s1 , s2):
    count = 0
    merged_s = ""
    for i in range(len(s1)):
        if s1[i] != s2[i]:
            count +=1
            merged_s += "-"
        else:
            merged_s += s1[i]
    if count == 1:
        return merged_s
    else:
        return None

def merge_groups(groups):
    new_groups = {}
    unmerged_strings = set()
    used_strings = set()
    weights = sorted(groups.keys())
    
    for w in weights:
        if (w + 1) in weights:
            for s1 in groups[w]:
                for s2 in groups[w + 1]:
                    merged = merge_strings(s1 , s2)
                    if merged is not None:
                        used_strings.add(s1)
                        used_strings.add(s2)

                        new_weight = merged.count('1')

                        if new_weight not in new_groups:
                            new_groups[new_weight] = set()
                        new_groups[new_weight].add(merged)

    for w in weights:
        for s in groups[w]:
            if s not in used_strings:
                unmerged_strings.add(s)

    return new_groups , unmerged_strings

def get_prime_implicants(variables , truth_values):
    curr_groups = get_initial_groups(variables , truth_values)
    prime_implicants = set()
    while curr_groups:
        new_groups , unmerged = merge_groups(curr_groups)
        prime_implicants.update(unmerged)
        curr_groups = new_groups
    return prime_implicants

def does_implicant_cover(implicant , original):
    for i in range(len(implicant)):
        if implicant[i] != '-' and implicant[i] != original[i]:
            return False
    return True

def get_final_implicants(prime_implicants , variables , truth_values):
    num_vars = len(variables)
    originals = set()
    for i in range(len(truth_values)):    
        if truth_values[i]:
            originals.add(format(i , f"0{num_vars}b"))

    chart = {}
    for o in originals:
        chart[o] = []
        for pi in prime_implicants:
            if does_implicant_cover(pi , o):
                chart[o].append(pi)

    final_implicants = set()
    covered = set()
    for o , pis in chart.items():
        if len(pis) == 1:
            final_implicants.add(pis[0])
    for pi in final_implicants:
        for o in originals:
            if does_implicant_cover(pi , o):
                covered.add(o)

    uncovered = originals - covered
    while uncovered:
        best_pi = None
        max_c = 0
        for pi in prime_implicants:
            if pi not in final_implicants:
                count = sum(1 for u in uncovered if does_implicant_cover(pi , u))
                if count > max_c:
                    max_c = count
                    best_pi = pi
        final_implicants.add(best_pi)
        just_covered = {u for u in uncovered if does_implicant_cover(best_pi , u)}
        uncovered = uncovered - just_covered

    return final_implicants

def format_final_implicants(implicants , variables):
    if not implicants:
        return "False"
    clauses = []
    for pi in implicants:
        terms = []
        for i in range(len(pi)):
            if pi[i] == '1':
                terms.append(variables[i])
            elif pi[i] == '0':
                terms.append(f"¬{variables[i]}")

        if terms:
            clause = " ∧ ".join(terms)
            clauses.append(f"({clause})")

    if not clauses:
        return "True"

    return " ∨ ".join(clauses)

def optimize_logic(variables , truth_values):
    all_pis = get_prime_implicants(variables , truth_values)
    final_pis = get_final_implicants(all_pis , variables , truth_values)
    optimized_formula = format_final_implicants(final_pis , variables)
    return optimized_formula
Core Operators Supported:
NOT: !, not, ¬
AND: and, ∧
OR: or, ∨
IMPLIES: =>, ⇒
EQUIVALENT: <=>, ⇔, ~
CONSTANTS: ⊤ (True), ⊥ (False)

Circuit Generation:
Circuits are designed and generated in Logisim using the minimal propositional formulas produced by this code.

lcs.py (Logic Core System)

tokenize(s) - Converts a string expression into a list of usable tokens.

parse_expression(s) - Converts a list of tokens into an Abstract Syntax Tree (AST) using the Shunting Yard algorithm.

is_valid_expression(s) - Returns a boolean indicating if the string is a well-formed propositional formula.

evaluate_expression(syntax_tree, interpretation) - Computes the True/False result of an AST given a specific dictionary of variable truth values.

tree_print(node) - Pretty-prints the hierarchical structure of the AST in the console.

generate_valuations(variables) - Uses backtracking to generate all 2^n possible True/False combinations for a given number of variables (integer).

get_variables(node) - Extracts and returns a set of all unique propositional variables present in an AST.

generate_interpretations(variables, valuations) - Combines a list of variable names and a list of boolean valuations to generate a list of interpretation dictionaries mapping variables to their truth values.

ast_to_string(node) - Converts an AST back into a readable string format.

get_sub_trees(node) - Recursively collects all sub-expressions (sub-trees) of a given AST.

truth_table(s) - Evaluates a formula and prints a fully formatted truth table, including columns for all sub-expressions.

generate_formula(variables, truth_values) - Generates an unoptimized Sum of Products (Disjunctive Normal Form) string based on an array of truth values.

check_equivalence(s) - Parses a string containing "~" and checks if the left and right formulas are logically equivalent.

check_consequence(s) - Parses a string containing "⊨" or "|=" and checks if the conclusion is a valid logical consequence of the premises.

is_tautology(s) - Checks if a formula is valid (True under all interpretations).

is_satisfiable(s) - Checks if a formula evaluates to True under at least one interpretation.

is_contradiction(s) - Checks if a formula evaluates to False under all interpretations.

optimizer.py (Quine-McCluskey Optimizer)

get_initial_groups(variables, truth_values) - Groups the binary representation of true outcomes by their weight (number of 1s).

merge_strings(s1, s2) - Compares two binary strings and replaces differing bits with a dash ("-") if they differ by exactly one position.

merge_groups(groups) - Compares adjacent weight groups to find all valid string merges.

get_prime_implicants(variables, truth_values) - Repeatedly merges groups to find all prime implicants using the Quine-McCluskey algorithm.

does_implicant_cover(implicant, original) - Helper function to check if an implicant string covers a specific original binary minterm.

get_final_implicants(prime_implicants, variables, truth_values) - Resolves the prime implicant chart to find the minimal essential cover.

format_final_implicants(implicants, variables) - Converts the final optimized list of binary strings back into a readable logic formula.

optimize_logic(variables, truth_values) - The main wrapper function that orchestrates the Quine-McCluskey algorithm and returns the final minimized logic string.

nf_convertor.py (Normal Form Converter)

remove_implications(node) - Replaces implications (=>) and equivalences (<=>) in an AST with equivalent AND/OR/NOT logic.

push_neg(node) - Pushes negations inward using De Morgan's laws and eliminates double negations.

to_nnf(node) - Converts an AST into Negation Normal Form (NNF).

get_operands(node, target_op) - Flattens nested trees of the same operator type.

build_tree(op, operands) - Reconstructs a binary AST from a list of operands.

simplify_nnf(node) - Simplifies an NNF AST by applying absorption laws, eliminating redundant variables, and handling truth constants.

distribute_and(A, B) - Distributes the AND operator over OR operators for DNF conversion.

to_DNF(node) - Wrapper function that converts any raw AST into NNF, simplifies it, and transforms it into Disjunctive Normal Form (DNF).

to_dnf(node) - Recursively converts an NNF AST into simplified Disjunctive Normal Form (DNF).

distribute_or(A, B) - Distributes the OR operator over AND operators for CNF conversion.

to_CNF(node) - Wrapper function that converts any raw AST into NNF, simplifies it, and transforms it into Conjunctive Normal Form (CNF).

to_cnf(node) - Recursively converts an NNF AST into simplified Conjunctive Normal Form (CNF).

resolution.py (Resolution Theorem Prover)

negate(literal) - Returns the negated form of a literal string.

resolve(c1, c2) - Resolves two clauses if they contain exactly one pair of complementary literals.

resolution_solver(clause_set, print_steps) - Checks a set of clauses for satisfiability using the propositional resolution method. Includes optimizations for subsumption and unit clauses.

sort_literal(literal) - Sorting key used to alphabetize literals by their base variable name.

get_corresponding_formula(clause_set) - Converts a list of frozenset clauses back into a standard CNF formula string.

get_clause_set(formula) - Parses a CNF formula string into a set of frozenset clauses, handling top-level truth constants (⊤ and ⊥).

eliminate_literal(clauses, lit, print_steps, rule_name, state=None) - Removes clauses satisfied by a literal and deletes its complement from the remaining clauses, updating the step trace.

apply_dp_rules(clauses, print_steps, state=None) - Repeatedly applies the one-literal rule (unit propagation) and the pure literal rule until neither is applicable or a terminal state is reached.

dp_solver(clause_set, print_steps) - Checks a set of clauses for satisfiability using the Davis-Putnam (DP) algorithm, combining unit propagation and pure literal elimination with resolution.

_dpll(clauses, print_steps, state, depth=0) - Recursive helper function that performs branching (splitting) on literals and backtracking for the DPLL algorithm.

dpll_solver(clause_set, print_steps) - Checks a set of clauses for satisfiability using the Davis-Putnam-Logemann-Loveland (DPLL) algorithm.
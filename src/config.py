# Number of test repeats when solving
TEST_REPEATS = 1

# List of different encodings to test
TEST_VERSIONS = [0, 1, 2, 3]

# File to use for SAT test
SAT_TEST_SEQ = "input/length-23-7"

# List of the solvers used
SOLVERS = ["cadical", "cryptominisat", "glucose", "kissat", "maplesat"]

# List of different search policies
POLICIES = ["binary_search_policy", "linear_search_policy", "double_binary_policy", "double_linear_policy"]

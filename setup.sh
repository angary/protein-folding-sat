echo "Making models and results directory"
mkdir -p models/{bul,cnf}
mkdir -p results/{encoding,policy,search}

# TODO: Possibly add installation script
echo "Checking SAT solvers"
declare -a solvers=("glucose" "kissat" "minisat")
passed=0
for i in "${solvers[@]}"
do
    if ! command -v ${i} &> /dev/null
    then
        echo "WARNING: ${i} could not be found"
        passed=1
    fi
done

if [ $passed -eq 0 ];
then 
    echo "All solvers installed"
fi

# TODO: Possibly add initialisation of input directory
echo "Making input directory"
mkdir input

echo "Done"

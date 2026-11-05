def generate_fibonacci(n):
    """Generate a list containing the first n Fibonacci numbers."""
    if n <= 0:
        return []
    elif n == 1:
        return [0]

    fib_sequence = [0, 1]
    while len(fib_sequence) < n:
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence


filename = "fibonacci.txt"

# 1. Generate the first 20 Fibonacci numbers
#fib_numbers = generate_fibonacci(20)
fib_numbers = generate_fibonacci(3)

# 2. Save the numbers to fibonacci.txt (one per line)
with open(filename, "w") as file:
    for num in fib_numbers:
        file.write(f"{num}\n")

print(f"Successfully saved {len(fib_numbers)} numbers to '{filename}'.\n")

# 3. Read the file and print its contents
print(f"Contents of '{filename}':")
with open(filename, "r") as file:
    contents = file.read()
    print(contents)
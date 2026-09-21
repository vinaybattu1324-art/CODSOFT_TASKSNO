def get_number(prompt):
    """Ask for a number, re-prompting until valid input is given."""
    while True:
        raw = input(prompt).strip()
        try:
            return float(raw)
        except ValueError:
            print("Please enter a valid number (e.g. 3, -4.5, 10).")

def get_operation():
    """Show a menu of operations and return the chosen operator symbol."""
    operations = {
        "1": ("+", "Addition"),
        "2": ("-", "Subtraction"),
        "3": ("*", "Multiplication"),
        "4": ("/", "Division"),
        "5": ("%", "Modulus (remainder)"),
        "6": ("**", "Exponent (power)"),
    }
    print("\nChoose an operation:")
    for key, (symbol, name) in operations.items():
        print(f"  {key}. {name} ({symbol})")

    while True:
        choice = input("Enter choice (1-6): ").strip()
        if choice in operations:
            return operations[choice][0]
        print("Please enter a number from 1 to 6.")

def calculate(a, b, op):
    """Perform the calculation for the given operator, raising on divide-by-zero."""
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        return a / b
    if op == "%":
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        return a % b
    if op == "**":
        return a ** b
    raise ValueError(f"Unknown operation: {op}")

def format_number(n):
    """Show whole-number results without a trailing '.0'."""
    if n == int(n):
        return str(int(n))
    return str(n)

def main():
    print("=== Simple Calculator ===")

    while True:
        a = get_number("\nEnter the first number: ")
        b = get_number("Enter the second number: ")
        op = get_operation()

        try:
            result = calculate(a, b, op)
        except ZeroDivisionError as e:
            print(f"\nError: {e}")
        else:
            print(
                f"\nResult: {format_number(a)} {op} {format_number(b)} "
                f"= {format_number(result)}"
            )

        again = input("\nCalculate again? [y/N]: ").strip().lower()
        if again not in ("y", "yes"):
            print("Goodbye!")
            break
if __name__ == "__main__":
    main()
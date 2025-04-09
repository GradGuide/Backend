def NUMBER(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def PRIME(start, end):
    primes = [num for num in range(start, end + 1) if NUMBER(num)]
    return primes

start = int(input("Enter the first number in the range: "))
end = int(input("Enter the last number in the range: "))

print("Prime numbers in the specified range:", PRIME(start, end))

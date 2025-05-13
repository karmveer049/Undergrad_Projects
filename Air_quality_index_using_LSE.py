def load_data(file_path):
    X, Y = [], []
    with open(file_path, 'r') as f:
        next(f)  # Skip header
        for line in f:
            parts = line.strip().split(',')
            if len(parts) != 6:
                continue
            try:
                features = list(map(float, parts[:5]))
                target = float(parts[5])
            except ValueError:
                continue
            X.append([1.0] + features)
            Y.append(target)
    return X, Y

def matrix_transpose(A):
    return [list(row) for row in zip(*A)]

def matrix_multiply(A, B):
    return [[sum(a * b for a, b in zip(row, col)) for col in zip(*B)] for row in A]

def identity_matrix(n):
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

def matrix_inverse(A):
    n = len(A)
    AM = [row[:] for row in A]
    IM = identity_matrix(n)
    
    for fd in range(n):
        if AM[fd][fd] == 0.0:
            for i in range(fd + 1, n):
                if AM[i][fd] != 0.0:
                    AM[fd], AM[i] = AM[i], AM[fd]
                    IM[fd], IM[i] = IM[i], IM[fd]
                    break
            else:
                raise ValueError("Matrix is singular and cannot be inverted.")
        
        pivot = AM[fd][fd]
        AM[fd] = [x / pivot for x in AM[fd]]
        IM[fd] = [x / pivot for x in IM[fd]]

        for i in range(n):
            if i != fd:
                factor = AM[i][fd]
                AM[i] = [a - factor * b for a, b in zip(AM[i], AM[fd])]
                IM[i] = [a - factor * b for a, b in zip(IM[i], IM[fd])]
    return IM

def compute_beta(X, Y):
    Xt = matrix_transpose(X)
    XtX_inv = matrix_inverse(matrix_multiply(Xt, X))
    XtY = matrix_multiply(Xt, [[y] for y in Y])
    beta = matrix_multiply(XtX_inv, XtY)
    return [b[0] for b in beta]

def predict(features, beta):
    return sum(f * b for f, b in zip([1.0] + features, beta))

def get_user_input():
    def get_valid_input(prompt, min_val, max_val):
        while True:
            try:
                val = float(input(f"Enter {prompt} [{min_val} - {max_val}]: "))
                if min_val <= val <= max_val:
                    return val
                else:
                    print(f"Value must be between {min_val} and {max_val}.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    return [
        get_valid_input("PM2.5 (µg/m³)", 0, 600),
        get_valid_input("PM10 (µg/m³)", 0, 700),
        get_valid_input("NO2 (ppb)", 0, 250),
        get_valid_input("SO2 (ppb)", 0, 200),
        get_valid_input("CO (ppm)", 0.0, 50.0)
    ]

def classify_aqi(aqi):
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Satisfactory"
    elif aqi <= 200:
        return "Moderate"
    elif aqi <= 300:
        return "Poor"
    elif aqi <= 400:
        return "Very Poor"
    else:
        return "Severe"

if __name__ == '__main__':
    file_path = r"C:\Users\karam\OneDrive\Desktop\Neural Project\aqi_dataset.csv"
    X, Y = load_data(file_path)
    beta = compute_beta(X, Y)

    print("Computed beta coefficients:")
    for i, coeff in enumerate(beta):
        print(f"Beta[{i}]: {coeff:.4f}")

    features = get_user_input()
    aqi = predict(features, beta)
    condition = classify_aqi(aqi)

    print(f"\nPredicted Air Quality Index (AQI): {aqi:.2f}")
    print(f"Air Quality Condition: {condition}")

def load_data(file_path):
    X = []
    Y = []

    with open(file_path, 'r') as f:
        lines = f.readlines()

    for line in lines[1:]:
        line = line.strip()
        if line == "":
            continue
        parts = line.split(',')
        try:
            area = float(parts[0])
            bedrooms = float(parts[1])
            crime_rate = float(parts[2])
            distance = float(parts[3])
            age = float(parts[4])
            price = float(parts[5])
        except ValueError:
            continue

        row = [1.0, area, bedrooms, crime_rate, distance, age]
        X.append(row)
        Y.append(price)

    return X, Y

def matrix_transpose(A):
    rows = len(A)
    cols = len(A[0])
    T = []
    for j in range(cols):
        new_row = []
        for i in range(rows):
            new_row.append(A[i][j])
        T.append(new_row)
    return T

def matrix_multiply(A, B):
    m = len(A)
    n = len(A[0])
    p = len(B[0])
    result = [[0 for _ in range(p)] for _ in range(m)]
    for i in range(m):
        for j in range(p):
            for k in range(n):
                result[i][j] += A[i][k] * B[k][j]
    return result

def identity_matrix(n):
    I = []
    for i in range(n):
        row = [0] * n
        row[i] = 1
        I.append(row)
    return I

def matrix_inverse(A):
    n = len(A)
    AM = [row[:] for row in A]
    IM = identity_matrix(n)

    for fd in range(n):
        if AM[fd][fd] == 0:
            for i in range(fd+1, n):
                if AM[i][fd] != 0:
                    AM[fd], AM[i] = AM[i], AM[fd]
                    IM[fd], IM[i] = IM[i], IM[fd]
                    break
            else:
                raise ValueError("Matrix is singular and cannot be inverted.")

        pivot = AM[fd][fd]
        for j in range(n):
            AM[fd][j] /= pivot
            IM[fd][j] /= pivot

        for i in range(n):
            if i != fd:
                factor = AM[i][fd]
                for j in range(n):
                    AM[i][j] -= factor * AM[fd][j]
                    IM[i][j] -= factor * IM[fd][j]

    return IM

def vector_to_column_matrix(v):
    return [[x] for x in v]

def compute_beta(X, Y):
    X_transpose = matrix_transpose(X)
    XtX = matrix_multiply(X_transpose, X)
    XtX_inv = matrix_inverse(XtX)
    Y_column = vector_to_column_matrix(Y)
    XtY = matrix_multiply(X_transpose, Y_column)
    beta_matrix = matrix_multiply(XtX_inv, XtY)
    beta = [row[0] for row in beta_matrix]
    return beta

if __name__ == '__main__':
    file_path = r"C:\Users\karam\OneDrive\Desktop\Neural Project\house_price_data_inr.csv"
    X, Y = load_data(file_path)
    beta = compute_beta(X, Y)
    print("Computed beta coefficients:")
    for i, coeff in enumerate(beta):
        print("Beta[{}]: {}".format(i, coeff))

def predict(features, beta):
    features = [1.0] + features
    predicted_price = sum(features[i] * beta[i] for i in range(len(beta)))
    return predicted_price

def get_user_input():
    print("\nEnter House Features:")
    area = float(input("Enter Area (sq ft): "))
    bedrooms = int(input("Enter Number of Bedrooms: "))
    crime_rate = float(input("Enter Crime Rate (0 to 10 scale): "))
    distance = float(input("Enter Distance from City (km): "))
    age = float(input("Enter Age of House (years): "))
    return [area, bedrooms, crime_rate, distance, age]

userFeature = get_user_input()
predicted_price = predict(userFeature, beta)
print(f"Predicted House Price: ₹{predicted_price:.2f}")

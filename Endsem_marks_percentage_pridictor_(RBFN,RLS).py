def read_csv_data(file_path):
    """Reads CSV data and constructs input matrix X and output vector Y with transformations."""
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Skip the header row and process only numerical data
    data = [list(map(float, line.strip().split(','))) for line in lines[1:]]
    e=2.71828
    c1,c2,c3,c4,c5=2,3,4,5,6
    sigma=100
    X = [[e**(-((row[0])-c1)**2/(2*sigma**2)), e**(-((row[1])-c2)**2/(2*sigma**2)),e**(-((row[2])-c3)**2/(2*sigma**2)),e**(-((row[3])-c4)**2/(2*sigma**2)),e**(-((row[4])-c5)**2/(2*sigma**2))]for row in data]  # Apply transformations
    Y = [row[-1] for row in data]  # Extract output values
    return X, Y


def matrix_transpose(matrix):
    """Returns the transpose of a given matrix."""
    return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]


def matrix_multiply(A, B):
    """Performs matrix multiplication A * B."""
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


def matrix_inverse(matrix):
    """Computes the inverse of a square matrix using Gauss-Jordan elimination."""
    n = len(matrix)
    identity = [[1 if i == j else 0 for j in range(n)] for i in range(n)]

    for i in range(n):
        factor = matrix[i][i]
        for j in range(n):
            matrix[i][j] /= factor
            identity[i][j] /= factor
        for k in range(n):
            if k != i:
                factor = matrix[k][i]
                for j in range(n):
                    matrix[k][j] -= factor * matrix[i][j]
                    identity[k][j] -= factor * identity[i][j]
    return identity


def scalar_matrix_multiply(scalar, matrix):
    """Multiplies a matrix by a scalar."""
    return [[scalar * elem for elem in row] for row in matrix]


def kalman_update(X, Y):
    """Applies recursive least squares using the Kalman filter approach."""
    num_features = len(X[0])
    W = [[0] for _ in range(num_features)]  # Initial weight matrix
    P = [[1000 if i == j else 0 for j in range(num_features)] for i in range(num_features)]  # Initial inverse covariance matrix

    for i in range(len(X)):
        x_i = [[X[i][j]] for j in range(num_features)]  # Convert row to column matrix
        y_i = Y[i]

        xT = matrix_transpose(x_i)
        P_x = matrix_multiply(P, x_i)
        xT_P_x = matrix_multiply(xT, P_x)
        xT_P_x_inv = matrix_inverse([[xT_P_x[0][0] + 1]])
        K = matrix_multiply(P_x, xT_P_x_inv)

        error = y_i - sum(matrix_multiply(xT, W)[0])
        W_update = scalar_matrix_multiply(error, K)
        W = [[W[j][0] + W_update[j][0]] for j in range(num_features)]

        K_xT = matrix_multiply(K, xT)
        P_update = matrix_multiply(K_xT, P)
        P = [[P[i][j] - P_update[i][j] for j in range(num_features)] for i in range(num_features)]

    return W

def performance(W):
    """Takes user input and predicts house price using trained weights."""
    Attendance = float(input("Attendance (%): "))
    MidSemMarks = float(input("MidSemMarks (%): "))
    IQLevel = float(input("IQLevel (70-160): "))
    SelfStudy = float(input("SelfStudy (0-24 hrs): "))
    Attentiveness = float(input("Attentiveness (%): "))
    e=2.71828
    c1,c2,c3,c4,c5=2,3,4,5,6
    sigma=100
    X_input=[
       e**(-(( Attendance)-c1)**2/(2*sigma**2)), e**(-((MidSemMarks)-c2)**2/(2*sigma**2)),
       e**(-((IQLevel)-c3)**2/(2*sigma**2)),e**(-((SelfStudy)-c4)**2/(2*sigma**2)),e**(-((Attentiveness)-c5)**2/(2*sigma**2)) 
    ]

    performance = sum(W[i][0] * X_input[i] for i in range(len(W)))
    print("End Sem marks(%):", performance)


# Example usage
file_path = "C:\\Users\\karam\\OneDrive\\Desktop\\Neural Project\\student_performance_dataset_2000_updated.csv"
X, Y = read_csv_data(file_path)
W_final = kalman_update(X, Y)
print("Final Weights:", W_final)


performance(W_final)

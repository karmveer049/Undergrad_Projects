# Step 1: Get user input
speed_input = float(input("Enter the speed of the car (0-100 km/hr): "))
distance_input = float(input("Enter the distance between cars (0-100 m): "))

# Step 2: Membership functions
def triangular_membership(x, a, b, c):
    if x <= a or x >= c:
        return 0
    elif a < x < b:
        return (x - a) / (b - a)
    elif b <= x < c:
        return (c - x) / (c - b)
    elif x == b:
        return 1
    return 0

# Fuzzy sets
def fuzzify_speed(speed):
    return {
        "slow": triangular_membership(speed, 0, 0, 30),
        "medium": triangular_membership(speed, 20, 40, 60),
        "fast": max(triangular_membership(speed, 50, 80, 101), triangular_membership(speed, 80, 100, 100))
    }

def fuzzify_distance(distance):
    return {
        "close": triangular_membership(distance, 0, 0, 30),
        "average": triangular_membership(distance, 20, 40, 60),
        "far": max(triangular_membership(distance, 50, 80, 101), triangular_membership(distance, 80, 100, 100))
    }

def brake_membership_graph():
    # returns triangular graph for brake
    return {
        "low": [0, 0, 30],
        "moderate": [20, 40, 60],
        "strong": [50, 80, 100]
    }

# Step 3: Rule base
rules = {
    ("close", "slow"): "moderate",
    ("close", "medium"): "moderate",
    ("close", "fast"): "strong",
    ("average", "slow"): "low",
    ("average", "medium"): "moderate",
    ("average", "fast"): "strong",
    ("far", "slow"): "low",
    ("far", "medium"): "low",
    ("far", "fast"): "moderate"
}

# Step 4: Get degrees of membership
speed_membership = fuzzify_speed(speed_input)
distance_membership = fuzzify_distance(distance_input)

# Step 5: Apply rules
activated_rules = []

for dist_label, dist_value in distance_membership.items():
    for speed_label, speed_value in speed_membership.items():
        activation = min(dist_value, speed_value)
        if activation > 0:
            brake_level = rules[(dist_label, speed_label)]
            activated_rules.append((brake_level, activation))

# Step 6: Clip brake membership functions
def get_clipped_brake_graph(level, degree):
    a, b, c = brake_membership_graph()[level]
    points = []
    step = 1
    for x in range(a, c + 1, step):
        y = triangular_membership(x, a, b, c)
        clipped_y = min(y, degree)
        points.append((x, clipped_y))
    return points

# Step 7: Aggregate all clipped graphs (take max at each x)
aggregated = [0] * 101  # x from 0 to 100
for brake_level, degree in activated_rules:
    clipped = get_clipped_brake_graph(brake_level, degree)
    for x, y in clipped:
        aggregated[x] = max(aggregated[x], y)

# Step 8: Defuzzify using Center of Gravity
def center_of_gravity(aggregated):
    num = 0
    denom = 0
    for x in range(len(aggregated)):
        y = aggregated[x]
        num += x * y
        denom += y
    if denom == 0:
        return 0
    return num / denom

brake_percent = center_of_gravity(aggregated)

print(f"\nBrake to be applied: {brake_percent:.2f}%")

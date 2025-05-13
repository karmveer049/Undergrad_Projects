clc;
clear;

%--- USER INPUT ---
speed = input('Enter the speed of the car (0-100 km/hr): ');
distance = input('Enter the distance to the car in front (0-100 m): ');

%--- FUZZIFICATION ---
% Speed fuzzy sets
speed_slow = trimf(speed, 0, 0, 40);
speed_medium = trimf(speed, 30, 50, 70);
speed_fast = trimf(speed, 60, 100, 100);

% Distance fuzzy sets
distance_close = trimf(distance, 0, 0, 40);
distance_moderate = trimf(distance, 30, 50, 70);
distance_far = trimf(distance, 60, 100, 100);

%--- RULE BASE & INFERENCE ---
% Rule 1: IF speed is Fast AND distance is Close → Brake Hard
rule1 = min(speed_fast, distance_close);

% Rule 2: IF speed is Slow AND distance is Far → Brake Soft
rule2 = min(speed_slow, distance_far);

% Rule 3: IF speed is Medium AND distance is Moderate → Brake Moderate
rule3 = min(speed_medium, distance_moderate);

% Rule 4: IF speed is Fast AND distance is Moderate → Brake Hard
rule4 = min(speed_fast, distance_moderate);

% Rule 5: IF speed is Medium AND distance is Close → Brake Hard
rule5 = min(speed_medium, distance_close);

% Rule 6: IF speed is Slow AND distance is Moderate → Brake Moderate
rule6 = min(speed_slow, distance_moderate);

% Rule 7: IF speed is Medium AND distance is Far → Brake Soft
rule7 = min(speed_medium, distance_far);

% Combine rules
brake_soft = max([rule2, rule7]);
brake_moderate = max([rule3, rule6]);
brake_hard = max([rule1, rule4, rule5]);

%--- OUTPUT MEMBERSHIP FUNCTIONS (Brake) ---
x = 0:1:100;  % Brake range in percentage

% Define the output membership functions
soft_mf = arrayfun(@(val) trimf(val, 0, 0, 40), x);
moderate_mf = arrayfun(@(val) trimf(val, 30, 50, 70), x);
hard_mf = arrayfun(@(val) trimf(val, 60, 100, 100), x);

% Activated output membership function
brake_mf = max([
    brake_soft * soft_mf;
    brake_moderate * moderate_mf;
    brake_hard * hard_mf
], [], 1);

%--- DEFUZZIFICATION USING CENTER OF GRAVITY ---
numerator = sum(x .* brake_mf);
denominator = sum(brake_mf);

if denominator == 0
    brake_output = 0;  % Avoid division by zero
else
    brake_output = numerator / denominator;
end

fprintf('\n==== Results ====\n');
fprintf('Fuzzy Brake Output: %.2f%%\n', brake_output);

%--- EXPORT RESULTS TO CSV FILE ---
% Create results table
results = table(speed, distance, ...
    speed_slow, speed_medium, speed_fast, ...
    distance_close, distance_moderate, distance_far, ...
    brake_soft, brake_moderate, brake_hard, ...
    brake_output);

% Save to CSV file
writetable(results, 'fuzzy_brake_output.csv');
fprintf('\nResults exported to fuzzy_brake_output.csv\n');

%--- VISUALIZATION ---

% Plot SPEED membership functions
figure;
subplot(3,1,1);
xx = 0:1:100;
plot(xx, arrayfun(@(x) trimf(x, 0, 0, 40), xx), 'b', 'LineWidth', 2); hold on;
plot(xx, arrayfun(@(x) trimf(x, 30, 50, 70), xx), 'g', 'LineWidth', 2);
plot(xx, arrayfun(@(x) trimf(x, 60, 100, 100), xx), 'r', 'LineWidth', 2);
title('Speed Membership Functions');
xlabel('Speed (km/h)');
ylabel('Degree');
legend('Slow','Medium','Fast');
grid on;

% Plot DISTANCE membership functions
subplot(3,1,2);
plot(xx, arrayfun(@(x) trimf(x, 0, 0, 40), xx), 'b', 'LineWidth', 2); hold on;
plot(xx, arrayfun(@(x) trimf(x, 30, 50, 70), xx), 'g', 'LineWidth', 2);
plot(xx, arrayfun(@(x) trimf(x, 60, 100, 100), xx), 'r', 'LineWidth', 2);
title('Distance Membership Functions');
xlabel('Distance (m)');
ylabel('Degree');
legend('Close','Moderate','Far');
grid on;

% Plot BRAKE membership functions (final)
subplot(3,1,3);
plot(x, brake_mf, 'm', 'LineWidth', 2);
title('Fuzzy Brake Output (Aggregated)');
xlabel('Brake (%)');
ylabel('Membership Degree');
grid on;

%--- SIMULATION: VARYING SPEED ---
sim_speed = 0:5:100;  % Varying speed from 0 to 100 km/h
sim_brake = zeros(size(sim_speed));

for i = 1:length(sim_speed)
    spd = sim_speed(i);
    
    % Fuzzify speed
    spd_slow = trimf(spd, 0, 0, 40);
    spd_medium = trimf(spd, 30, 50, 70);
    spd_fast = trimf(spd, 60, 100, 100);
    
    % Distance already fuzzified
    dst_close = trimf(distance, 0, 0, 40);
    dst_mod = trimf(distance, 30, 50, 70);
    dst_far = trimf(distance, 60, 100, 100);

    % Rules
    r1 = min(spd_fast, dst_close);
    r2 = min(spd_slow, dst_far);
    r3 = min(spd_medium, dst_mod);
    r4 = min(spd_fast, dst_mod);
    r5 = min(spd_medium, dst_close);
    r6 = min(spd_slow, dst_mod);
    r7 = min(spd_medium, dst_far);

    bs = max([r2, r7]);
    bm = max([r3, r6]);
    bh = max([r1, r4, r5]);

    % Memberships
    s_mf = arrayfun(@(val) trimf(val, 0, 0, 40), x);
    m_mf = arrayfun(@(val) trimf(val, 30, 50, 70), x);
    h_mf = arrayfun(@(val) trimf(val, 60, 100, 100), x);

    brake_mf_sim = max([
        bs * s_mf;
        bm * m_mf;
        bh * h_mf
    ], [], 1);

    num = sum(x .* brake_mf_sim);
    denom = sum(brake_mf_sim);
   if denom == 0
    sim_brake(i) = 0;
else
    sim_brake(i) = num / denom;
end

end

% Plot simulation
figure;
plot(sim_speed, sim_brake, 'b-o', 'LineWidth', 2);
title('Simulated Brake Output vs Speed (Distance = 30m)');
xlabel('Speed (km/h)');
ylabel('Brake Output (%)');
grid on;

%--- TRIMF FUNCTION DEFINITION ---
function mu = trimf(x, a, b, c)
    if x <= a
        mu = 0;
    elseif x <= b
        mu = (x - a) / (b - a);
    elseif x <= c
        mu = (c - x) / (c - b);
    else
        mu = 0;
    end
end

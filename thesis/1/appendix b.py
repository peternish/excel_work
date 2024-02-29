import numpy as np

# Define the initial variables
wd = "/path/to/your/directory"
F = np.genfromtxt(f"{wd}/F.csv", delimiter=',', dtype=float)
G = np.genfromtxt(f"{wd}/G.csv", delimiter=',', dtype=float)
K = np.genfromtxt(f"{wd}/K.csv", delimiter=',', dtype=float)

T = F * G * K

mu0 = 4 * np.pi * 1E-7

# Tape parameters
t0 = 0.0001
w0 = 0.012
insu = 2.5 * 1E-6
t = t0 + 2 * insu
w = w0 + 2 * insu

# Safety factor, fill factor, and efficiency
s = 0.8
f = 0.75
eta = 0.9

# Critical curve parameters
a1, b1, c1 = 275.76, 1555.825, -0.32
a2, b2, c2 = 143.32, 920.9, -0.162

# Shape factors alpha and beta
alpha_vector = np.array([1.08, 1.1, 1.2, 1.3, 1.4, 1.6, 2.1, 2.6, 3.1])
beta_vector = np.array([0.25, 0.5, 0.75, 1, 1.5, 2, 2.5, 3])

# Constraints
B_min = 2
B_step = 0.01
r_min, r_max, r_step = 0.01, 1, 0.01
stress_max = 550

# Define the functions
def critical_current(B):
    if B <= 8:
        return round(a1 + b1 * np.exp(c1 * B), 2)
    elif 8 < B <= 16:
        return round(a2 + b2 * np.exp(c2 * B), 2)
    else:
        print("The magnetic field density is too large!")

def critical_field(I):
    if 396 <= I < 1100:
        return round(np.log((I - a1) / b1) / c1, 2)
    elif 143 <= I < 396:
        return round(np.log((I - a2) / b2) / c2, 2)
    elif I < 143:
        print("The current is too low!")
    else:
        print("The current is too high!")

def load_line_current(B, fgk, ri):
    return (t * w) / (s * f) * (B / (fgk * ri))

def working_point(B, fgk, ri):
    return critical_current(B) - load_line_current(B, fgk, ri)

def stress(a1, B, k, fgk):
    return round(B**2 / (fgk * k) * 1 / (a1 - 1) * ((2 * a1 * (7 * a1**2 + a1 + 1)) / (9 * (a1 + 1)) - (5 * a1**2 + 1) / 6) / 1E6, 2)

def tape_length(alpha, beta, ri):
    return (2 * np.pi * f * (alpha**2 - 1) * beta * ri**3) / (t * w)

def Kn(alpha, beta):
    return ((alpha + 1)**2) / (1 + (0.9 * (alpha + 1) / (4 * beta)) + (0.64 * (alpha - 1) / (alpha + 1)) + (0.84 * (alpha - 1) / (2 * beta)))

def turns(alpha, beta, ri):
    N = (2 * beta * (alpha - 1) * ri**2 * f / (t * w))
    return int(N)

def inductance(alpha, beta, ri):
    return Kn(alpha, beta) * (turns(alpha, beta, ri)**2) * (np.pi**2) * ri / (2 * beta) * 1E-7

def energy_stored(alpha, beta, B, fgk, ri):
    return 0.5 * inductance(alpha, beta, ri) * (load_line_current(B, fgk, ri)**2)

# Main algorithm
def coil_configuration(Energy, Power, Voltage):
    l_max = 1E6  # Upper bound for tape length (in meters)
    E_target = Energy / eta  # Target energy stored
    I_min = Power / Voltage  # Minimum required current
    I_op_min = I_min / np.sqrt(1 - eta)  # Minimum required peak operating current to achieve efficiency
    I_crit = I_op_min / s  # Minimum critical current required, considering stress factor
    B_crit = critical_field(I_crit)  # Critical field

    for i in range(len(alpha_vector)):
        for j in range(len(beta_vector)):
            for ri in np.arange(r_min, r_max + r_step, r_step):
                for B in np.arange(B_min, B_crit, B_step):
                    L = inductance(alpha_vector[i], beta_vector[j], ri)
                    I_op = load_line_current(s * B, T[i, j], ri)
                    E_stored = energy_stored(alpha_vector[i], beta_vector[j], B, T[i, j], ri)
                    stress_cfg = stress(alpha_vector[i], B * s, K[i, j], T[i, j])
                    length_cfg = tape_length(alpha_vector[i], beta_vector[j], ri)

                    if (working_point(B, T[i, j], ri) > 0 and
                        E_stored >= E_target and
                        stress_cfg < stress_max * s and
                        l_max > length_cfg and
                        I_op / s > I_crit):

                            l_max = length_cfg
                            e_mem = E_stored
                            L_mem = L
                            stress_mem = stress_cfg
                            alpha_mem = alpha_vector[i]
                            beta_mem = beta_vector[j]
                            r_mem = ri
                            i_mem = i
                            j_mem = j
                            B_mem = B
                            I_mem = load_line_current(B, T[i, j], ri)
                            I_op_mem = I_op
                            I_crit_mem = I_crit

    print("Magnetic Field (T):", B_mem)
    print("Tape Length (m):", l_max)
    print("Inner Radius (m):", r_mem)
    print("Alpha value:", alpha_mem)
    print("Beta value:", beta_mem)
    print("Inductance (H):", L_mem)
    print("Stored Energy (kJ):", e_mem / 1000)
    print("Load Line current Current (A):", I_mem)
    print("Operating Current (A):", I_op_mem)
    print("Minimum Critical curve Current (A):", I_crit_mem)

# Call the function

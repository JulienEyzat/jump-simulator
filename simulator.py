import scipy.integrate
import numpy as np

# x''(t) = -(alpha/m)*(x')**2 - (alpha/m)*wind**2
def dU_dt(t, U, alphax, m, windx_dir, windx):
    # Here U is a vector such that y=U[0] and z=U[1]. This function should return [y', z']
    return [U[1], -(alphax/m)*(U[1]**2-windx_dir*windx**2)]

# y''(t) = -(alpha/m)*(y')**2 - (alpha/m)*wind**2 - g
def dV_dt(t, V, alphay, m, windy_dir, windy, g):
    return [V[1], (alphay/m)*(V[1]**2+windy_dir*windy**2)-g]

def dU_dt_no_air(t, U):
    return [U[1], 0]

def dV_dt_no_air(t, V, g):
    return [V[1], -g]

def get_xs(ts, constants, is_air):
    if is_air:
        func = dU_dt
        args = (constants["alphax"], constants["m"], constants["windx_dir"], constants["windx"])
    else:
        func = dU_dt_no_air
        args = None
    Us = scipy.integrate.solve_ivp(
        func, 
        t_span=(constants["t0"], constants["tend"]), 
        y0=(constants["x0"], constants["vx0"]), 
        method="RK45", 
        args=args, 
        dense_output=True
    )
    xs = Us.sol(ts)[0]
    return xs

def get_ys(ts, constants, is_air):
    if is_air:
        func = dV_dt
        args = (constants["alphay"], constants["m"], constants["windy_dir"], constants["windy"], constants["g"])
    else:
        func = dV_dt_no_air
        args = (constants["g"],)
    Vs = scipy.integrate.solve_ivp(
        func, 
        t_span=(constants["t0"], constants["tend"]), 
        y0=(constants["y0"], constants["vy0"]), 
        method="RK45", 
        args=args, 
        dense_output=True
    )
    ys = Vs.sol(ts)[0]
    return ys

def get_constants():
    constants = {}
    Cx = 1.2 # https://fr.wikipedia.org/wiki/Coefficient_de_tra%C3%AEn%C3%A9e
    rho = 1.225 # https://fr.wikipedia.org/wiki/Masse_volumique_de_l%27air
    Sx = 0.4*1.8
    Sy = 0.15*0.15
    constants["alphax"] = (1/2)*Cx*rho*Sx
    constants["alphay"] = (1/2)*Cx*rho*Sy

    constants["windx_dir"] = 1 # or -1, wind oriented in the same direction as the x vector (push the human if positive)
    constants["windy_dir"] = 1 # or -1, wind oriented in the same direction as the y vector (slow the fall of the human if positive)
    constants["windx"] = 0 # Speed in m/s of wind in x axis
    constants["windy"] = 0 # Speed in m/s of wind in y axis

    constants["m"] = 70
    constants["g"] = 9.8

    constants["t0"] = 0
    constants["tend"] = 2

    constants["x0"] = 0
    constants["vx0"] = 5

    constants["y0"] = 10
    constants["vy0"] = 0

    return constants

def update_constant(input_value, constant):
    if input_value is not None:
        return input_value
    else:
        return constant

def update_constants(input_constants, constants):
    for input_constant_name in input_constants:
        constants[input_constant_name] = update_constant(input_constants[input_constant_name], constants[input_constant_name])
    return constants

def get_jumped_distance(ts, constants):
    xs = get_xs(ts, constants)
    ys = get_ys(ts, constants)
    
    return xs[np.where(ys == np.min(np.abs(ys)))][0]

def simulator(input_constants, is_air):
    constants = get_constants()
    constants = update_constants(input_constants, constants)
    ts = np.linspace(constants["t0"], constants["tend"], 200)
    xs = get_xs(ts, constants, is_air)
    ys = get_ys(ts, constants, is_air)
    return ts, xs, ys
import matplotlib.pyplot as plt
import numpy as np

# Function to read data from file and parse it into arrays
def read_data(filename):
    time = []
    x = []
    y = []
    psi = []
    
    with open(filename, 'r') as file:
        for line in file:
            t, x_val, y_val, psi_val = map(float, line.split(","))
            time.append(t)
            x.append(x_val)
            y.append(y_val)
            psi.append(psi_val)
    
    return time, x, y, psi

def read_params(filename, flag_is_voilier=False):
    cmd, epsx, epsy, w_speed, w_angle = '', 0, 0, 0, 0
    f = open(filename, 'r')
    first_line = f.readline()
    str_epsx = first_line.split('|')[1]
    epsx = float(str_epsx.split(' ')[2])
    str_epsy = first_line.split('|')[2]
    epsy = float(str_epsy.split(' ')[2])
    str_wind_speed = first_line.split('|')[3]
    w_speed = float(str_wind_speed.split(' ')[3])
    str_wind_angle = first_line.split('|')[4]
    w_angle = float(str_wind_angle.split(' ')[3])

    waypoints = []
    if flag_is_voilier: 
        waypoints.append(float(str_wind_angle.split(' ')[4]))
        for line in f:
            waypoints.append(float(line))

    f.close()
    return cmd, epsx, epsy, w_speed, w_angle, waypoints

def calc_E(x, y, psi, epsx, epsy):
    xE, yE, psiE = [], [], []

    T = np.array([[1, 0, epsy], 
                  [0, 1, epsx], 
                  [0, 0, 1]])
    
    for i in range(0, len(x)): 
        psii = psi[i]
        Ri = np.array([[np.cos(psii), -np.sin(psii)],
                       [np.sin(psii), np.cos(psii)]])
        pE = np.array([[x[i]], [y[i]]]) + np.dot(Ri, np.array([[epsx], [epsy]]))
        xE.append(pE[0, 0])
        yE.append(pE[1, 0])
        psiE.append(psii)

    return xE, yE, psiE
    

# Function to plot the data
def plot_data(time, x, y, psi, time_ref, x_ref, y_ref, psi_ref, xE, yE, psiE, waypoints, flag_is_voilier):
    fig, axs = plt.subplots(3, 1, figsize=(10, 8))
    
    axs[0].plot(time, x, '--', label='x')
    axs[0].plot(time, xE, label='xE')
    axs[0].plot(time_ref, x_ref, label='x_ref')
    axs[0].set_title('x vs Time')
    axs[0].set_xlabel('Time')
    axs[0].set_ylabel('x')
    axs[0].grid()
    axs[0].legend()

    axs[1].plot(time, y, '--', label='y')
    axs[1].plot(time, yE, label='yE')
    axs[1].plot(time_ref, y_ref, label='y_ref')
    axs[1].set_title('y vs Time')
    axs[1].set_xlabel('Time')
    axs[1].set_ylabel('y')
    axs[1].grid()
    axs[1].legend()
    
    axs[2].plot(time, psi, label='psi')
    axs[2].plot(time_ref, psi_ref, label='psi_ref')
    axs[2].set_title('psi vs Time')
    axs[2].set_xlabel('Time')
    axs[2].set_ylabel('psi')
    axs[2].grid()
    axs[2].legend()

    fig, axs = plt.subplots(1, 1, figsize=(10, 8))    
    if flag_is_voilier: 
        i = 0
        while i < len(waypoints):
            axs.plot(waypoints[i], waypoints[i+1], 'ko')
            axs.plot(waypoints[i+2], waypoints[i+3], 'ko')
            axs.plot([waypoints[i], waypoints[i+2]], [waypoints[i+1], waypoints[i+3]], 'k--')
            i += 4
    axs.plot(x, y, '--', label='pos')
    axs.plot(xE, yE, label='E')
    axs.plot(x_ref, y_ref, label='ref')


    axs.set_title('y vs x')
    axs.set_xlabel('x')
    axs.set_ylabel('y')
    axs.grid()
    axs.legend()

    # Interpolate xE and yE to match the sampling rate of x_ref and y_ref
    xE_interp = np.interp(time_ref, time, xE)
    yE_interp = np.interp(time_ref, time, yE)

    # Calculate the errors
    ex = np.array(x_ref) - np.array(xE_interp)
    ey = np.array(y_ref) - np.array(yE_interp)
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))
    axs[0].plot( ex, label='ex')
    axs[0].set_title('ex vs Time')
    axs[0].set_xlabel('Time')
    axs[0].set_ylabel('ex')
    axs[0].grid()
    axs[0].legend()

    axs[1].plot(ey, label='ey')
    axs[1].set_title('ey vs Time')
    axs[1].set_xlabel('Time')
    axs[1].set_ylabel('ey')
    axs[1].grid()
    axs[1].legend()
    
    plt.tight_layout()
    plt.show()

# Main function
def main():
    # date = '2024-11-29_12-40-36_boustro'
    # date = '2024-11-29_12-12-35_etoile_check'
    # date = '2024-11-29_11-49-14_voilier_carre'
    # date = '2024-11-29_11-28-37_evitement_ok'
    # date = '2024-11-28_12-07-29_voilier_ok_2'
    # date = '2024-11-28_12-00-05_voilier_ok_1'
    # date = '2024-11-27_15-59-11_boustro_ok'
    date = '2024-11-27_15-54-45_docking_ok'
    filename_params = f'/home/user/log_bboat/{date}/params.txt'
    filename_state = f'/home/user/log_bboat/{date}/pose_rob.txt' 
    flag_is_voilier = 'voilier' in date
    if flag_is_voilier:
        filename_ref = f'/home/user/log_bboat/{date}/pose_vsb.txt'
    else: 
        filename_ref = f'/home/user/log_bboat/{date}/control_target.txt'

    cmd, epsx, epsy, w_speed, w_angle, waypoints = read_params(filename_params, flag_is_voilier)
    time, x, y, psi = read_data(filename_state)
    time_ref, x_ref, y_ref, psi_ref = read_data(filename_ref)
    xE, yE, psiE = calc_E(x, y, psi, epsx, epsy)
    plot_data(time, x, y, psi, time_ref, x_ref, y_ref, psi_ref, xE, yE, psiE, waypoints, flag_is_voilier)

if __name__ == "__main__":
    main()
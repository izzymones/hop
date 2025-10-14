import numpy as np
import casadi as ca

class Constants:
    def __init__(self):

        # general constants
        # ---------------------------------------------------------------
        self.timelimit = 1 # time limit for a flight in seconds 


        # model related constants
        # ---------------------------------------------------------------
        self.m = 1.5    # mass of drone in kg
        self.l = 0.18   # length from point of thrust to center of mass in meters

        self.gx = 0     # acceleration due to gravity in world frame
        self.gy = 0
        self.gz = -9.81
        self.g = np.array([
            self.gx,
            self.gy,
            self.gz
        ])

        self.Ixx = 0.06     # moments of inertia
        self.Iyy = 0.06
        self.Izz = 0.012
        self.moment_arm = np.array([
            0,
            0,
            -self.l/2
        ])

        self.I = np.array([
            [self.Ixx,0,0],
            [0,self.Iyy,0],
            [0,0,self.Izz]
        ])

        self.I_diag = [self.Ixx, self.Iyy, self.Izz]
        self.I_inv = np.linalg.inv(self.I)

        # thrust model and mapping
        # thrust is modeled as a degree 2 polynomial with coefficients a, b, c
        # that is scaled by a thrust curve constant
        self.tcc = 1.6 # thrust curve constant 
        # these values are based on the 21V data from 
        # https://drive.google.com/file/d/1KMV0z-SipDZAr_uxRndRSnhmOHLBXNA5/view
        self.a = 1.327 * self.tcc
        self.b = 0.284 * self.tcc
        self.c = -0.015 * self.tcc
        # rotation about z axis caused by differential thrust between motors is modeled linearly with d
        self.d = 0.1 

 
        # mechanical and hardware constants
        # ---------------------------------------------------------------       
        self.outer_gimbal_range = [-20,20]          # outer gimbal range limit in degrees
        self.inner_gimbal_range = [-13.5,13.5]      # inner gimbal range limit in degrees
        self.theta_dot_constraint = 6.16            # gimbal rate of change limit in degrees per second
        self.thrust_dot_limit = 20.0                # thrust rate of change limit in Newtons per second
        self.hover_thrust = 2.529                   # the thrust rate needed to hover
        self.prop_thrust_constraint = 50.0          # max thrust allowed 
        self.diff_thrust_constraint = [-0.8,0.8]    # min and max thrust difference allowed

        # NMPC related constants
        # ---------------------------------------------------------------        
        self.dt = 0.02 # 50 Hz like in paper
        self.x0 = ca.vertcat(0.0,0.0,0.0, 0.0,0.0,0.0, 0.0,0.0,0.0,1.0, 0.0,0.0,0.0) # initial state 
        self.Q = ca.DM.eye(13)                                                       # state cost matrix
        self.R = ca.diag([0.03, 0.03, 1, 0.03])                                      # control cost matrix
        self.xr = ca.vertcat(0.0,0.0,0.0, 0.0,0.0,0.0, 0.0,0.0,0.0,1.0, 0.0,0.0,0.0) # goal state
        self.ur = ca.DM([0.0, 0.0, self.hover_thrust, 0.0])                          # goal control

        # list of navigation waypoints for the flight to follow
        # these are (x,y,z) points in world frame meters
        self.waypoints = [
            np.array([0.0, 0.0, 0.0]),
            np.array([0.0, 0.0, 0.25]),
            np.array([0.0, 0.0, 0.0])
        ]

        self.nmpc_rate_constraints = False

        # constants for specific NLP formulations
        # --------------------------------------------------------------- 
        # multiple shooter constants
        self.mpc_horizon = 100 # number of timesteps for nmpc to consider

        # chebyshev pseudospectral constants
        self.spectral_order = 6

        # do-mpc constants
        self.finite_interval_size = 0.3
        self.number_intervals = 6
        self.collocation_degree = 2

        # IPOPT settings
        # --------------------------------------------------------------- 
        self.ipopt_settings = {
            "ipopt.max_iter": 100,                   
            "ipopt.tol": 1e-3,                     
            "ipopt.acceptable_tol": 1e-4,
            'ipopt.print_level': 0,
            'ipopt.sb': 'yes',
            'print_time': 0,
            'ipopt.linear_solver': 'ma27',
            # 'ipopt.warm_start_init_point': 'yes',
            # 'ipopt.warm_start_bound_push': 1e-6,
            # 'ipopt.warm_start_mult_bound_push': 1e-6,
            # 'ipopt.mu_init': 1e-3,  
        }




    # This function makes it possible to print the Constants with print function
    # This way we can add our constants to our runs and simulation logs.
    def __repr__(self):
        s = 'Constants \n' + '---------------------\n'
        s += 'General constants: \n'
        s += '-----------------------------------------------\n'
        s += f"{'flight time:':15}  {str(self.timelimit):15}\n"
        s += 'Model related constants: \n'
        s += '-----------------------------------------------\n'
        s += f"{'m:':10}  {str(self.m):15}\n"
        s += f"{'l:':10}  {str(self.l):15}\n"
        s += f"{'gx:':10}  {str(self.gx):15}\n"
        s += f"{'gy:':10}  {str(self.gy):15}\n"
        s += f"{'gz:':10}  {str(self.gz):15}\n"
        s += f"{'g:':10}  {str(self.g.tolist()):15}\n"
        s += f"{'Ixx:':10}  {str(self.Ixx):15}\n"
        s += f"{'Iyy:':10}  {str(self.Iyy):15}\n"
        s += f"{'Izz:':10}  {str(self.Izz):15}\n"
        s += f"{'moment arm:':20}  {str(self.moment_arm.tolist())}\n" 
        s += f"{'I_inv:':20}  {str(self.I_inv.tolist())}\n" 
        s += 'thrust model constants: \n'
        s += '-----------------------------------------------\n'        
        s += f"{'tcc:':10}  {str(self.tcc):15}\n"
        s += f"{'a:':10}  {str(self.a):15}\n"
        s += f"{'b:':10}  {str(self.b):15}\n"
        s += f"{'c:':10}  {str(self.c):15}\n"
        s += f"{'d:':10}  {str(self.d):15}\n"
        s += 'Mechanical and hardware constants: \n'
        s += '-----------------------------------------------\n'
        s += f"{'outer gimbal range:':20}  {str(self.outer_gimbal_range)}\n" 
        s += f"{'inner gimbal range:':20}  {str(self.inner_gimbal_range)}\n" 
        s += f"{'theta dot max:':20}  {str(self.theta_dot_constraint)}\n" 
        s += f"{'thrust dot max:':20}  {str(self.thrust_dot_limit)}\n" 
        s += f"{'hover thrust:':20}  {str(self.hover_thrust)}\n" 
        s += f"{'max thrust:':20}  {str(self.prop_thrust_constraint)}\n" 
        s += f"{'max diff thrus:':20}  {str(self.diff_thrust_constraint)}\n" 
        s += 'NMPC constants: \n'
        s += '-----------------------------------------------\n'
        s += f"{'dt:':10}  {str(self.dt):15}\n"
        s += f"{'x0:':10}  {str(self.x0)}\n" 
        s += f"{'Q:':10}  {str(self.Q)}\n" 
        s += f"{'R:':10}  {str(self.R)}\n" 
        s += f"{'xr:':10}  {str(self.xr)}\n"
        s += f"{'ur:':10}  {str(self.ur)}\n"        
        s += f"{'waypoints:':20}  {str(self.waypoints):15}\n"   
        s += f"{'NMPC rate constraints:':20}  {str(self.nmpc_rate_constraints)}\n"  
        s += 'NLP constants: \n'
        s += '-----------------------------------------------\n'
        s += f"{'nmpc horizon:':20}  {str(self.mpc_horizon):15}\n"
        s += f"{'spectral order:':20}  {str(self.spectral_order):15}\n"
        s += f"{'size of intervals:':20}  {str(self.finite_interval_size):15}\n"
        s += f"{'num intervals:':20}  {str(self.number_intervals):15}\n"
        s += f"{'collocation deg:':20}  {str(self.collocation_degree):15}\n"
        s += 'IPOPT settings: \n'
        s += '-----------------------------------------------\n'
        s += str(self.ipopt_settings)

        return s



        

    

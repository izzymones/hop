import numpy as np
import casadi as ca
from casadi import sin, cos
import do_mpc

from hop.constants import Constants

mc = Constants()

class DroneModel:
    def __init__(self):

        self.model = do_mpc.model.Model('continuous' , 'SX')
        p = self.model.set_variable(var_type='_x', var_name='p', shape=(3,1))
        v = self.model.set_variable(var_type='_x', var_name='v', shape=(3,1))
        q = self.model.set_variable(var_type='_x', var_name='q', shape=(4,1))
        w = self.model.set_variable(var_type='_x', var_name='w', shape=(3,1))

        state = ca.vertcat(p,v,q,w)
        u = self.model.set_variable(var_type='_u', var_name='u', shape=(4,1))

        I_mat = ca.diag(mc.I_diag)
        F = mc.a * u[2]**2 + mc.b * u[2] + mc.c 
        M = mc.d * mc.Izz * u[3]

        F_vector = F * ca.vertcat(
            sin((np.pi/180)*u[1]),
            -sin((np.pi/180)*u[0])*cos((np.pi/180)*u[1]),
            cos((np.pi/180)*u[0])*cos((np.pi/180)*u[1])
        )

        roll_moment = ca.vertcat(0, 0, M)
        M_vector = ca.cross(mc.moment_arm, F_vector) + roll_moment
        angular_momentum = I_mat @ w

        r_b2w = ca.vertcat(
            ca.horzcat(1 - 2*(state[7]**2 + state[8]**2), 2*(state[6]*state[7] - state[8]*state[9]), 2*(state[6]*state[8] + state[7]*state[9])),
            ca.horzcat(2*(state[6]*state[7] + state[8]*state[9]), 1 - 2*(state[6]**2 + state[8]**2), 2*(state[7]*state[8] - state[6]*state[9])),
            ca.horzcat(2*(state[6]*state[8] - state[7]*state[9]), 2*(state[7]*state[8] + state[6]*state[9]), 1 - 2*(state[6]**2 + state[7]**2)),
        )

        Q_omega = ca.vertcat(
            ca.horzcat(0, state[12], -state[11], state[10]),
            ca.horzcat(-state[12], 0, state[10], state[11]),
            ca.horzcat(state[11], -state[10], 0, state[12]),
            ca.horzcat(-state[10], -state[11], -state[12], 0)
        )

        q_full = state[6:10]
        q_full = q_full / ca.norm_2(q_full)

        self.model.set_rhs('p', v)
        self.model.set_rhs('v', (r_b2w @ F_vector) / mc.m + mc.g)
        self.model.set_rhs('q', 0.5 * Q_omega @ q_full)
        self.model.set_rhs('w', ca.solve(I_mat, M_vector - ca.cross(w, angular_momentum)))

        self.model.setup()
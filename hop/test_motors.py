import rclpy
from hop.offboard_node import OffBoardNode
from hop.constants import Constants
mc = Constants()

pwm = [float(i) / 20.0 for i in range(10, 20)]
class TestMotors(OffBoardNode):

    def __init__(self):
        super().__init__('test_motors', timelimit=100, dt=mc.dt)
        self.dual_inc = 0.1
        self.run_diff_test = False
        self.diff_pairs = []
        self.diff_test_i = 0
        self.i = 0
        for p in pwm:
            for j in pwm:
                self.diff_pairs.append([p,j])

    def timer_callback(self):

        # manage key presses
        if self.key == 'u':
            self.key = ''
            self.pwm_motors[0] += self.dual_inc
            self.pwm_motors[1] += self.dual_inc
            self.get_logger().info('motor pwm ' + str(self.pwm_motors))

        elif self.key == 'j':
            self.key = ''
            self.pwm_motors[0] -= self.dual_inc
            self.pwm_motors[1] -= self.dual_inc
            self.get_logger().info('motor pwm ' + str(self.pwm_motors))

        elif self.key == 't':
            self.key = ''
            self.run_diff_test = True

        elif not self.key == '':
            self.pwm_motors = [0.0, 0.0]
            raise SystemExit
        
        super().timer_callback()

    
    def run_motors(self):

        if self.run_diff_test:
            if self.diff_test_i >= len(self.diff_pairs):
                self.pwm_motors = [0.0, 0.0]
                raise SystemExit
            else:
                if self.i % 20 == 0:
                    self.pwm_motors = self.diff_pairs[self.diff_test_i]
                    self.get_logger().info('motor pwm ' + str(self.pwm_motors))
                    self.diff_test_i += 1
                self.i += 1

        super().run_motors()        

def main(args=None):
    rclpy.init(args=args)
    motor_test = TestMotors()
    motor_test.logging_on = False

    try:
        rclpy.spin(motor_test)
    except SystemExit:
        pass
    finally:
        motor_test.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
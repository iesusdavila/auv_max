import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from nav_msgs.msg import Odometry
import matplotlib.pyplot as plt
import numpy as np

class PositionPlotter(Node):
    def __init__(self):
        super().__init__('position_plotter_angular')
        self.target_pitch = self.create_subscription(
            Float64,
            '/model/rov_max/longitud_controller/target_pitch',
            self.target_callback_pitch,
            10
        )
        self.target_yaw = self.create_subscription(
            Float64,
            '/model/rov_max/longitud_controller/target_yaw',
            self.target_callback_yaw,
            10
        )
        self.target_posxy = self.create_subscription(
            Float64,
            '/model/rov_max/longitud_controller/target_longitud',
            self.target_callback_posxy,
            10
        )
        self.target_prof = self.create_subscription(
            Float64,
            '/model/rov_max/longitud_controller/target_altitud',
            self.target_callback_prof,
            10
        )
        self.odometry_sub = self.create_subscription(
            Odometry,
            '/model/rov_max/odometry',
            self.odometry_callback,
            10
        )
        self.pitch_positions = []
        self.yaw_positions = []
        self.posxy_positions = []
        self.prof_positions = []
        self.target_position_pitch = None
        self.target_position_yaw = None
        self.target_position_posxy = None
        self.target_position_prof = None

        # Crear subplots
        self.fig, self.axes = plt.subplots(4, 1, figsize=(10, 8))
        self.fig.tight_layout()

    def target_callback_pitch(self, msg):
        self.target_position_pitch = msg.data
    
    def target_callback_yaw(self, msg):
        self.target_position_yaw = msg.data

    def target_callback_posxy(self, msg):
        self.target_position_posxy = msg.data
    
    def target_callback_prof(self, msg):
        self.target_position_prof = msg.data

    def euler_from_quaternion(self, quaternion):
        x = quaternion.x
        y = quaternion.y
        z = quaternion.z
        w = quaternion.w

        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = np.arctan2(sinr_cosp, cosr_cosp)

        sinp = 2 * (w * y - z * x)
        pitch = np.arcsin(sinp)

        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = np.arctan2(siny_cosp, cosy_cosp)

        return roll, pitch, yaw

    def odometry_callback(self, msg):
        euler = self.euler_from_quaternion(msg.pose.pose.orientation)
        pitch = euler[1]
        yaw = euler[2]
        self.pitch_positions.append(pitch)
        self.yaw_positions.append(yaw)
        self.posxy_positions.append(msg.pose.pose.position.x)
        self.prof_positions.append(msg.pose.pose.position.z)
        self.plot_positions()

    def plot_positions(self):
        self.axes[0].cla()
        self.axes[0].plot(self.pitch_positions, label='Actual Position Pitch')
        self.axes[0].set_ylabel('Pitch')
        self.axes[0].set_xlabel('Time')

        self.axes[1].cla()
        self.axes[1].plot(self.yaw_positions, label='Actual Position Yaw')
        self.axes[1].set_ylabel('Yaw')
        self.axes[1].set_xlabel('Time')

        self.axes[2].cla()
        self.axes[2].plot(self.posxy_positions, label='Actual Position PosXY')
        self.axes[2].set_ylabel('PosXY')
        self.axes[2].set_xlabel('Time')

        self.axes[3].cla()
        self.axes[3].plot(self.prof_positions, label='Actual Position Profundidad')
        self.axes[3].set_ylabel('Profundidad')
        self.axes[3].set_xlabel('Time')

        if self.target_position_pitch is not None:
            self.axes[0].axhline(y=self.target_position_pitch, color='r', linestyle='--', label='Target Position Pitch')
        if self.target_position_yaw is not None:
            self.axes[1].axhline(y=self.target_position_yaw, color='g', linestyle='--', label='Target Position Yaw')
        if self.target_position_posxy is not None:
            self.axes[2].axhline(y=self.target_position_posxy, color='b', linestyle='--', label='Target Position PosXY')
        if self.target_position_prof is not None:
            self.axes[3].axhline(y=self.target_position_prof, color='y', linestyle='--', label='Target Position Profundidad')

        for ax in self.axes:
            ax.legend()
            ax.grid(True)

        self.fig.canvas.flush_events()
        plt.pause(0.01)

def main(args=None):
    rclpy.init(args=args)
    position_plotter = PositionPlotter()
    rclpy.spin(position_plotter)
    position_plotter.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

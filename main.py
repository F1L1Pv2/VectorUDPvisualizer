import math
import socket
import threading
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
import random

# Define the function to visualize a vector
def visualize_vectors(frames):
    global ax
    global vectors
    ax.clear()
    ax.set_xlim([-1.5, 1.5])
    ax.set_ylim([-1.5, 1.5])
    ax.set_zlim([-1.5, 1.5])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Orientation Vectors')

    for v in vectors.values():

        color = (random.random(), random.random(), random.random())
        ax.quiver(0, 0, 0, v[0], v[1], v[2], color=color)

vectors ={}

def rotate_quaternion_by_quaternion(q, r):
    """
    Rotates quaternion q by quaternion r using quaternion multiplication
    """
    # quaternion multiplication formula: q * r = (w1w2 - x1x2 - y1y2 - z1z2, 
    #                                             w1x2 + x1w2 + y1z2 - z1y2, 
    #                                             w1y2 - x1z2 + y1w2 + z1x2, 
    #                                             w1z2 + x1y2 - y1x2 + z1w2)
    w1, x1, y1, z1 = q
    w2, x2, y2, z2 = r
    return (w1*w2 - x1*x2 - y1*y2 - z1*z2,
            w1*x2 + x1*w2 + y1*z2 - z1*y2,
            w1*y2 - x1*z2 + y1*w2 + z1*x2,
            w1*z2 + x1*y2 - y1*x2 + z1*w2)


# Define the function to handle incoming messages
def handle_message(msg, ax):
    global vectors
    try:
        deviceId, q0, q1, q2, q3 = map(float, msg.split(','))
        q = np.array([q0, q1, q2, q3])

        qx = q1
        qy = q2
        qz = q3
        qw = q0

        deviceId = int(deviceId)

        #conver quaternion to euler angles
        roll = np.arctan2(2 * (q[0] * q[1] + q[2] * q[3]), 1 - 2 * (q[1] * q[1] + q[2] * q[2]))
        pitch = np.arcsin(2 * (q[0] * q[2] - q[3] * q[1]))
        yaw = np.arctan2(2 * (q[0] * q[3] + q[1] * q[2]), 1 - 2 * (q[2] * q[2] + q[3] * q[3]))
        
        #print in degrees
        # print("roll: ", roll * 180 / np.pi, "pitch: ", pitch * 180 / np.pi, "yaw: ", yaw * 180 / np.pi)

        # convert the quaternion to a vector


        #rotate quaternion by 90 degrees around x axis

        # v = np.array([0, 2 * (q[1] * q[3] - q[0] * q[2]), 2 * (q[0] * q[1] + q[2] * q[3]), 2 * (0.5 - q[1] * q[1] - q[2] * q[2])])

        v = 2 * (qx*qz - qw*qy), 2 * (qy*qz + qw*qx), 1 - 2 * (qx*qx + qy*qy)

        

        # check if the vector is already in the list
        vectors[deviceId] = v
    except ValueError:
        pass




# Define the function to receive messages
def receive_messages():
    # Set up the UDP server
    host = '0.0.0.0'
    port = 8000
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))

    while True:
        msg, _ = server_socket.recvfrom(1024)
        msg = msg.decode()
        handle_message(msg, ax)

# Create a figure
fig = plt.figure()
global ax
ax = fig.add_subplot(111, projection="3d")
ax.set_xlim([-1.5, 1.5])
ax.set_ylim([-1.5, 1.5])
ax.set_zlim([-1.5, 1.5])

# Start the UDP server in a separate thread
udp_thread = threading.Thread(target=receive_messages)
udp_thread.start()

ani = animation.FuncAnimation(fig, visualize_vectors, interval=10)

# Show the figure
plt.show()

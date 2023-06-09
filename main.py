import math
import socket
import threading
import numpy as np
import matplotlib.pyplot as plt
from math import cos, sin
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
import random

def angleAxisQuat(axis, angle):
    if axis == "x":
        q = (
            cos(angle / 2.),
            sin(angle / 2.),
            0,
            0
        )
    elif axis == "y":
        q = (
            cos(angle / 2.),
            0,
            sin(angle / 2.),
            0
        )
    elif axis == "z":
        q = (
            cos(angle / 2.),
            0,
            0,
            sin(angle / 2.)
        )
    else:
        raise ValueError("Invalid axis")

    return q

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

def multiply(q1,q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    return np.array([-x1 * x2 - y1 * y2 - z1 * z2 + w1 * w2,
                    x1 * w2 + y1 * z2 - z1 * y2 + w1 * x2,
                    -x1 * z2 + y1 * w2 + z1 * x2 + w1 * y2,
                    x1 * y2 - y1 * x2 + z1 * w2 + w1 * z2], dtype=np.float64)

# Define the function to handle incoming messages
def handle_message(msg, ax):
    global vectors
    try:
        deviceId, q0, q1, q2, q3 = map(float, msg.split(','))
        q = np.array([q0, q1, q2, q3])

        # q2=[0.71,0.71,0,0]

        #multiply quaternion by quaternion

        # q=multiply(q,q2)

        # q = np.array([0.71,0,0.71,0])

        # q=multiply(q,q2)
        nQ = np.array(angleAxisQuat("x", 1.570796))
        q = multiply(q, nQ)

        qx = q[1]
        qy = q[2]
        qz = q[3]
        qw = q[0]

        deviceId = int(deviceId)

        # Obtain the quaternion from your Android application
        
        quaternion = np.array([qw, qx, qy, qz])


        
        # Convert the quaternion from the Android coordinate system to the new coordinate system
        
        result_quaternion = np.dot(transform_matrix, quaternion)

        qw = result_quaternion[0]
        qx = result_quaternion[1]
        qy = result_quaternion[2]
        qz = result_quaternion[3]

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
        
forward = np.array([0, 0, 1])
up = np.array([0, 1, 0])
right = np.array([1, 0, 0])
# Define the transformation matrix from the Android coordinate system to the new coordinate system
transform_matrix = np.eye(4)
transform_matrix[:3,:3] = np.column_stack((right, up, -forward))

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

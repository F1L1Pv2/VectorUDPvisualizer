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
    # print(vectors)
    ax.set_xlim([-1.5, 1.5])
    ax.set_ylim([-1.5, 1.5])
    ax.set_zlim([-1.5, 1.5])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Orientation Vectors')
    # for v in vectors:
    #     ax.quiver(0, 0, 0, v[0], v[1], v[2], color='r')
    for v in vectors.values():

        #find v in vectors

        # id = list(vectors.keys())[list(vectors.values()).index(v)]
        # print(id)

        # #set seed of random number generator to id
        # random.seed(id)

        color = (random.random(), random.random(), random.random())
        ax.quiver(0, 0, 0, v[0], v[1], v[2], color=color)


vectors ={}

# Define the function to handle incoming messages
def handle_message(msg, ax):
    try:
        deviceId, azimuth, pitch, roll = map(float, msg.split(','))
        azimuth = np.radians(azimuth)
        pitch = np.radians(pitch)
        roll = np.radians(roll)
        R_az = np.array([[np.cos(azimuth), -np.sin(azimuth), 0], [np.sin(azimuth), np.cos(azimuth), 0], [0, 0, 1]])
        R_p = np.array([[np.cos(pitch), 0, np.sin(pitch)], [0, 1, 0], [-np.sin(pitch), 0, np.cos(pitch)]])
        R_r = np.array([[1, 0, 0], [0, np.cos(roll), -np.sin(roll)], [0, np.sin(roll), np.cos(roll)]])
        R = R_az.dot(R_p).dot(R_r)
        v = R.dot(np.array([1, 0, 0]))
        
        deviceId = int(deviceId)

        #check if the vector is already in the list
        vectors[deviceId] = v
        

        
        # visualize_vectors(ax, vectors)

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
        # Call the message handling function
        # print(msg)
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
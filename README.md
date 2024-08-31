# Introcution

This project is a video conferencing and messaging application inspired by Zoom but built fron the group up using custom TCP and UDP protocols. It enables reliable text communication over TCP and efficient video file transfer over UDP. It supports key features such as user authentication, broadcasting messages, creating separate chat rooms, and peer-to-peer file uploads. This project is assignment for UNSW Computer Network Assignment worth 20 marks, and I got full marks

**Technical Stack**

**Programming Language**: Python

**Networking**: TCP/IP, UDP

**Concurrency**: Multi-threading with Python's `threading` module

**Socket Programming**: Python's `socket` library for implementing custom protocols



# Description

## Server component

The server-side is designed to handle multiple clients concurrently using multi-threading, ensuring that each user interaction, including login, message broadcasting, and chat room creation, is process efficiently.
The server maintains user states, manages active sessions, and logs all interactions, showcasing a robust approach to building scalable, reliable network services.
**Key features include:**

1. **User Authentication and Blocking:** Handles login attempts and blocks users after multiple failed attempts.
2. **Message Broadcasting:** Supports broadcasting messages to all active users and logs them.
3. **Chat Room Management:** Allows users to create and manage separate chat rooms, enabling private group communications.
4. **UDP-Based File Transfer:** Facilitates peer-to-peer file transfer using UDP, ensuring efficient and timely delivery.



## Client component

The client-side manages the user's interactions with the server, including logging in, sending commands, and receiving messages. It establishes and maintains TCP connections for command exchanges and uses UDP for direct peer-to-peer file transfers. The client application is designed to be responsive and capable of handling multiple tasks simultaneously through multi-threading.

**Key features include:**

1. **User Interaction:** Handles user input and communicates with the server for command execution.
2. **Command Handling:** Supports various commands like broadcasting messages, checking active users, and uploading files.
3. **Multi-threaded Communication:** Simultaneously listens for server responses and manages UDP file transfers without blocking user input.

import matplotlib.pyplot as plt

# Data
x = [1, 2, 3, 4, 5]
y1 = [10, 8, 6, 4, 2]
y2 = [5, 4, 3, 2, 1]

# Create a figure and axes without add_subplot(111)
fig1, ax1 = plt.subplots()
ax1.plot(x, y1, label='Line 1')
ax1.plot(x, y2, label='Line 2')
ax1 = fig1.add_subplot(121)
ax1.legend()
ax1.set_xlabel('X-axis')
ax1.set_ylabel('Y-axis')
ax1.set_title('Without add_subplot(111)')

# Create a figure and axes with add_subplot(111)
fig2 = plt.figure()
ax2 = fig2.add_subplot(122)
ax2.plot(x, y1, label='Line 1')
ax2.plot(x, y2, label='Line 2')
ax2.legend()
ax2.set_xlabel('X-axis')
ax2.set_ylabel('Y-axis')
ax2.set_title('With add_subplot(111)')

# Save the figures
fig1.savefig('graph_without_subplot.png')
fig2.savefig('graph_with_subplot.png')


import base64

message = "Python is fun"
message_bytes = message.encode('ascii')
print(message_bytes)
base64_bytes = base64.b64encode(message_bytes)
print(base64_bytes)
base64_message = base64_bytes.decode('ascii')
print(base64_message)
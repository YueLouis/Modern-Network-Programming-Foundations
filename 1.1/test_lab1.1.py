import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 9999))

# Test echo
print("Sending: Hello World")
client.send(b"Hello World\n")
response = client.recv(1024).decode()
print(f"Response: {response}")

# Test TIME command
print("\nSending: TIME")
client.send(b"TIME\n")
response = client.recv(1024).decode()
print(f"Response: {response}")

client.close()
print("\nTest completed!")
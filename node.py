import socket
import threading

class Node:
	def __init__(self, ip_addr, port, node_id):

		self.my_port = port 			# an int representing the port number
		self.my_ip_addr = ip_addr 		# a string representing the IP address
		self.my_node_id = node_id 		# a string representing the node name
		self.other_nodes = {}			# dictionary format {node name : node object}
		self.existing_addresses = [(str(self.my_ip_addr), str(self.my_port))]	# list format [(ip_address, port)]

		#initialize socket
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		
		#initialize base server to my port and my IP address
		self.server.bind(("0.0.0.0", self.my_port))
		
		#listen for connection from clients
		self.server.listen()

		#start accepting connections from new clients
		threading.Thread(target=self.accept_new_clients).start()

		#wait before starting prompt
		for i in range(10000000):
			pass

		threading.Thread(target=self.prompt).start()

	def prompt(self):
		print()
		print("Node '" + self.my_node_id + "' initiated.")
		print()
		while True:
			cmd = input(">>>: ").split()
			if len(cmd) == 3 and cmd[0] == "connect":
				self.connect_to_node(str(cmd[1]), int(cmd[2]))
				print()
			if len(cmd) >= 3 and cmd[0] == "write":
				self.write_to_node(cmd[1], " ".join(cmd[2:]))


	def connect_to_node(self, dest_ip_addr, dest_port):
		#done as a client connecting to an existing server

		if (str(dest_ip_addr), str(dest_port)) == (str(self.my_ip_addr), str(self.my_port)):
			print("Cannot connect to self node.")
		elif (str(dest_ip_addr), str(dest_port)) in self.existing_addresses:
			print("Already connected.")
		else:
			#initialize a new socket
			new_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			#connect to new existing server
			new_server.connect((dest_ip_addr, dest_port))
			#send my info to new server
			data = str(self.my_node_id) + " " + str(self.my_ip_addr) + " " + str(self.my_port)
			new_server.send(data.encode("ascii"))
			#receive new server info
			new_server_id = new_server.recv(1024).decode("ascii")

			self.other_nodes[new_server_id] = new_server
			self.existing_addresses.append((str(dest_ip_addr), str(dest_port)))
			print("Client side: " + str(self.existing_addresses))
			print("Connected to " + new_server_id)

			#start receiving messages from new server
			threading.Thread(target=self.receive_from_all_nodes, args=(new_server_id, )).start()


	def accept_new_clients(self):
		while True:

			#receive connection from new client
			new_client, address = self.server.accept()
			new_client_id, sent_ip_addr, sent_port = new_client.recv(1024).decode("ascii").split(" ")
			new_client.send(self.my_node_id.encode("ascii"))

			self.other_nodes[new_client_id] = new_client
			self.existing_addresses.append((str(sent_ip_addr), str(sent_port)))
			print("Server side: " + str(self.existing_addresses))
			print("Connected to " + new_client_id)

			#start receiving messages from new client
			threading.Thread(target=self.receive_from_all_nodes, args=(new_client_id,)).start()


	def receive_from_all_nodes(self, other_node_id):
		while True:
			message = self.other_nodes[other_node_id].recv(1024).decode("ascii")
			if len(message) > 0:
				print(message)
				print()


	#write a message from this node to another node.
	def write_to_node(self, other_node_id, message):
		if other_node_id == self.my_node_id:
			print("Cannot write to self node.")
		elif other_node_id not in self.other_nodes:
			print("Cannot find Node: '" + other_node_id + "'.")
		else:
			if len(message) > 0:
				self.other_nodes[other_node_id].send((self.my_node_id + ": " + message).encode("ascii")) 

ip = str(input("IP: "))
port = int(input("port: "))
name = (input("name: "))
Node(ip, port, name)




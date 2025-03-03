import argparse
import random
import time
import socket
import threading
import queue
import sys

class Machine:
    def __init__(self, machine_id, listen_host, listen_port, peers_str):
        self.machine_id = machine_id
        self.listen_host = listen_host
        self.listen_port = listen_port
        
        # Parse peer list: "host1:port1,host2:port2,..."
        # We'll store them in a list of (host, port) tuples.
        self.peer_info = []
        for p in peers_str.split(","):
            host_port = p.strip().split(":")
            phost = host_port[0]
            pport = int(host_port[1])
            self.peer_info.append((phost, pport))
        
        # Initialize Lamport clock
        self.logical_clock = 0
        
        # We'll store incoming message timestamps in a thread-safe queue
        self.msg_queue = queue.Queue()
        
        # Decide random ticks-per-second from 1..12 (increasing variability)
        # (You can also experiment with other ranges or distributions.)
        self.ticks_per_second = random.randint(1, 12)
        self.cycle_time = 1.0 / self.ticks_per_second
        
        # Open a log file for this machine
        self.log_file = open(f"machine_{self.machine_id}.log", "w")
        
        # Create a server socket and listen for connections
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.listen_host, self.listen_port))
        self.server_socket.listen(5)
        
        # We'll keep track of sockets connected to our peers
        # Keyed by (host, port) => socket
        self.peer_sockets = {}
        
        # Start a thread to accept incoming connections
        self.accept_thread = threading.Thread(target=self.accept_incoming, daemon=True)
        self.accept_thread.start()
        
        # Connect to our known peers (some of them might also connect to us)
        self.connect_to_peers()
        
        self.log_event(f"INIT", note=f"ticks={self.ticks_per_second}")

    def connect_to_peers(self):
        """
        Initiate connections to each peer in peer_info with a simple retry mechanism.
        """
        for (phost, pport) in self.peer_info:
            # Skip if it's our own port
            if (phost == self.listen_host and pport == self.listen_port):
                continue
            
            # Try connecting up to 5 times with a 1-second sleep between attempts
            max_retries = 5
            for attempt in range(1, max_retries + 1):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((phost, pport))
                    self.peer_sockets[(phost, pport)] = sock
                    break  # Connected successfully, no need to retry
                except Exception as e:
                    print(f"[Machine {self.machine_id}] "
                          f"Attempt {attempt}/{max_retries} failed to connect to {phost}:{pport}. "
                          f"Error: {e}", file=sys.stderr)
                    if attempt < max_retries:
                        time.sleep(1)  # Wait before retrying

    def accept_incoming(self):
        """
        Accept incoming connections in a loop and spawn a thread to handle each one.
        """
        while True:
            try:
                client_sock, addr = self.server_socket.accept()
                t = threading.Thread(target=self.receive_messages, args=(client_sock,), daemon=True)
                t.start()
            except Exception as e:
                print(f"Socket closed or error accepting: {e}", file=sys.stderr)
                break

    def receive_messages(self, sock):
        """
        Continuously read data from a client socket and push the timestamps into the msg_queue.
        """
        while True:
            try:
                data = sock.recv(1024)
                if not data:
                    break  # connection closed by peer
                msg_str = data.decode("utf-8").strip()
                # Expected format: "lamport_timestamp:sender_id"
                # Example: "17:2"
                parts = msg_str.split(":")
                their_clock = int(parts[0])
                self.msg_queue.put(their_clock)
            except Exception as e:
                print(f"Error receiving: {e}", file=sys.stderr)
                break
        
        sock.close()

    def send_message(self, sock):
        """
        Send our current logical clock to a peer socket.
        We also send our machine ID if we want the receiver to know who sent the message.
        """
        msg_str = f"{self.logical_clock}:{self.machine_id}"
        try:
            sock.sendall(msg_str.encode("utf-8"))
        except Exception as e:
            print(f"Error sending message: {e}", file=sys.stderr)

    def log_event(self, event_type, queue_len=None, note=None):
        """
        Write a log line:
          <system_time>, <event_type>, L=<lamport_clock>, optional queue_len, optional note
        """
        now = time.time()
        line = f"{now:.4f}, {event_type}, L={self.logical_clock}"
        if queue_len is not None:
            line += f", queue={queue_len}"
        if note:
            line += f", {note}"
        line += "\n"
        self.log_file.write(line)
        self.log_file.flush()

    def run(self, run_time=60):
        """
        Main loop:
         - runs for 'run_time' seconds
         - each iteration tries to stay close to (1 / ticks_per_second) in duration
         - check for incoming messages first; if none, do a random event
        """
        start_time = time.time()
        
        while (time.time() - start_time) < run_time:
            cycle_start = time.time()
            
            # Check if there's a message in the queue
            if not self.msg_queue.empty():
                # Process one incoming message
                their_clock = self.msg_queue.get()
                # Lamport receive rule: L = max(L, their_clock) + 1
                self.logical_clock = max(self.logical_clock, their_clock) + 1
                self.log_event("RECEIVE", queue_len=self.msg_queue.qsize())
            else:
                # No incoming message => do a random event
                r = random.randint(1, 10)
                
                if r == 1:
                    # Send to exactly ONE peer (choose randomly if multiple)
                    self.logical_clock += 1  # increment on send
                    if self.peer_sockets:
                        sock = random.choice(list(self.peer_sockets.values()))
                        self.send_message(sock)
                    self.log_event("SEND(1)")
                
                elif r == 2:
                    # Send to "the other" single peer
                    self.logical_clock += 1
                    if len(self.peer_sockets) >= 2:
                        all_socks = list(self.peer_sockets.values())
                        sock = all_socks[1 % len(all_socks)]
                        self.send_message(sock)
                    elif self.peer_sockets:
                        # fallback if only one peer
                        sock = list(self.peer_sockets.values())[0]
                        self.send_message(sock)
                    self.log_event("SEND(2)")
                
                elif r == 3:
                    # Send to ALL peers
                    self.logical_clock += 1
                    for sock in self.peer_sockets.values():
                        self.send_message(sock)
                    self.log_event("SEND(3)")
                
                else:
                    # Internal event
                    self.logical_clock += 1
                    self.log_event("INTERNAL")
            
            # Sleep enough so we only do 'ticks_per_second' cycles per second
            elapsed = time.time() - cycle_start
            to_sleep = self.cycle_time - elapsed
            if to_sleep > 0:
                time.sleep(to_sleep)
        
        # Cleanup after finishing
        self.shutdown()

    def shutdown(self):
        """
        Close all resources.
        """
        self.log_event("SHUTDOWN")
        self.log_file.close()
        self.server_socket.close()
        for sock in self.peer_sockets.values():
            sock.close()
        print(f"Machine {self.machine_id} finished.")

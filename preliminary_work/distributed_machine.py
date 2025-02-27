#!/usr/bin/env python3

import argparse
import random
import time
import socket
import threading
import queue
import sys

def parse_arguments():
    """
    Parse command-line arguments for the distributed machine.
    Example:
      python distributed_machine.py \
          --id=1 \
          --host=127.0.0.1 \
          --port=5001 \
          --peers=127.0.0.1:5002,127.0.0.1:5003 \
          --run_time=60
    """
    parser = argparse.ArgumentParser(
        description="Run a single instance of a distributed machine with a Lamport clock."
    )
    parser.add_argument("--id", type=int, required=True,
                        help="Unique ID of this machine (e.g. 1, 2, 3).")
    parser.add_argument("--host", type=str, default="127.0.0.1",
                        help="Host/IP address on which to listen (default 127.0.0.1).")
    parser.add_argument("--port", type=int, required=True,
                        help="TCP port to listen on.")
    parser.add_argument("--peers", type=str, required=True,
                        help="Comma-separated list of other machines in the form host:port,host:port.")
    parser.add_argument("--run_time", type=int, default=60,
                        help="Number of seconds to run before stopping (default: 60).")
    return parser.parse_args()


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
        
        # Decide random ticks-per-second from 1..6
        self.ticks_per_second = random.randint(1, 6)
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
        Initiate connections to each peer in peer_info.
        It's possible that some peers haven't started listening yet
        or we might end up with two connections (one in each direction).
        For a basic assignment, this is usually acceptable.
        """
        for (phost, pport) in self.peer_info:
            # If it's our own port, skip
            if (phost == self.listen_host and pport == self.listen_port):
                continue
            
            # Attempt to connect
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((phost, pport))
                self.peer_sockets[(phost, pport)] = sock
            except Exception as e:
                print(f"Failed to connect to peer {phost}:{pport} => {e}", file=sys.stderr)

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
                # sender_id = int(parts[1])  # If you want to track who sent it
                
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
          <system_time>, <event_type>, <lamport_clock>, optional queue_len, optional note
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
                
                # Log
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
                    # (If you have multiple peers, you can choose the second,
                    #  or some other logic. We'll do a simple fallback.)
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


def main():
    args = parse_arguments()
    
    # Seed the random module so each run can differ (or you can set a fixed seed).
    # random.seed(12345)  # for reproducibility if needed
    
    m = Machine(
        machine_id=args.id,
        listen_host=args.host,
        listen_port=args.port,
        peers_str=args.peers
    )
    
    m.run(run_time=args.run_time)


if __name__ == "__main__":
    main()

# CS2620_Assignment_3


**Overview**: 
- Single socket-based Python script that runs multiple times (once for each machine). Script can behave differently based on: 
  - Command-line arguments (e.g., which port to listen on, the ID of this machine, the IP/ports of the other machines)
  - (Metadata of machine, e.g. outward-facing IP)

**How to Run**: 
- Aforementioned machine script is contained in `./src/distributed_machine.py`
- Machine UID, IP, Port, and Peers can be specified via CLI
- Sample script to run: 

```bash
python distributed_machine.py --id=1 --port=5001 --peers=localhost:5002,localhost:5003
python distributed_machine.py --id=2 --port=5002 --peers=localhost:5001,localhost:5003
python distributed_machine.py --id=3 --port=5003 --peers=localhost:5001,localhost:5002
```

Within our ecosystem, each machine: 
1. Listens for incoming connections/messages from its peers.
2. Maintains a Lamport clock to track a logical notion of time.
3. Randomly decides whether to send messages to peers or perform internal events.
4. Logs every event—send, receive, internal, initialization, and shutdown—to a local file.

We track relative time via **Lamport Clocks**: 
- Integer in each process that helps to order events in a distributed system
  1. Increment on local events
	 * Whenever a process does an internal event or sends a message, it does `logical_clock += 1`
  2. Synchronize on receive
	 * Every message carries the sender's logical clock value
	 * When a process receives a message carrying timestamp T, it does `logical_clock = max(logical_clock, T) + 1`

To run all of the scripts to get all output files, we created an executable:
```bash
chmod +x run_machines.sh
./run_machines.sh
```

**File Structure:**
```
├── src
│   └── distributed_machine.py
├── README.md
└── testing
│   └── tests1/
│   └── tests2/
│   └── tests3/
│   └── ...
```

**Log Format:**

Each event line in `machine_<id>.log` follows this format:
- **`<system_time>`**: Real‐world time (epoch time in floating‐point seconds).
- **`<event_type>`**: One of:
  - `INIT`
  - `RECEIVE`
  - `SEND(1)`, `SEND(2)`, `SEND(3)`
  - `INTERNAL`
  - `SHUTDOWN`
- **`L=<lamport_clock>`**: The machine’s current Lamport clock value.
- **`queue=<queue_len>`**: *(Optional)* Logged **only** for `RECEIVE` events, representing the message queue size after popping one message.
- **`note=`**: *(Optional)* Logged for `INIT` to record details like chosen ticks per second.

**Observations:**
When running multiple machines over at least one minute each, you can see interesting patterns in the logs:
- Clock Drift: Each machine operates at a randomly chosen tick rate, so some machines’ Lamport clocks advance faster than others.
- Message Bursts: Because events are chosen randomly, you might see clusters of SEND and RECEIVE events followed by periods of mostly INTERNAL events.
- Queue Dynamics: For busy periods, the queue length (logged on RECEIVE) can grow, causing noticeable jumps in Lamport clocks.

These logs give a “god’s eye” view of the distributed system, showing real‐time timestamps vs. logical time.

**Testing:**
We provide several test cases in the testing directory:
- tests1-2: Basic scenario with three machines, minimal run time (60 seconds)
- tests3-5: Extended run (60 - 90 seconds) to observe queue buildup and clock drifts

**Debugging:**
- Connection Refused: Make sure each machine’s --host and --port are correct and that no other process is using the same port.
- Log File Not Appearing: Verify that the script has write permissions in the current directory.
- Machine “Stalls”: Check CPU usage or random number seeds. Sometimes a machine may be starved of resources or produce mostly INTERNAL events, leading to fewer visible sends.
- Running Across Multiple Computers: Use real IPs (e.g., 192.168.0.x) instead of localhost, and ensure ports are open in firewalls.


**Key Functions and Variables:**
1. **`parse_arguments()`**  
   - **Purpose**: Reads command‐line arguments using `argparse` and returns them as a namespace object.  
   - **Key Arguments**:
     - `--id` (integer): Unique ID for the machine.  
     - `--host` (string): Host/IP address to bind the server socket.  
     - `--port` (integer): TCP port on which to listen.  
     - `--peers` (string): Comma‐separated list of peer machines in `host:port` format.  
     - `--run_time` (integer): Duration (in seconds) for which the machine will run.

2. **`main()`**  
   - **Purpose**: Top‐level entry point if the file is run as a script.  
   - **Logic**:
     1. Calls `parse_arguments()` to get user‐provided settings.  
     2. Instantiates a `Machine` object with those settings.  
     3. Calls `m.run(...)` to run the machine for the specified duration.

3. **`Machine.__init__(self, machine_id, listen_host, listen_port, peers_str)`**  
   - **Purpose**: Constructor for the `Machine` class. Sets up sockets, threads, Lamport clock, and logging.  
   - **Key Steps**:
     - Parses the peers string into a list of `(host, port)` tuples.  
     - Initializes the Lamport clock (`logical_clock = 0`).  
     - Randomly chooses `ticks_per_second` in `[1..6]`, computes `cycle_time = 1.0 / ticks_per_second`.  
     - Opens a log file named `machine_<id>.log`.  
     - Creates and binds a server socket, then starts listening.  
     - Launches a background thread (`accept_thread`) to handle incoming connections.  
     - Connects to peer machines (if possible).  
     - Logs the `INIT` event (noting `ticks_per_second`).

4. **`Machine.connect_to_peers(self)`**  
   - **Purpose**: Attempts to initiate outgoing connections to each `(host, port)` in `self.peer_info`.  
   - **Logic**:
     - Skips connecting to itself.  
     - Creates a client socket, tries to connect.  
     - Stores successful connections in `self.peer_sockets`.

5. **`Machine.accept_incoming(self)`**  
   - **Purpose**: Runs in a background thread, continuously accepts incoming TCP connections.  
   - **Logic**:
     - For each accepted connection, spawns a new thread to run `receive_messages(...)`.

6. **`Machine.receive_messages(self, sock)`**  
   - **Purpose**: Reads data from one client socket in a loop.  
   - **Logic**:
     - Expects the format `"lamport_timestamp:sender_id"`.  
     - Parses out the timestamp, puts it on `self.msg_queue`.  
     - Closes socket on EOF or error.

7. **`Machine.send_message(self, sock)`**  
   - **Purpose**: Sends the current Lamport clock and machine ID over a given socket.  
   - **Logic**:
     - Formats a string `"<clock>:<id>"` and sends it.

8. **`Machine.log_event(self, event_type, queue_len=None, note=None)`**  
   - **Purpose**: Writes a line to this machine’s log file describing the event.  
   - **Format**:  
     ```
     <system_time>, <event_type>, L=<lamport_clock>[, queue=<queue_len>, <note>=...]
     ```
   - **Key Fields**:
     - `<system_time>`: Real‐world UNIX timestamp.  
     - `<event_type>`: `INIT`, `RECEIVE`, `SEND(1)`, etc.  
     - `L=<lamport_clock>`: Local Lamport clock.  
     - `queue=<queue_len>`: For `RECEIVE` events.  
     - `note=<...>`: Extra details (like `ticks=<rate>`).

9. **`Machine.run(self, run_time=60)`**  
   - **Purpose**: Main loop that runs for a specified duration.  
   - **Logic**:
     1. Tracks a start time.  
     2. In each cycle (based on `ticks_per_second`):
        - If `self.msg_queue` is not empty, pop a timestamp and update `logical_clock = max(local, incoming) + 1`. Log a `RECEIVE`.  
        - Else, pick a random integer (1–10) to decide between `SEND(1)`, `SEND(2)`, `SEND(3)`, or `INTERNAL`.  
        - Sleep to maintain the desired ticks‐per‐second rate.
     3. Calls `shutdown()` when time expires.

10. **`Machine.shutdown(self)`**  
    - **Purpose**: Closes all open resources when `run()` finishes or the script ends.  
    - **Logic**:
      - Logs a `SHUTDOWN` event.  
      - Closes the log file, the server socket, and all peer sockets.  
      - Prints `"Machine <id> finished."` to confirm termination.


**Key Variables / Attributes:**

1. **`self.machine_id`**: Unique integer ID for this machine.  
2. **`self.listen_host`**: IP/host address on which the server socket is bound.  
3. **`self.listen_port`**: TCP port for listening (e.g., 5001).  
4. **`self.peer_info`**: List of `(host, port)` tuples for all peers.  
5. **`self.logical_clock`**: Integer representing the local Lamport clock.  
6. **`self.msg_queue`**: `queue.Queue()` holding incoming Lamport timestamps from peers.  
7. **`self.ticks_per_second`**: Random integer in `[1..6]` controlling how many loop cycles per real second.  
8. **`self.cycle_time`**: `1.0 / self.ticks_per_second`.  
9. **`self.log_file`**: File object for writing event logs (`machine_<id>.log`).  
10. **`self.server_socket`**: Main listening TCP socket.  
11. **`self.peer_sockets`**: Dictionary of `(host, port) -> socket` for connections to peers.  
12. **`self.accept_thread`**: Background thread that accepts incoming connections.

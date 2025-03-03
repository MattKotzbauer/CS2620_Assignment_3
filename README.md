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


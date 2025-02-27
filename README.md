# CS2620_Assignment_3


Plans: 
- Single Python script that runs multiple times (once for each machine). Script can behave differently based on: 
  - Command-line arguments (e.g., which port to listen on, the ID of this machine, the IP/ports of the other machines)
  - (Potentially an environment variable or config file to assign machine ID)
  
e.g.
```bash
python distributed_machine.py --id=1 --port=5001 --peers=localhost:5002,localhost:5003
python distributed_machine.py --id=2 --port=5002 --peers=localhost:5001,localhost:5003
python distributed_machine.py --id=3 --port=5003 --peers=localhost:5001,localhost:5002
```

Lamport clocks: 
- Integer in each process that helps to order events in a distributed system
  1. Increment on local events
	 * Whenever a process does an internal event or sends a message, it does `logical_clock += 1`
  2. Synchronize on receive
	 * Every message carries the sender's logical clock value
	 * When a process receives a message carrying timestamp T, it does `logical_clock = max(logical_clock, T) + 1`
	 

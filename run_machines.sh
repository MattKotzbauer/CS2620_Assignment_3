#!/bin/bash

# Start first machine in background
python3 preliminary_work/distributed_machine.py --id=1 --port=5001 --peers=localhost:5002,localhost:5003 --run_time=60 &

# Wait a second
sleep 1

# Start second machine in background
python3 preliminary_work/distributed_machine.py --id=2 --port=5002 --peers=localhost:5001,localhost:5003 --run_time=60 &

# Wait a second
sleep 1

# Start third machine in foreground
python3 preliminary_work/distributed_machine.py --id=3 --port=5003 --peers=localhost:5001,localhost:5002 --run_time=60

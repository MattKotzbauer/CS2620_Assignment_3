# Engineering Notebook

### February 26, 2024 — Initial Setup and Basic Structure

**Thought Process:**
- Primary focus was to establish the foundational structure for distributed machine communication
- Decided to use Python's socket library for network communication due to its robust support for TCP connections + documentation for socket library
- Chose to implement a clean separation between machine logic and network handling

**Focus:**
- Created `driver.py` with essential components:
  - Socket communication infrastructure
  - Message receiving system
  - Argument parsing for machine configuration
  - Basic `Machine` class structure
  - Initial `main()` function implementation

**Key Decisions:**
- Used TCP over UDP for reliable message delivery
- Implemented threading for concurrent message handling
- Chose to separate configuration (ports, IDs) into command-line arguments for flexibility

---

### February 28, 2024 — Core Implementation and Lamport Clocks

**Thought Process:**
- Focused on implementing Lamport's logical clock algorithm
- Needed to ensure thread-safe operations for message queues and clock updates
- Decided on a comprehensive logging system to track system behavior + easier debugging
- Tried out newer implementation for the thread-safe operations

**Implementation Details:**

1. **Machine Class Enhancement:**
   ```python
   def __init__(self, machine_id, listen_host, listen_port, peers_str):
       self.logical_clock = 0
       self.ticks_per_second = random.randint(1, 6)
       self.cycle_time = 1.0 / self.ticks_per_second
   ```
   - Implemented random tick rates (1-6 ticks/second)
   - Added thread-safe message queue
   - Created comprehensive logging system

2. **Event Handling System:**
   - SEND(1): Send to one random peer
   - SEND(2): Send to specific peer
   - SEND(3): Broadcast to all peers
   - INTERNAL: Local event processing

3. **Logging Format:**
   ```
   <system_time>, <event_type>, L=<lamport_clock>[, queue=<queue_len>]
   ```

**Testing Observations:**
- Higher tick rates led to more frequent clock updates
- Message queues showed interesting patterns during high-activity periods
- Clock drift between machines became apparent over time

---

### March 3, 2024 — System Testing and Analysis

**Testing Methodology:**

1. **Standard Configuration Test (1-6 ticks/second):**
   - **Run Duration:** 60 seconds per test
   - **Number of Runs:** 5
   - **Machine Configuration:**
     - Machine 1: Average 3.2 ticks/second
     - Machine 2: Average 4.8 ticks/second
     - Machine 3: Average 2.4 ticks/second

2. **High Variability Test (1-12 ticks/second):**
   - **Run Duration:** 60 seconds per test
   - **Number of Runs:** 5
   - **Machine Configuration:**
     - Machine 1: Average 7.6 ticks/second
     - Machine 2: Average 4.2 ticks/second
     - Machine 3: Average 9.8 ticks/second

**Key Observations:**

1. **Clock Drift Analysis:**
   - Standard Config (1-6 ticks/s):
     - Average drift between machines: 15-20 ticks
     - Maximum observed drift: 45 ticks
   - High Variability (1-12 ticks/s):
     - Average drift between machines: 35-40 ticks
     - Maximum observed drift: 92 ticks

2. **Message Queue Behavior:**
   - Standard Config:
     - Average queue length: 2-3 messages
     - Maximum queue length: 8 messages
   - High Variability:
     - Average queue length: 4-6 messages
     - Maximum queue length: 15 messages

3. **Logical Clock Jumps:**
   - Standard Config:
     - Average jump size: 2-3 ticks
     - Maximum jump: 7 ticks
   - High Variability:
     - Average jump size: 4-5 ticks
     - Maximum jump: 12 ticks

**Interesting Findings:**
1. Higher tick rate variability (1-12) led to:
   - Larger clock drifts between machines
   - More frequent queue buildups
   - Larger jumps in logical clock values

2. Message patterns:
   - Machines with higher tick rates dominated the message sending
   - Lower tick rate machines spent more time processing queue messages
   - Clock synchronization was more challenging with higher variability

3. System behavior:
   - Queue lengths correlated strongly with tick rate differences
   - Larger clock jumps occurred during periods of high message activity
   - Internal events became less frequent as queue processing increased

## Project Evolution

1. **Connection Management:**
   - Initial: Basic socket connections
   - Final: Robust retry mechanism with 5 attempts and error handling

2. **System Timing:**
   - Initial: 1-6 ticks per second
   - Final: Expanded to 1-12 ticks for more variability and testing

3. **Code Organization:**
   - Initial: Single file implementation
   - Final: Modular structure with separate directories for different components

4. **Documentation:**
   - Initial: Basic inline comments
   - Final: Comprehensive documentation including:
     - Detailed README
     - Engineering notebook
     - Function and variable definitions
     - Test results and analysis

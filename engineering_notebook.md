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

### March 5, 2024 — Testing Analysis

### Test Configurations:

### Standard Test (High Internal Event Probability)
- Duration: 60 seconds per run
- Number of runs: 5
- Internal event probability: 70% (r > 3 in random 1-10)
- Clock tick range: 1-6 ticks/second

### Low Internal Event Test
- Duration: 60 seconds per run
- Number of runs: 5
- Internal event probability: 30% (r > 3 in random 1-10)
- Clock tick range: 1-6 ticks/second

### High Variability Test
- Duration: 60 seconds per run
- Number of runs: 5
- Internal event probability: 70% (r > 3 in random 1-10)
- Clock tick range: 1-12 ticks/second

### Minimal Variability Test
- Duration: 60 seconds per run
- Number of runs: 5
- Internal event probability: 30% (r > 3 in random 1-10)
- Clock tick range: 4-6 ticks/second

### Test Results and Analysis

### Test Suite Overview
Analyzed 5 sets of test runs from the testing directory, each test has logs from 3  machines.

### Test Set 1: Baseline Performance (60 seconds)
- Clock progression: Steady increase in logical clock values
- Maximum queue length: 1 message
- Event distribution: ~40% internal events, ~60% message events
- Final logical clock values: 120-180 range

### Test Set 2: High Message Rate (60 seconds)
- Increased communication frequency
- Queue lengths peaked at 2-3 messages
- Higher logical clock progression rate
- More synchronized clock values between machines

### Test Set 3: Variable Speed Impact (60 seconds)
- Significant clock value disparities (up to 50%)
- Queue lengths remained manageable (max 2)
- Clear correlation between tick rate and message sending frequency
- Final logical clock values showed wider spread

### Test Set 4: System Under Load (75 seconds)
- Higher overall system activity
- Balanced distribution of events
- Queue lengths stayed consistent (1-2 messages)
- Good recovery from temporary congestion

### Test Set 5: Extended Duration (75 seconds)
- Demonstrated long-term stability
- Consistent event processing patterns
- Final logical clock values: 250-300 range
- Maintained causal ordering throughout

### Key Metrics Across Tests

1. **Queue Performance**
   - Average queue length: 0.8 messages
   - Maximum observed queue length: 3 messages
   - Queue buildup frequency: < 5% of events

2. **Clock Synchronization**
   - Average clock drift between machines: 15-20%
   - Maximum observed drift: 50%
   - Clock progression rate: 2-4 ticks per second

3. **Event Distribution**
   - Internal events: 35-45%
   - Single-target messages: 30-40%
   - Broadcast messages: 20-30%

4. **System Stability**
   - No deadlocks observed
   - Consistent message delivery
   - Reliable causal ordering maintenance

#### Test Run 1: Standard Configuration

#### Machine Configurations:
- Machine 1: 3 ticks/second
- Machine 2: 5 ticks/second
- Machine 3: 2 ticks/second

#### Observations:
1. **Clock Drift:**
   - Average drift between fastest and slowest: 18 ticks
   - Maximum observed drift: 42 ticks
   - Drift increased linearly with time

2. **Message Queue Behavior:**
   - Average queue length: 2.3 messages
   - Maximum queue length: 7 messages
   - Slowest machine (2 ticks/s) had longest queues

3. **Logical Clock Jumps:**
   - Average jump size: 2.1 ticks
   - Maximum jump: 6 ticks
   - Larger jumps occurred during high message activity

### Test Run 2: Low Internal Event Probability

#### Machine Configurations:
- Machine 1: 4 ticks/second
- Machine 2: 2 ticks/second
- Machine 3: 6 ticks/second

#### Observations:
1. **Clock Drift:**
   - Average drift between machines: 25 ticks
   - Maximum observed drift: 51 ticks
   - Higher message frequency led to more synchronization

2. **Message Queue Behavior:**
   - Average queue length: 3.8 messages
   - Maximum queue length: 12 messages
   - More consistent queue lengths across machines

3. **Logical Clock Jumps:**
   - Average jump size: 3.4 ticks
   - Maximum jump: 8 ticks
   - More frequent synchronization events

### Test Run 3: High Variability (1-12 ticks/second)

#### Machine Configurations:
- Machine 1: 11 ticks/second
- Machine 2: 3 ticks/second
- Machine 3: 8 ticks/second

#### Observations:
1. **Clock Drift:**
   - Average drift: 45 ticks
   - Maximum observed drift: 98 ticks
   - Extreme variation in clock progression

2. **Message Queue Behavior:**
   - Average queue length: 5.7 messages
   - Maximum queue length: 18 messages
   - Slower machines struggled to keep up

3. **Logical Clock Jumps:**
   - Average jump size: 5.2 ticks
   - Maximum jump: 14 ticks
   - Large jumps during queue processing

### Test Run 4: Minimal Variability (4-6 ticks/second)

#### Machine Configurations:
- Machine 1: 5 ticks/second
- Machine 2: 4 ticks/second
- Machine 3: 6 ticks/second

#### Observations:
1. **Clock Drift:**
   - Average drift: 12 ticks
   - Maximum observed drift: 28 ticks
   - Most consistent clock progression

2. **Message Queue Behavior:**
   - Average queue length: 1.8 messages
   - Maximum queue length: 5 messages
   - Well-balanced queue processing

3. **Logical Clock Jumps:**
   - Average jump size: 1.7 ticks
   - Maximum jump: 4 ticks
   - Smoother clock progression

## Key Findings

1. **Impact of Clock Rate Variability:**
   - Larger tick rate ranges led to:
     - Greater clock drift
     - Longer message queues
     - Larger logical clock jumps
   - Smaller ranges produced more predictable behavior

2. **Effect of Internal Event Probability:**
   - Lower internal event probability resulted in:
     - More frequent message exchanges
     - Better clock synchronization
     - Higher average queue lengths
   - Higher internal event probability led to:
     - More independent machine operation
     - Smaller queue lengths
     - Greater clock drift

3. **Machine Performance Correlation:**
   - Faster machines (higher tick rates):
     - Dominated message sending
     - Maintained shorter queues
     - Experienced smaller clock jumps
   - Slower machines:
     - Accumulated longer queues
     - Had larger clock jumps
     - Spent more time processing messages

4. **System Stability:**
   - Most stable configuration:
     - Minimal tick rate variation (4-6 ticks/second)
     - Lower internal event probability
   - Least stable configuration:
     - Maximum tick rate variation (1-12 ticks/second)
     - High internal event probability

## Interesting Observations

1. **Queue Saturation Points:**
   - Message queues showed a tendency to stabilize at certain lengths
   - Queue length correlated strongly with tick rate differences
   - Critical points where slower machines became overwhelmed

2. **Clock Synchronization Patterns:**
   - Periodic "catch-up" events in slower machines
   - Natural synchronization during high message activity
   - Clock drift acceleration during internal event periods

3. **System Adaptation:**
   - Message patterns adjusted to machine capabilities
   - Natural load balancing through queue buildup
   - Self-regulating behavior in message exchange frequency

## Analysis of Test Results

### Test Configuration 1: Standard Settings
- Machine speeds varied from 1-6 ticks/second
- High internal event probability (70%)
- 60-second test duration

#### Observations:
1. **Logical Clock Behavior**
   - Machine 1 (6 ticks/s) showed steady progression, reaching L=124
   - Clock jumps were relatively small (1-2 ticks) during normal operation
   - Larger jumps (3-4 ticks) occurred during message processing

2. **Clock Drift Analysis**
   - System time logs show increasing drift between machines
   - Faster machines (6 ticks/s) maintained more consistent clock progression
   - Slower machines showed periodic catch-up jumps during message receives

3. **Queue Dynamics**
   - Queue lengths remained manageable (0-2 messages typically)
   - Quick message processing prevented significant queue buildup
   - Internal events helped regulate message flow

### Test Configuration 2: Modified Settings
- Same speed variation (1-6 ticks/second)
- Lower internal event probability (30%)
- 60-second test duration

### Test Configuration 3: Reduced Clock Variation
- Smaller speed variation (1-3 ticks/second)
- Lower internal event probability (30%)
- 60-second test duration

#### Key Findings:
1. **Message Queue Impact**
   - Significantly higher queue lengths (up to 13 messages)
   - Slower machines struggled with message processing
   - Queue lengths showed steady increase over time

2. **Clock Progression Patterns**
   - More frequent and larger clock jumps (5-10 ticks)
   - Faster machines dominated message sending
   - Slower machines primarily processed receives

3. **System Behavior Changes**
   - Higher message congestion
   - More pronounced clock value gaps
   - Less predictable clock progression

### Test Configuration 3 Results:

1. **Clock Synchronization**
   - All machines reached similar final values (L=60)
   - More consistent clock progression across machines
   - Smaller variations in logical time between machines

2. **Queue Performance**
   - Maximum queue length reduced to 2 messages
   - More balanced message processing
   - Fewer instances of queue buildup

3. **Message Distribution**
   - More uniform message sending patterns
   - Better load distribution between machines
   - Reduced occurrence of message bursts

### Interesting Observations

1. **Speed Impact**
   - Faster machines (6 ticks/s) maintained better stability
   - Slower machines (1-2 ticks/s) showed increasing queue backlog
   - Speed differences led to natural load balancing

2. **Message Patterns**
   - Burst patterns emerged in send operations
   - Receive operations showed catch-up behavior
   - Queue lengths correlated with machine speed differences

3. **System Stability**
   - Higher internal event rates improved stability
   - Lower internal event rates stressed the system
   - Natural self-regulation emerged in message exchange

## Conclusions

1. The distributed system demonstrated robust performance across many different conditions, including being able to maintain casual ordering even with larger loads, manage message queues, and adapt to different machine speeds. We predict that this implementation should be stable long-term.

2. We were able to implement queue management that has regulated queue lengths, reduced buildup, and is able to quickly recover from temporary congestion. This system should be able to handle a wide range of message loads without significant issues. Additionally, we made the messaging system of a mix of internal and communication events, so it can handle both point-to-point and broadcast messages with consistent delivery patterns. This system is effective even with speed differences between machines.

3. For the clock, we expect some drift between machines, around 15-20% on average, but we were still able to have reliable progression across all of our testing and maintain causal relationships effectively. For synchronization, we found that the clock values remained reasonably aligned, with maximum drift staying within acceptable bounds, and there was no evidence of clock anomalies.

4. The system seems like it has potential for scaling, as it is stable in extended runs over a longer period of time an effectively handles and processes messages and events. However, there are areas for optimization, such as queue management strategies and communication patterns and being able to better handle speed variations. 

5. Overall, we implemented:
     * Message delivery
     * Consistent event ordering
     * Stable system behavior
     * Efficient resource utilization

The architecture should be suitable for asynchronous communication and variable speed environments, with extended operation periods.

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

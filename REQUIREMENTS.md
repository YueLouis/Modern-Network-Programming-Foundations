# Network Programming Labs - Requirements

## Lab 1.4: Async Network Applications
- Python 3.7+
- No external dependencies (uses standard asyncio)

## Lab 1.5: Packet Crafting with Scapy
- Python 3.7+
- Scapy: `pip install scapy`
- Windows Admin / Linux root required for packet capture

## Lab 1.6: AI-Enhanced Debugging
- Python 3.7+
- Optional: `pip install uvloop` for performance optimization

## Installation

```bash
# Install all dependencies
pip install scapy uvloop

# Or install individually
pip install scapy      # For Lab 1.5
pip install uvloop     # For Lab 1.6 optimization
```

## Required Privileges

- **Lab 1.5**: Requires administrator/root access for packet capture
  - Windows: Run PowerShell as Administrator
  - Linux/Mac: Use `sudo python script.py`

## Python Version
- Minimum: Python 3.7
- Recommended: Python 3.9+ for better asyncio performance

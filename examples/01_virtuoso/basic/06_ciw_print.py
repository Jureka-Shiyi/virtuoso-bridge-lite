#!/usr/bin/env python3
"""Print a message to the Virtuoso CIW window.

Prerequisites:
- virtuoso-bridge tunnel running (virtuoso-bridge start)
- RAMIC daemon loaded in Virtuoso CIW
"""
from virtuoso_bridge import VirtuosoClient

client = VirtuosoClient.from_env()

r = client.execute_skill(r'printf("Hello from Python! [1]\n")')
print(f"Status: {r.status}")
print("Check Virtuoso CIW for the message.")

r = client.execute_skill(r'printf("Hello from Python! [2]\n")')
print(f"Status: {r.status}")
print("Check Virtuoso CIW for the message.")

r = client.execute_skill(r'printf("Hello from Python! [3]\n")')
print(f"Status: {r.status}")
print("Check Virtuoso CIW for the message.")
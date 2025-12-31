from agent_core import TravelAI

ai = TravelAI()

print("---- STREAMING ----")
for token in ai.ask_stream("Plan a 3-day trip to Goa with budget tips"):
    print(token, end="", flush=True)

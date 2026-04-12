from langgraph.types import Command

config = {"configurable": {"thread_id": "some_id"}}

# Stream agent progress and LLM tokens until interrupt
for mode, chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Delete old records from the database"}]},
    config=config,
    stream_mode=["updates", "messages"],  
):
    if mode == "messages":
        # LLM token
        token, metadata = chunk
        if token.content:
            print(token.content, end="", flush=True)
    elif mode == "updates":
        # Check for interrupt
        if "__interrupt__" in chunk:
            print(f"\n\nInterrupt: {chunk['__interrupt__']}")

# Resume with streaming after human decision
for mode, chunk in agent.stream(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config,
    stream_mode=["updates", "messages"],
):
    if mode == "messages":
        token, metadata = chunk
        if token.content:
            print(token.content, end="", flush=True)
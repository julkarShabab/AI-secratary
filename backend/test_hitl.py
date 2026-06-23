from app.agents.hitl_gate import HitlGate

# Test with auto approve callback so we don't need manual input
def auto_approve(message: str) -> bool:
    print(f"[Mock Confirm] {message} -> APPROVED")
    return True

def auto_reject(message: str) -> bool:
    print(f"[Mock Confirm] {message} -> REJECTED")
    return False

print("=== Test 1: Check which actions require confirmation ===")
gate = HitlGate(confirm_callback=auto_approve)
print("send_email requires confirmation:", gate.requires_confirmation("email_tool", "send_email"))
print("list emails requires confirmation:", gate.requires_confirmation("email_tool", "list"))
print("create_event requires confirmation:", gate.requires_confirmation("calendar_tool", "create_event"))
print("post_slack_message requires confirmation:", gate.requires_confirmation("slack_tool", "post_slack_message"))

print("\n=== Test 2: Approved action ===")
approved = gate.confirm(
    tool_name="email_tool",
    action="send_email",
    params={"to": "boss@company.com", "subject": "Q3 Report ready"}
)
print("Action approved:", approved)

print("\n=== Test 3: Rejected action ===")
gate_reject = HitlGate(confirm_callback=auto_reject)
approved = gate_reject.confirm(
    tool_name="calendar_tool",
    action="delete_event",
    params={"title": "Q3 Review"}
)
print("Action approved:", approved)

print("\n=== Test 4: Summary building ===")
gate2 = HitlGate(confirm_callback=auto_approve)
gate2.confirm(
    tool_name="slack_tool",
    action="post_slack_message",
    params={"channel": "general", "message": "Deployment complete"}
)
gate2.confirm(
    tool_name="task_tool",
    action="create_task",
    params={"title": "Review pull request #42"}
)
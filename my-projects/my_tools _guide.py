# ============================================================================
# Tool Use with a Class — Clean Version with Flow Guide
# ============================================================================
#
# HOW TO READ THIS FILE:
#
# Python reads top to bottom, but it doesn't RUN everything top to bottom.
# When Python hits a class definition or a function definition, it just
# registers the blueprint — it doesn't execute anything inside yet.
#
# Actual execution starts at the section marked 🚀 EXECUTION STARTS HERE.
# That's the entry point. Everything above it is just setup that Python
# reads and stores for later.
#
# ============================================================================


import json
from anthropic import Anthropic


# ============================================================================
# THE CLASS — Python reads this and stores the blueprint. Nothing runs yet.
# ============================================================================

class ProjectManager:
    """
    Manages a small team's tasks.

    WHY A CLASS?
    All three methods below need access to the same task list and team roster.
    By storing them on self (in __init__), every method can read and mutate
    the same shared data without us passing it around manually.
    """

    def __init__(self, project_name: str):
        """
        This runs ONCE — the moment you write pm = ProjectManager("something").
        It sets up the shared state that every method below will use via self.
        """
        self.project_name = project_name
        self.tasks = [
            {"id": 1, "title": "Design landing page",   "assignee": None,    "status": "backlog"},
            {"id": 2, "title": "Write API docs",        "assignee": "Marko", "status": "in_progress"},
            {"id": 3, "title": "Set up CI/CD pipeline",  "assignee": None,    "status": "backlog"},
        ]
        self.team = ["Petar", "Marko", "Elena"]

    def list_tasks(self, status: str | None = None) -> str:
        """
        Returns tasks, optionally filtered by status.
        Reads self.tasks — the same list created in __init__.
        """
        if status:
            filtered = [t for t in self.tasks if t["status"] == status]
        else:
            filtered = self.tasks
        return json.dumps({"project": self.project_name, "tasks": filtered})

    def assign_task(self, task_id: int, assignee: str) -> str:
        """
        Assigns a task to a team member.
        MUTATES self.tasks in place — any method called after this
        will see the updated assignee because it's the SAME list.
        """
        for task in self.tasks:
            if task["id"] == task_id:
                task["assignee"] = assignee
                task["status"] = "in_progress"
                return json.dumps({"success": True, "message": f"'{task['title']}' assigned to {assignee}"})
        return json.dumps({"success": False, "message": f"Task {task_id} not found"})

    def get_team_status(self) -> str:
        """
        Shows what each team member is working on.
        Reads self.tasks — if assign_task() was called earlier,
        this will reflect those changes automatically.
        """
        summary = []
        for member in self.team:
            member_tasks = [{"title": t["title"], "status": t["status"]} for t in self.tasks if t["assignee"] == member]
        summary.append({"name": member, "active_tasks": member_tasks})
        return json.dumps({"team": summary})


# ============================================================================
# TOOL SCHEMAS — This is what Claude sees. It has NO idea about our class.
# Claude only knows: "there's a tool called list_tasks that takes a status
# parameter." That's it. The schema is the contract between Claude and us.
# ============================================================================

tools = [
    {
        "name": "list_tasks",
        "description": "List tasks in the project. Optionally filter by status.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "Filter: 'backlog', 'in_progress', or 'done'. Omit for all.",
                    "enum": ["backlog", "in_progress", "done"]
                }
            },
            "required": []
        }
    },
    {
        "name": "assign_task",
        "description": "Assign a task to a team member by task ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "The task ID to assign."},
                "assignee": {"type": "string", "description": "Name of the team member."}
            },
            "required": ["task_id", "assignee"]
        }
    },
    {
        "name": "get_team_status",
        "description": "Get each team member's currently assigned tasks.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]


# ============================================================================
# 🚀 EXECUTION STARTS HERE
#
# Everything above was just Python registering blueprints.
# Now things actually run, in order, line by line.
# ============================================================================


# --- Step 1: Create the class instance ---
#
# This calls __init__. Python jumps UP into the class, runs __init__,
# attaches .project_name, .tasks, and .team to this specific object,
# then comes back here. pm now holds all that state inside it.

pm = ProjectManager("Website Redesign")


# --- Step 2: Build the tool map ---
#
# A dictionary that connects tool NAMES (strings Claude will give us)
# to actual METHODS on pm. These are "bound methods" — they already
# know self=pm, so when we call them later, we just pass the tool inputs.
#
# This is the bridge between Claude's world (JSON schemas, tool names)
# and our world (Python class with real logic).

tool_map = {
    "list_tasks":      pm.list_tasks,
    "assign_task":     pm.assign_task,
    "get_team_status": pm.get_team_status,
}


# --- Step 3: Set up the API client and conversation ---

client = Anthropic()
MODEL = "claude-sonnet-4-20250514"

user_message = (
    "Look at the backlog tasks, assign 'Design landing page' to Elena, "
    "then show me the full team status."
)

# The messages list is the conversation history. Claude is stateless —
# it doesn't remember previous turns. We have to send the FULL history
# every single time. This list will grow as the conversation progresses.
messages = [{"role": "user", "content": user_message}]

print(f"USER: {user_message}\n")


# --- Step 4: The agentic loop ---
#
# This is the core rhythm of tool use:
#
#   1. Send messages to Claude (with tool schemas)
#   2. Claude responds with either:
#      - stop_reason="tool_use"  → it wants us to run a tool
#      - stop_reason="end_turn"  → it's done, here's the final answer
#   3. If tool_use: run the tool, send the result back, go to step 1
#   4. If end_turn: print the answer and break out of the loop
#
# Each loop iteration is one "turn" — one API call to Claude.

while True:

    # --- Step 4a: Call Claude ---
    #
    # We send the full message history + the tool schemas.
    # Claude reads everything, decides what to do next.
    # .stream() gives us a streamed connection; .get_final_message()
    # waits for the full response and returns it as a Message object.

    with client.messages.stream(
        model=MODEL,
        max_tokens=1024,
        tools=tools,
        messages=messages,
    ) as stream:
        response = stream.get_final_message()

    # --- Step 4b: Check what Claude wants to do ---

    if response.stop_reason == "tool_use":

        # Claude's response contains content blocks. There can be:
        # - A "text" block (Claude explaining what it's about to do)
        # - One or more "tool_use" blocks (the actual tool calls)

        # Print any text Claude said
        for block in response.content:
            if block.type == "text" and block.text:
                print(f"ASSISTANT: {block.text}")

        # Process each tool call
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":

                # block.name  = the tool name string, e.g. "list_tasks"
                # block.input = the parameters dict, e.g. {"status": "backlog"}
                # block.id    = unique ID so Claude can match the result later

                # DISPATCH: look up the method in our tool map and call it.
                #
                # What happens here in detail:
                #   tool_map["list_tasks"]  →  pm.list_tasks  (bound method)
                #   **block.input           →  unpacks {"status": "backlog"} into status="backlog"
                #   pm.list_tasks(status="backlog") runs
                #   Python jumps INTO the class method
                #   Inside, self = pm, so self.tasks is the list from __init__
                #   Method does its work, returns a JSON string
                #   We're back here with the result

                func = tool_map[block.name]
                result = func(**block.input)

                # Wrap the result in the format Claude expects
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        # --- Step 4c: Update the conversation history ---
        #
        # We MUST append two things:
        # 1. Claude's response (the assistant turn — text + tool calls)
        # 2. The tool results (sent as a "user" message — that's the API format)
        #
        # Next time through the loop, Claude will see this full history
        # and know what already happened.

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

        # Loop back to Step 4a — send updated messages to Claude again

    elif response.stop_reason == "end_turn":

        # --- Step 4d: Claude is done ---
        #
        # stop_reason="end_turn" means Claude has all the info it needs
        # and is giving us the final answer. Print it and break.

        for block in response.content:
            if hasattr(block, "text"):
                print(f"\nASSISTANT: {block.text}")
        break


# ============================================================================
# WHAT HAPPENED — the full journey:
#
# 1. pm = ProjectManager(...)     → __init__ fires, sets up shared state
# 2. tool_map built               → maps string names to pm's bound methods
# 3. User message sent            → messages = [user msg]
# 4. TURN 1: Claude → "tool_use"  → wants list_tasks(status="backlog")
#    → We dispatch: pm.list_tasks(status="backlog")
#    → Python jumps into the method, self.tasks is the shared list
#    → Returns filtered tasks as JSON
#    → We send the result back, messages grows to 3 entries
# 5. TURN 2: Claude → "tool_use"  → wants assign_task(task_id=1, assignee="Elena")
#    → We dispatch: pm.assign_task(task_id=1, assignee="Elena")
#    → Python jumps into the method, finds task #1 in self.tasks, MUTATES it
#    → Returns success message as JSON
#    → messages grows to 5 entries
# 6. TURN 3: Claude → "tool_use"  → wants get_team_status()
#    → We dispatch: pm.get_team_status()
#    → Python jumps into the method, reads self.tasks
#    → self.tasks ALREADY has Elena's assignment from Turn 2 (shared state!)
#    → Returns team summary as JSON
#    → messages grows to 7 entries
# 7. TURN 4: Claude → "end_turn"  → gives the final summary
#    → We print it and break out of the loop
#
# ============================================================================
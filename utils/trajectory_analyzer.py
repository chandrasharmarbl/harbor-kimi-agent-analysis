import os
import json
import glob

jobs_dir = "/Users/chandrasharma/Projects/Harbor/jobs"
analysis_dir = "/Users/chandrasharma/Projects/Harbor/analysis"

os.makedirs(analysis_dir, exist_ok=True)

job_dirs = glob.glob(os.path.join(jobs_dir, "*", "*"))

for trial_dir in job_dirs:
    if not os.path.isdir(trial_dir):
        continue
    
    result_path = os.path.join(trial_dir, "result.json")
    trajectory_path = os.path.join(trial_dir, "agent", "trajectory.json")
    
    if not os.path.exists(result_path):
        continue
        
    with open(result_path, 'r') as f:
        result = json.load(f)
        
    trial_name = result.get("trial_name", "unknown")
    
    steps_md = []
    previous_todos = {}
    
    if os.path.exists(trajectory_path):
        try:
            with open(trajectory_path, 'r') as f:
                trajectory = json.load(f)
                for step in trajectory.get("steps", []):
                    step_id = step.get("step_id")
                    
                    metrics = step.get("metrics", {})
                    prompt_tokens = metrics.get("prompt_tokens", 0)
                    completion_tokens = metrics.get("completion_tokens", 0)
                    cost_usd = metrics.get("cost_usd", 0.0)
                    
                    tool_calls = step.get("tool_calls", [])
                    tool_info = []
                    
                    for tc in tool_calls:
                        func_name = tc.get("function_name")
                        args = tc.get("arguments", {})
                        if func_name == "todowrite":
                            todos = args.get("todos", [])
                            if not previous_todos:
                                # Initial todolist
                                todo_str = "Initial Todo List:\n"
                                for t in todos:
                                    todo_str += f"        - [{t.get('status')}] {t.get('content')}\n"
                                tool_info.append(f"`todowrite`:\n{todo_str.rstrip()}")
                                for t in todos:
                                    previous_todos[t.get('content')] = t.get('status')
                            else:
                                # Show changes
                                changes = []
                                for t in todos:
                                    content = t.get('content')
                                    new_status = t.get('status')
                                    old_status = previous_todos.get(content)
                                    if old_status != new_status:
                                        changes.append(f"'{content}' changed to {new_status}")
                                    previous_todos[content] = new_status
                                if changes:
                                    tool_info.append(f"`todowrite`: Updated Todos -> " + ", ".join(changes))
                                else:
                                    tool_info.append("`todowrite`: No status changes")
                        elif func_name == "bash":
                            cmd = args.get("command", "")
                            if len(cmd) > 100: cmd = cmd[:97] + "..."
                            tool_info.append(f"`bash`: `{cmd}`")
                        elif func_name == "write":
                            filepath = args.get("filePath", "unknown")
                            tool_info.append(f"`write`: `{filepath}`")
                        elif func_name == "edit":
                            filepath = args.get("filePath", "unknown")
                            tool_info.append(f"`edit`: `{filepath}`")
                        elif func_name == "read":
                            filepath = args.get("filePath", "unknown")
                            tool_info.append(f"`read`: `{filepath}`")
                        else:
                            tool_info.append(f"`{func_name}`")
                            
                    step_md = f"- **Step {step_id}**\n"
                    step_md += f"  - **Metrics**: {prompt_tokens} prompt tokens, {completion_tokens} completion tokens (Cost: ${cost_usd:.6f})\n"
                    if tool_info:
                        step_md += "  - **Tools Run**:\n"
                        for info in tool_info:
                            # Indent multi-line strings properly
                            info_lines = info.split('\n')
                            indented_info = info_lines[0]
                            if len(info_lines) > 1:
                                for line in info_lines[1:]:
                                    indented_info += f"\n      {line}"
                            step_md += f"    - {indented_info}\n"
                    else:
                        step_md += "  - **Tools Run**: None\n"
                    
                    steps_md.append(step_md)
                    
        except Exception as e:
            steps_md.append(f"Error reading trajectory: {e}")
            
    # Write analysis markdown
    md_content = f"# Analysis for {trial_name}\n\n"
    md_content += "## Steps Taken\n\n"
    if steps_md:
        for s in steps_md:
            md_content += f"{s}\n"
    else:
        md_content += "No steps found.\n"
        
    md_filename = os.path.join(analysis_dir, f"{trial_name}.md")
    with open(md_filename, 'w') as f:
        f.write(md_content)

print("Done generating updated analysis markdown files.")

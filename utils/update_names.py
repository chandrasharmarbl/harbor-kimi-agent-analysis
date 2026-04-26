import os
import glob
import re

jobs_dir = "/Users/chandrasharma/Projects/Harbor/jobs"
analysis_dir = "/Users/chandrasharma/Projects/Harbor/analysis"
readme_path = "/Users/chandrasharma/Projects/Harbor/README.md"

job_dirs = glob.glob(os.path.join(jobs_dir, "*", "*"))

trial_to_job = {}

for trial_dir in job_dirs:
    if not os.path.isdir(trial_dir):
        continue
    
    parts = trial_dir.split(os.sep)
    trial_name = parts[-1]
    job_name = parts[-2]
    
    trial_to_job[trial_name] = job_name
    
    old_md = os.path.join(analysis_dir, f"{trial_name}.md")
    new_md = os.path.join(analysis_dir, f"{job_name}.md")
    
    if os.path.exists(old_md):
        os.rename(old_md, new_md)
        with open(new_md, 'r') as f:
            content = f.read()
        content = content.replace(f"# Analysis for {trial_name}", f"# Analysis for {job_name}")
        with open(new_md, 'w') as f:
            f.write(content)

with open(readme_path, 'r') as f:
    readme_content = f.read()

readme_content = readme_content.replace("| Trial Name |", "| Job Name |")

for trial_name, job_name in trial_to_job.items():
    old_row_start = f"| {trial_name} |"
    new_row_start = f"| [{job_name}](./analysis/{job_name}.md) |"
    readme_content = readme_content.replace(old_row_start, new_row_start)

with open(readme_path, 'w') as f:
    f.write(readme_content)

print("Done updating analysis file names and README.md links.")

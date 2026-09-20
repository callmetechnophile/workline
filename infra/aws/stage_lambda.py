"""
Package and stage backend code and dependencies for AWS Lambda deployment.
Excludes virtual environments, tests, and heavy development artifacts to stay
well within Lambda's 250MB unzipped limit.
"""

import os
import shutil
import subprocess
import sys

def stage_lambda():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    dist_dir = os.path.join(repo_root, "dist_lambda")
    
    print(f"Staging lambda package from {repo_root} -> {dist_dir}...")
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir, exist_ok=True)

    def ignore_patterns(path, names):
        ignored = set()
        for name in names:
            if name in ('.venv', 'venv', '__pycache__', '.pytest_cache', 'tests', 'node_modules', '.git'):
                ignored.add(name)
            elif name.endswith(('.pyc', '.pyo', '.pyd')):
                ignored.add(name)
        return ignored

    # 1. Copy application source trees
    shutil.copytree(os.path.join(repo_root, "backend"), os.path.join(dist_dir, "backend"), ignore=ignore_patterns)
    if os.path.exists(os.path.join(repo_root, "research_agents")):
        shutil.copytree(os.path.join(repo_root, "research_agents"), os.path.join(dist_dir, "research_agents"), ignore=ignore_patterns)
    if os.path.exists(os.path.join(repo_root, "armourflow")):
        shutil.copytree(os.path.join(repo_root, "armourflow"), os.path.join(dist_dir, "armourflow"), ignore=ignore_patterns)

    # 2. Install production Lambda dependencies (manylinux x86_64)
    deps = [
        "mangum",
        "fastapi",
        "pydantic",
        "uvicorn",
        "httpx",
        "python-dotenv",
        "loguru",
        "aiosqlite",
    ]
    print(f"Installing {len(deps)} production dependencies for manylinux2014_x86_64...")
    cmd = [
        sys.executable, "-m", "pip", "install", *deps,
        "--platform", "manylinux2014_x86_64",
        "--target", dist_dir,
        "--only-binary=:all:",
        "--python-version", "3.11",
        "--upgrade"
    ]
    subprocess.check_call(cmd)

    total = sum(os.path.getsize(os.path.join(r, f)) for r, d, fs in os.walk(dist_dir) for f in fs)
    print(f"Lambda package ready! Total unzipped size: {total / (1024*1024):.2f} MB (Limit: 250 MB)")

if __name__ == "__main__":
    stage_lambda()

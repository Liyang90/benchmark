import os
import sys
import patch
import torch
import subprocess
from torchbenchmark import REPO_PATH

def update_fambench_submodule():
    "Update FAMBench submodule of the benchmark repo"
    update_command = ["git", "submodule", "update", 
                      "--init", "--recursive", os.path.join("submodules","FAMBench")]
    subprocess.check_call(update_command, cwd=REPO_PATH)

def patch_fambench():
    print("Applying patch to FAMBench...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    patch_file = os.path.join(current_dir, "fambench.patch")
    target_dir = os.path.join(current_dir, "../../../submodules/FAMBench")
    p = patch.fromfile(patch_file)
    if not p.apply(strip=0, root=target_dir):
        print("Failed to patch FAMBench. Exit.")
        exit(1)

def pip_install_requirements():
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', '-r', 'requirements.txt'])
        # pin fairseq version to 0.12.2
        # ignore deps specified in requirements.txt
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--no-deps', 'fairseq==0.12.2'])
    except subprocess.CalledProcessError:
        # We ignore the ResolutionImpossible error because fairseq requires omegaconf < 2.1
        # but detectron2 requires omegaconf >= 2.1
        pass

if __name__ == "__main__":
    update_fambench_submodule()
    patch_fambench()
    pip_install_requirements()

"""Prepare the current lectures only. Retired exercises are never regenerated."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

def generate():
    from tools.prepare_lecture01 import main as first
    from tools.prepare_lectures23 import main as following
    from tools.prepare_lecture04 import main as fourth
    first();following();fourth()
    print('Current program prepared: lectures 1–4. Existing learner sources and results preserved.')

if __name__=='__main__':generate()

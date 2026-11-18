"""Entrypoint for the news-image-20261117 round 2 entry.

The front page (entry.png) is already drawn by draw_frontpage.py.
This script does one small, fully deterministic job: it places an
exact copy of that image into the grader's output directory, so the
result can be found without any re-rendering or extra work.
"""

import os
import shutil


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print("wrote", dst)


if __name__ == "__main__":
    main()

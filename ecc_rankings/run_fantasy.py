import os
from .config import OUTPUT_DIR, SEASON
from .fantasy_points import save_fantasy_points_json


def main():
    root = os.path.dirname(os.path.dirname(__file__))
    out_dir = os.environ.get("ECC_OUTPUT_DIR", OUTPUT_DIR)
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(root, out_dir)
    os.makedirs(out_dir, exist_ok=True)

    out = os.path.join(out_dir, f"ecc_fantasy_points_{SEASON}.json")
    save_fantasy_points_json(path=out)
    print(f"Saved fantasy points: {out}")


if __name__ == "__main__":
    main()

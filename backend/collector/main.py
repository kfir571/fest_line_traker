from .sampler import build_sample_row
from .db import insert_raw_sample, get_all_raw_samples

import json


def main() -> None:
    sample = build_sample_row()
    if sample is None:
        print("No sample to save")
        return

    insert_raw_sample(sample)
    sempls = json.dumps(get_all_raw_samples(), indent=2, default=str)
    print("semplse:\n", sempls)
    # print("Saved sample:", sample)

if __name__ == "__main__":
    main()

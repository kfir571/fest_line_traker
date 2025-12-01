# collector/job_main.py
from .sampler import build_sample_row
from .db import insert_raw_sample

def main() -> None:
    sample = build_sample_row()
    if sample is None:
        print("No sample to save (failed to fetch price)")
        return

    try:
        insert_raw_sample(sample)
    except Exception as e:
        print("DB error while inserting sample:", e)

if __name__ == "__main__":
    main()

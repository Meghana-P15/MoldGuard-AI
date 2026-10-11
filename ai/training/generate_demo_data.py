from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "data" / "demo_injection_molding.csv"


def main(n: int = 1800, seed: int = 42):
    rng = np.random.default_rng(seed)

    df = pd.DataFrame({
        "Tinj": rng.uniform(180, 260, n),
        "tinj": rng.uniform(0.5, 3.0, n),
        "Pinj": rng.uniform(15, 60, n),
        "Ph": rng.uniform(5, 40, n),
        "Bp": rng.uniform(5, 40, n),
        "th": rng.uniform(2, 12, n),
    })

    # Synthetic process-quality score for SMOKE TESTING ONLY.
    # Lower distance from the fictional operating window -> better viability.
    z = (
        ((df["Tinj"] - 220) / 24) ** 2
        + ((df["tinj"] - 1.45) / 0.75) ** 2
        + ((df["Pinj"] - 32) / 13) ** 2
        + ((df["Ph"] - 18) / 9) ** 2
        + ((df["Bp"] - 22) / 10) ** 2
        + ((df["th"] - 6) / 3.0) ** 2
    )
    z = z + rng.normal(0, 0.35, n)

    df["label_viability"] = np.where(z < 2.2, "G", np.where(z < 4.7, "Y", "R"))

    # Synthetic energy target for end-to-end smoke testing only.
    energy = (
        0.35
        + 0.0035 * df["Tinj"]
        + 0.0060 * df["Pinj"]
        + 0.0040 * df["Ph"]
        + 0.0020 * df["Bp"]
        + 0.0250 * df["tinj"]
        + 0.0080 * df["th"]
        + rng.normal(0, 0.025, n)
    )
    df["energy"] = energy.clip(lower=0.2)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Wrote {len(df)} demo rows to {OUT}")


if __name__ == "__main__":
    main()

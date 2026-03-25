import pandas as pd

LM_POSITIVE = set()
LM_NEGATIVE = set()


def load_lm_dictionary(filepath):
    global LM_POSITIVE, LM_NEGATIVE

    df = pd.read_csv(filepath)

    LM_POSITIVE = set(df[df["Positive"] > 0]["Word"].str.lower())
    LM_NEGATIVE = set(df[df["Negative"] > 0]["Word"].str.lower())

    print(f"Loaded LM dictionary: {len(LM_POSITIVE)} positive, {len(LM_NEGATIVE)} negative words")
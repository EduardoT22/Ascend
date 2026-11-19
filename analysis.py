"""
Ascend — pandas analysis for the submitted questions (DRAFT)

Reads sample_profiles.csv, builds the 2 calculated columns with
ascend.py (so the app and the analysis use the SAME calorie
definition), then answers Q1-Q3, plus optional Q4.

Q1: distribution of fitness goals — counts + %
Q2: activity level vs average estimated daily calories (goal-adjusted)
Q3: among lose/gain users, typical (median) desired % change,
     by fitness goal and activity level
Q4 (optional): age groups — goal mix + average calories per group.
     Age ranges are NOT in the proposal, so these are a draft choice:
     18-24, 25-34, 35-49. Change them in AGE_BINS if Eduardo picks others.

Run: python3 analysis.py
"""
import pandas as pd

from ascend import UserProfile

# Draft age ranges for optional Q4 only — not committed in the proposal.
AGE_BINS = [18, 25, 35, 50]
AGE_LABELS = ["18-24", "25-34", "35-49"]


def load_profiles(path="sample_profiles.csv"):
    """Load profiles, validate + goal-check each one, add calculated columns.

    Takes in a CSV path, returns a DataFrame with the 8 inputs plus
    estimated_daily_calories and desired_weight_change_pct.
    Rows that fail validation or the goal check are reported and skipped,
    so bad sample rows cannot silently enter the analysis.
    """
    raw = pd.read_csv(path)
    rows = []
    for _, r in raw.iterrows():
        profile = UserProfile(
            name=r["name"], age=int(r["age"]), height_inches=float(r["height_inches"]),
            weight_lbs=float(r["weight_lbs"]), fitness_goal=r["fitness_goal"],
            goal_weight_lbs=float(r["goal_weight_lbs"]),
            activity_level=r["activity_level"], sex=r["sex"],
        )
        errors = profile.validate()
        passes, message = profile.goal_check()
        if errors:
            print(f"Skipping {r['name']}: validation errors {errors}")
            continue
        if not passes:
            print(f"Skipping {r['name']}: {message}")
            continue
        rows.append(profile.to_dict())
    return pd.DataFrame(rows)


def question_1(df):
    """Q1: How does the distribution of fitness goals compare? Returns counts + %."""
    counts = df["fitness_goal"].value_counts()
    pct = df["fitness_goal"].value_counts(normalize=True) * 100
    return pd.DataFrame({"count": counts, "percent": pct.round(1)})


def question_2(df):
    """Q2: How does activity level affect average estimated daily calories?

    Note: estimated_daily_calories is now GOAL-ADJUSTED (lose -500,
    maintain 0, gain +500), so a group average mixes activity AND
    the mix of goals in that group. Describe it as a difference in
    the app's goal-adjusted estimates, not as activity alone causing it.
    """
    return (
        df.groupby("activity_level")["estimated_daily_calories"]
        .agg(["count", "mean"])
        .round(1)
        .reindex(["bmr", "sedentary", "light", "moderate", "active", "very_active", "extra_active"])
    )


def question_3(df):
    """Q3: Typical (median) desired % change, lose/gain only, by goal x activity."""
    subset = df[df["fitness_goal"].isin(["lose weight", "gain weight"])]
    return (
        subset.groupby(["fitness_goal", "activity_level"])["desired_weight_change_pct"]
        .agg(["count", "median"])
        .round(2)
    )


def question_4(df):
    """Q4 (optional): goals + average calories by age group."""
    df = df.copy()
    df["age_group"] = pd.cut(df["age"], bins=AGE_BINS, labels=AGE_LABELS, right=False)
    goals = df.groupby(["age_group", "fitness_goal"], observed=True).size().unstack(fill_value=0)
    calories = df.groupby("age_group", observed=True)["estimated_daily_calories"].mean().round(1)
    return goals, calories


if __name__ == "__main__":
    df = load_profiles()
    print(f"Profiles analysed: {len(df)} (sample data only — no real users)\n")

    print("Q1 — Fitness goal distribution")
    print(question_1(df), "\n")

    print("Q2 — Average estimated daily calories (goal-adjusted) by activity level")
    print(question_2(df), "\n")

    print("Q3 — Median desired % weight change, lose/gain users, by goal x activity")
    print(question_3(df), "\n")

    print("Q4 (optional) — Fitness goals by age group")
    goals, calories = question_4(df)
    print(goals)
    print("\nQ4 (optional) — Average estimated daily calories by age group")
    print(calories)

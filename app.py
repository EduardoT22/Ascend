"""
Ascend — Streamlit app (DRAFT, built Nov 17, 2026 for the MIST 4600 workday)

What this file is, in plain terms:
  This is ONLY the front-end. It does no calorie math of its own.
  It collects the 8 profile fields in a form, hands them to the
  code Eduardo already has, and shows the results:
    - ascend.py  -> UserProfile class: validate(), goal_check(),
      maintenance_calories, estimated_daily_calories,
      desired_weight_change_pct
    - analysis.py -> load_profiles(), question_1/2/3: the pandas
      answers on the 300 sample profiles

  So if the professor asks "where does the number come from?",
  the answer is always ascend.py, not this file.

How to run it (on Eduardo's laptop, in the project folder):
    pip install -r requirements.txt
    streamlit run app.py
  That opens http://localhost:8501 in the browser.
  For the showcase, the same repo can be deployed free on
  Streamlit Cloud for a shareable link — no code change needed.

Sample data only: the Q1-Q3 section uses sample_profiles.csv
(Sample A-L, made-up profiles). No real names or metrics.
"""
import streamlit as st
import pandas as pd
import altair as alt

from ascend import UserProfile
from analysis import load_profiles, question_1, question_2, question_3

# Brand colors, exactly as the logo — see BRAND.md.
BRAND = ["#FF4D8D", "#D500E6", "#B000F0", "#7C2FF7", "#5A3DFF", "#2E7DFF", "#00B4FF"]

st.set_page_config(
    page_title="Ascend — Personalized Fitness Profile",
    page_icon="ascend-logo-transparent.png",
    layout="wide",
)

# Ascend logo, transparent version: the white background was removed,
# so the logo blends into the white app background. The file lives in
# the repo root, next to app.py, so Streamlit Cloud loads it with the app.
# Exact brand colors are in BRAND.md: pink #FF4D8D, magenta #D500E6,
# purple #7C2FF7, blue #2E7DFF, navy #0A1931, background white #FFFFFF.
st.image("ascend-logo-transparent.png", width=300)

# Brand the app exactly like the logo, on a WHITE background:
# gradient buttons, navy headings, gradient divider. This CSS only
# changes styling, not math. The light theme itself is in
# .streamlit/config.toml (background #FFFFFF, text #0A1931).
st.markdown(
    """
    <style>
    .stApp { background-color: #FFFFFF; color: #0A1931; }
    .stButton > button, .stFormSubmitButton > button {
        background: linear-gradient(90deg, #FF4D8D, #D500E6, #7C2FF7, #2E7DFF);
        color: white; border: none;
    }
    h1, h2, h3 { color: #0A1931; }
    hr { border: none; height: 3px;
         background: linear-gradient(90deg, #FF4D8D, #D500E6, #7C2FF7, #2E7DFF); }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")
st.write(
    "My app helps new Ascend users create a personalized fitness profile by "
    "validating their information, checking whether their goal weight aligns "
    "with their fitness goal, and estimating their daily calorie needs based "
    "on their personal metrics and activity level."
)
st.caption("MIST 4600 project — Python + pandas + Streamlit. Sample data only in the analysis below.")

# ---------------------------------------------------------------------------
# Section 1: one new user's profile
# ---------------------------------------------------------------------------
st.header("1. Create your profile")

st.write(
    "Fill in the 8 fields from the proposal, then press the button. "
    "Ascend validates the entries, checks the goal weight, and estimates "
    "a goal-adjusted daily calorie target: maintenance (Mifflin-St Jeor "
    "BMR x activity) then lose -500, maintain 0, gain +500."
)

with st.form("profile_form"):
    name = st.text_input("Name", placeholder="e.g. Sample User")
    age = st.number_input("Age (years)", min_value=15, max_value=80, step=1, value=20)
    sex = st.radio("Gender", ["male", "female"], horizontal=True)
    st.write("Height")
    height_col1, height_col2 = st.columns(2)
    with height_col1:
        height_feet = st.number_input("Feet", min_value=0, max_value=8, step=1, value=6)
    with height_col2:
        height_inches_only = st.number_input("Inches", min_value=0, max_value=11, step=1, value=0)
    weight_lbs = st.number_input("Current weight (lb)", min_value=1.0, step=1.0, value=185.0)
    fitness_goal = st.selectbox(
        "Fitness goal",
        ["lose weight", "maintain weight", "gain weight"],
    )
    goal_weight_lbs = st.number_input("Goal weight (lb)", min_value=1.0, step=1.0, value=176.0)
    # Calculator.net's 7 activity choices, exactly as on calculator.net.
    # Labels only — the multipliers are in ascend.py (1.0 / 1.2 / 1.375 /
    # 1.55 / 1.725 / 1.9 / 1.95).
    activity_label = st.radio(
        "Activity Level",
        [
            "Basal Metabolic Rate (BMR)",
            "Sedentary: little or no exercise",
            "Light: exercise 1-3 times/week",
            "Moderate: exercise 4-5 times/week",
            "Active: daily exercise or intense exercise 3-4 times/week",
            "Very Active: intense exercise 6-7 times/week",
            "Extra Active: very intense exercise daily, or physical job",
        ],
    )
    submitted = st.form_submit_button("Check my profile")

if submitted:
    # Convert feet + inches to total inches, exactly what the lab takes.
    # 6 ft 0 in = 72 in.
    height_inches = float(height_feet * 12 + height_inches_only)
    activity_level = {
        "Basal Metabolic Rate (BMR)": "bmr",
        "Sedentary: little or no exercise": "sedentary",
        "Light: exercise 1-3 times/week": "light",
        "Moderate: exercise 4-5 times/week": "moderate",
        "Active: daily exercise or intense exercise 3-4 times/week": "active",
        "Very Active: intense exercise 6-7 times/week": "very_active",
        "Extra Active: very intense exercise daily, or physical job": "extra_active",
    }[activity_label]
    # Build the class object — one UserProfile holds the 8 inputs.
    profile = UserProfile(
        name=name,
        age=int(age),
        height_inches=float(height_inches),
        weight_lbs=float(weight_lbs),
        fitness_goal=fitness_goal,
        goal_weight_lbs=float(goal_weight_lbs),
        activity_level=activity_level,
        sex=sex,
    )

    # Step 1: validation — "did the user fill in every field?" etc.
    # validate_profile() returns a list of error strings; empty = valid.
    errors = profile.validate()
    if errors:
        st.error("Please fix these entries:")
        for error in errors:
            st.write(f"- {error}")
    else:
        # Step 2: goal-weight check — lose < current, maintain = current,
        # gain > current. Returns (passes, message).
        passes, message = profile.goal_check()
        if not passes:
            st.error(message)
            st.write("Fix the goal or the goal weight, then try again.")
        else:
            st.success(message)
            # Step 3: the two calorie numbers, both from ascend.py.
            # maintenance = BMR x activity; estimated = maintenance + goal adjustment.
            st.subheader("Your estimate")
            col1, col2, col3 = st.columns(3)
            col1.metric("Maintenance calories", f"{profile.maintenance_calories:,} / day")
            col2.metric("Goal-adjusted daily calories", f"{profile.estimated_daily_calories:,} / day")
            col3.metric("Desired weight change", f"{profile.desired_weight_change_pct:.2f}%")
            st.write(
                f"Maintenance is {profile.maintenance_calories:,} cal/day. "
                f"For '{fitness_goal}' Ascend adjusts it by "
                f"{profile.estimated_daily_calories - profile.maintenance_calories:+,} "
                f"to {profile.estimated_daily_calories:,} cal/day. "
                "Desired % change is what you want to change, not what you lost or gained."
            )

# ---------------------------------------------------------------------------
# Section 2: the data questions, on the 300 sample profiles
# ---------------------------------------------------------------------------
st.header("2. What the sample profiles show (Q1–Q3)")

st.write(
    "These answers come from analysis.py, using the same calorie "
    "definition as Section 1. The data is 300 made-up sample profiles "
    "— no real users."
)

try:
    df = load_profiles("sample_profiles.csv")
    st.write(f"Profiles analysed: {len(df)} (sample data only)")

    st.subheader("Q1 — How does the distribution of fitness goals compare?")
    q1 = question_1(df)
    st.dataframe(q1)
    q1_chart = q1.reset_index()
    st.altair_chart(
        alt.Chart(q1_chart)
        .mark_bar()
        .encode(
            x=alt.X("fitness_goal:N", title="Fitness goal"),
            y=alt.Y("count:Q", title="Users"),
            color=alt.Color("fitness_goal:N", scale=alt.Scale(range=BRAND[:3]), legend=None),
        ),
        use_container_width=True,
    )

    st.subheader("Q2 — Average estimated daily calories (goal-adjusted) by activity level")
    st.write(
        "Note: these are goal-adjusted averages, so a group average mixes "
        "activity AND the mix of lose / maintain / gain users in that group."
    )
    q2 = question_2(df)
    st.dataframe(q2)
    q2_chart = q2.reset_index()
    st.altair_chart(
        alt.Chart(q2_chart)
        .mark_bar()
        .encode(
            x=alt.X("activity_level:N", title="Activity level", sort=["bmr", "sedentary", "light", "moderate", "active", "very_active", "extra_active"]),
            y=alt.Y("mean:Q", title="Average daily calories"),
            color=alt.Color("activity_level:N", scale=alt.Scale(domain=["bmr", "sedentary", "light", "moderate", "active", "very_active", "extra_active"], range=BRAND), legend=None),
        ),
        use_container_width=True,
    )

    st.subheader("Q3 — Median desired % weight change, lose / gain users, by goal x activity")
    q3 = question_3(df)
    st.dataframe(q3)

    with st.expander("See the 300 sample profiles"):
        st.dataframe(df)
except FileNotFoundError:
    st.warning("sample_profiles.csv was not found next to app.py, so Q1–Q3 cannot load.")

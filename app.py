"""
Ascend — Streamlit app (updated Nov 19, 2026)

What this file is, in plain terms:
  This is ONLY the front-end. It does no calorie math of its own.
  It collects the profile fields in a form, hands them to the
  code Eduardo already has, and shows the results:
    - ascend.py  -> UserProfile class: validate(), goal_check(),
      maintenance_calories, estimated_daily_calories,
      desired_weight_change_pct, weeks_to_goal,
      projected_weight_path()

  Q1-Q3 are NOT shown here. They stay in the notebook
  (ascend.ipynb), where they are answered with pandas on the
  300 sample profiles. This app is for creating one profile
  and seeing that person's plan.

  New Nov 19, 2026 — weight-loss rate slider: for lose weight,
  pick 0.5 / 1.0 / 1.5 lb/week. Deficit is rate x 500 cal/day
  (-250 / -500 / -750), 1 lb of fat is about 3,500 cal, so
  3,500 / 7 = 500. Default 1.0, so the demo is unchanged.
  The line chart below shows weight over time at all 3 rates,
  with the slider's rate highlighted in Ascend colors and the
  other two muted. That chart is a plan from the user's own
  numbers — the sample data has no outcomes, so it cannot
  prove a calorie level works.

How to run it (on Eduardo's laptop, in the project folder):
    pip install -r requirements.txt
    streamlit run app.py
  That opens http://localhost:8501 in the browser.
  Live: https://ascend-eduardot22.streamlit.app/
"""
import streamlit as st
import pandas as pd
import altair as alt

from ascend import (
    UserProfile,
    WEIGHT_LOSS_RATES,
    projected_weight_path,
    weight_loss_deficit,
)

# Brand colors, exactly as the logo — see BRAND.md.
# Rate colors: 0.5 pink, 1.0 purple, 1.5 blue.
RATE_COLORS = {0.5: "#FF4D8D", 1.0: "#7C2FF7", 1.5: "#2E7DFF"}

st.set_page_config(
    page_title="Ascend — Personalized Fitness Profile",
    page_icon="ascend-logo-transparent.png",
    layout="wide",
)

# Ascend logo, transparent version: the white background was removed,
# so the logo blends into the white app background.
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
st.caption("MIST 4600 project — Python + pandas + Streamlit. Q1–Q3 are answered in the notebook, not here.")

# ---------------------------------------------------------------------------
# Section 1: one new user's profile
# ---------------------------------------------------------------------------
st.header("1. Create your profile")

st.write(
    "Fill in the 8 fields from the proposal, then press the button. "
    "Ascend validates the entries, checks the goal weight, and estimates "
    "a goal-adjusted daily calorie target: maintenance (Mifflin-St Jeor "
    "BMR x activity), then lose -500 per lb/week wanted, maintain 0, "
    "gain +500."
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
    # Weight-loss rate slider — lose weight only. 0.5 / 1.0 / 1.5 lb/week,
    # step 0.5, default 1.0. Ignored for maintain / gain.
    weight_loss_rate = st.select_slider(
        "How fast do you want to lose weight? (lb/week — lose weight only)",
        options=list(WEIGHT_LOSS_RATES),
        value=1.0,
        help="0.5 lb/week is -250 cal/day, 1.0 is -500, 1.5 is -750. 1 lb of fat is about 3,500 cal, so 3,500 / 7 = 500 cal/day per lb/week. Not a medical recommendation.",
    )
    # Calculator.net's 7 activity choices, exactly as on calculator.net.
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
    profile = UserProfile(
        name=name,
        age=int(age),
        height_inches=float(height_inches),
        weight_lbs=float(weight_lbs),
        fitness_goal=fitness_goal,
        goal_weight_lbs=float(goal_weight_lbs),
        activity_level=activity_level,
        sex=sex,
        weight_loss_rate_lb_per_week=float(weight_loss_rate),
    )

    errors = profile.validate()
    if errors:
        st.error("Please fix these entries:")
        for error in errors:
            st.write(f"- {error}")
    else:
        passes, message = profile.goal_check()
        if not passes:
            st.error(message)
            st.write("Fix the goal or the goal weight, then try again.")
        else:
            st.success(message)
            st.subheader("Your estimate")
            col1, col2, col3 = st.columns(3)
            col1.metric("Maintenance calories", f"{profile.maintenance_calories:,} / day")
            col2.metric("Goal-adjusted daily calories", f"{profile.estimated_daily_calories:,} / day")
            col3.metric("Desired weight change", f"{profile.desired_weight_change_pct:.2f}%")
            if fitness_goal == "lose weight":
                st.write(
                    f"Maintenance is {profile.maintenance_calories:,} cal/day. "
                    f"At {weight_loss_rate} lb/week, Ascend adjusts it by "
                    f"{weight_loss_deficit(weight_loss_rate):+,} "
                    f"to {profile.estimated_daily_calories:,} cal/day. "
                    f"That is {profile.weeks_to_goal:.0f} weeks to your goal. "
                    "Desired % change is what you want to change, not what you lost or gained."
                )
                if profile.estimated_daily_calories < 1200:
                    st.warning(
                        "This target is below 1,200 cal/day. A fast rate is not "
                        "right for everyone — consider a slower rate. "
                        "This is not medical advice."
                    )
            else:
                st.write(
                    f"Maintenance is {profile.maintenance_calories:,} cal/day. "
                    f"For '{fitness_goal}' Ascend adjusts it by "
                    f"{profile.estimated_daily_calories - profile.maintenance_calories:+,} "
                    f"to {profile.estimated_daily_calories:,} cal/day. "
                    "Desired % change is what you want to change, not what you lost or gained."
                )

            # -------------------------------------------------------------------
            # Section 2: your journey — weight over time, by rate
            # -------------------------------------------------------------------
            st.header("2. Your journey to your goal")
            if fitness_goal == "lose weight":
                st.write(
                    "All 3 lines start at your current weight and end at your "
                    "goal weight. The line for the rate you picked is highlighted "
                    "in Ascend colors; the other two are muted, for comparison. "
                    "This is a plan from your own numbers — not a prediction "
                    "from past users."
                )
                # Build one row per week per rate, for the Altair line chart.
                rows = []
                for rate in WEIGHT_LOSS_RATES:
                    for week, weight in projected_weight_path(
                        float(weight_lbs), float(goal_weight_lbs), fitness_goal, rate
                    ):
                        rows.append(
                            {
                                "week": week,
                                "weight": weight,
                                "rate": f"{rate} lb/week",
                                "selected": rate == float(weight_loss_rate),
                            }
                        )
                chart_df = pd.DataFrame(rows)
                selected_df = chart_df[chart_df["selected"]]
                other_df = chart_df[~chart_df["selected"]]
                # Selected line: its Ascend color, thick. Others: light grey, thin.
                selected_color = RATE_COLORS[float(weight_loss_rate)]
                selected_line = (
                    alt.Chart(selected_df)
                    .mark_line(strokeWidth=4)
                    .encode(
                        x=alt.X("week:Q", title="Weeks"),
                        y=alt.Y("weight:Q", title="Weight (lb)", scale=alt.Scale(zero=False)),
                        color=alt.Color(
                            "rate:N",
                            scale=alt.Scale(domain=[f"{float(weight_loss_rate)} lb/week"], range=[selected_color]),
                            title="Rate",
                        ),
                    )
                )
                other_rates = [r for r in WEIGHT_LOSS_RATES if r != float(weight_loss_rate)]
                other_line = (
                    alt.Chart(other_df)
                    .mark_line(strokeWidth=1.5, opacity=0.7)
                    .encode(
                        x=alt.X("week:Q", title="Weeks"),
                        y=alt.Y("weight:Q", title="Weight (lb)", scale=alt.Scale(zero=False)),
                        color=alt.Color(
                            "rate:N",
                            scale=alt.Scale(domain=[f"{r} lb/week" for r in other_rates], range=["#D3D3D3", "#D3D3D3"]),
                            title="Rate",
                        ),
                    )
                )
                goal_rule = (
                    alt.Chart(pd.DataFrame({"goal": [float(goal_weight_lbs)]}))
                    .mark_rule(strokeDash=[6, 4], color="#0A1931")
                    .encode(y="goal:Q")
                )
                st.altair_chart(selected_line + other_line + goal_rule, use_container_width=True)
                st.write(
                    f"At your chosen rate, **{weight_loss_rate} lb/week**, "
                    f"that is **{profile.estimated_daily_calories:,} cal/day** "
                    f"and **{profile.weeks_to_goal:.0f} weeks** to your goal. "
                    f"At 0.5 it would be {profile.maintenance_calories - 250:,} cal/day "
                    f"and {(float(weight_lbs) - float(goal_weight_lbs)) / 0.5:.0f} weeks; "
                    f"at 1.5 it would be {profile.maintenance_calories - 750:,} cal/day "
                    f"and {(float(weight_lbs) - float(goal_weight_lbs)) / 1.5:.0f} weeks."
                )
            elif fitness_goal == "gain weight":
                st.write(
                    f"At +500 cal/day, about 1 lb/week, that is "
                    f"**{profile.weeks_to_goal:.0f} weeks** to your goal."
                )
            else:
                st.write("You are already at your goal weight — 0 weeks to go.")

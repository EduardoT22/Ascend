# Ascend — One-Page Explainer (for the MIST 4600 final exam)

Updated Nov 19, 2026 — verified against the CURRENT `ascend.py`,
`analysis.py`, `app.py`, and `ascend.ipynb`.
All profile numbers are from the 300 made-up sample profiles in
`sample_profiles.csv` only — no real users.

## In one sentence

Ascend collects one new user's 8 inputs, validates them, checks goal
weight against the fitness goal, and estimates a goal-adjusted daily
calorie target.

## Pipeline

`validate_profile()` → `check_goal_weight()` →
`estimate_daily_calories()` → `desired_weight_change_pct()`, then
`UserProfile.to_dict()` adds the 2 calculated columns for pandas in
`analysis.py`. `load_profiles()` runs every row through the class,
so a bad row never reaches Q1–Q3.

## Functions — what goes in, what comes out

- `validate_profile(dict)` → list of error strings. Empty list = valid.
  Checks every field is filled, age 15–80, height/weight positive,
  goal is lose / maintain / gain, sex is male / female.
- `check_goal_weight(current, goal, fitness_goal)` → (passes bool, message).
  Lose: goal < current. Maintain: goal = current. Gain: goal > current.
- `calculate_bmr(sex, age, height_inches, weight_lbs)` → BMR, calories/day.
- `activity_multiplier(activity_level)` → the multiplier for that level.
- `estimate_maintenance_calories(...)` → round(BMR × activity).
- `estimate_daily_calories(...+ fitness_goal, weight_loss_rate_lb_per_week=1.0)` → maintenance + goal adjustment.
- `weight_loss_deficit(rate)` → -250 / -500 / -750 for 0.5 / 1.0 / 1.5.
- `weeks_to_goal(current, goal, fitness_goal, rate=1.0)` → weeks, a float.
- `projected_weight_path(current, goal, fitness_goal, rate=1.0)` → list of (week, weight) points for the line chart.
- `desired_weight_change_pct(current, goal)` → (goal − current) / current × 100.

## Formula — Mifflin-St Jeor

kg = lb / 2.20462, cm = in × 2.54. Male: 10×kg + 6.25×cm − 5×age + 5.
Female: same, but −161 instead of +5.
Goal adjustment: lose −500 per lb/week wanted, maintain 0, gain +500.
The lose rate is a slider: 0.5 / 1.0 / 1.5 lb/week, default 1.0,
so −250 / −500 / −750 cal/day. That 500 per lb/week is 1 lb of fat
is about 3,500 cal, so 3,500 / 7 days = 500 cal/day per lb/week —
a simple documented rule, not a medical recommendation.
Weeks to goal for lose users is (current − goal) / rate.
Gain is +500, about 1 lb/week, so weeks = goal − current.
Maintain is 0 weeks.

## Activity levels — 7, calculator.net style (changed Nov 19, 2026)

This is NOT the 3 levels in the submitted proposal (low / moderate / high).
Project files use 7: bmr 1.0, sedentary 1.2, light 1.375, moderate 1.55,
active 1.725, very_active 1.9, extra_active 1.95.
calculator.net lists sedentary 1.2, light 1.375, moderate 1.55,
very active 1.725, extra active 1.9, factor range 1.2–1.95.
extra_active 1.95 is the top of that range, chosen to separate it
from very_active 1.9. This deviation is noted in `ascend.py` and README.
TRAP: Module06 lab Cell 35 still uses the old 3 levels — the lab was
NOT updated, on purpose. The project (ascend.py, notebook, app) uses 7.

## Worked example — the demo

20-year-old male, 72 in, 185 lb, lose to 176 lb, moderate activity.

- kg 83.91, cm 182.88
- BMR = 839.1 + 1,143.0 − 100 + 5 = 1,887.1
- Maintenance = 1,887.1 × 1.55 = 2,925
- Goal-adjusted, lose = 2,925 − 500 = **2,425**
- Desired change = (176 − 185) / 185 × 100 = **−4.86%**
- Weeks to goal: 9 lb to lose, so 18 weeks at 0.5, **9 weeks at 1.0**,
  6 weeks at 1.5. Targets: 2,675 / 2,425 / 2,175 cal/day.
- Same person gaining would be 3,425. And lose at 185 → 195 fails
  the goal check, with a mismatch message.
- Lab test, same math: male 25y, 70 in, 180 lb, moderate, lose = 2,302.0.
  It did not change when levels went 3 → 7, because moderate is still 1.55.

## The class

`UserProfile` holds the 8 fields, with `.validate()`, `.goal_check()`,
`.maintenance_calories`, `.estimated_daily_calories`,
`.desired_weight_change_pct`, and `.to_dict()`. That's the "at least one
class actually used" requirement — `load_profiles()` and `app.py` both
use it, it is not just defined.

## Q1–Q3, on the 300 sample profiles (sample data only, no real users)

300 rows, stratified 7 activities × 3 goals, ~42–44 per activity.
Ages 18–45, heights 60–76 in by sex, weights from BMI 18–31,
lose −4% to −12%, gain +4% to +9%, maintain 0%.

- Q1: lose 126 (42.0%), gain 105 (35.0%), maintain 69 (23.0%)
- Q2, goal-adjusted average cal/day: bmr 1,614.4 (n=42), sedentary
  1,897.8 (n=43), light 2,024.4 (n=43), moderate 2,456.2 (n=44),
  active 2,674.3 (n=43), very_active 2,879.4 (n=43),
  extra_active 2,955.2 (n=42)
- Q3, median desired %: lose — bmr −10.00%, sedentary −7.03%,
  light −8.27%, moderate −9.09%, active −8.95%, very_active −8.20%,
  extra_active −8.53%; gain — bmr +6.81%, sedentary +5.19%,
  light +7.14%, moderate +5.77%, active +6.86%, very_active +6.98%,
  extra_active +5.99%
- Q4 (optional, draft age groups 18–24, 25–34, 35–49): goal counts
  and average calories by age group, in `analysis.py` `question_4()`.

## The app and the notebook — what each file does

- `app.py` — front-end ONLY, no calorie math of its own. It collects
  the 8 fields in a form, plus a weight-loss rate slider (0.5 / 1.0 /
  1.5 lb/week, lose only, default 1.0), calls `UserProfile` from
  `ascend.py`, and shows a line chart of weight over time at all 3
  rates, with the slider's rate highlighted in Ascend colors
  (0.5 pink #FF4D8D, 1.0 purple #7C2FF7, 1.5 blue #2E7DFF) and the
  other two muted grey. Q1–Q3 are NOT in the app — they stay in the
  notebook. White background #FFFFFF, navy text #0A1931, transparent
  logo `ascend-logo-transparent.png`, gradient buttons.
  Theme is in `.streamlit/config.toml`. Live:
  https://ascend-eduardot22.streamlit.app/
- `ascend.ipynb` — project notebook. Same math, same class, Q1–Q4 as
  named functions (`question_1`, `question_2`, `question_3`,
  `question_4`), brand-color matplotlib charts after Q1/Q2.
  Outside tool: `get_recommendation()` — one Gemini call
  (model gemini-flash-lite-latest, key from Colab Secrets
  `GOOGLE_API_KEY`, never typed in code), one encouraging sentence
  for the demo profile, no medical advice.
- `analysis.py` — `load_profiles(path)`, `question_1/2/3/4`.
  Q1 counts + %, Q2 mean by activity, Q3 median by goal × activity,
  lose and gain kept separate.

## Traps to say out loud on the exam

1. Validation — "did they fill in every field?" — is NOT one of the
   four analysis questions.
2. Q2 is goal-adjusted, so a group average mixes activity AND the mix
   of lose/maintain/gain users in that group. Describe it as a
   difference in goal-adjusted estimates, not proof activity alone
   caused it.
3. Desired % change is what users want, not what they lost or gained.
4. Q4 age groups 18–24, 25–34, 35–49 in `analysis.py` are a draft
   choice, not committed in the proposal.
5. `analysis.py` / notebook `load_profiles` skips rows that fail
   validation or the goal check, so bad sample rows can't silently
   enter Q1–Q3.
6. Project = 7 activity levels. Module06 lab = 3 levels. Moderate
   1.55 is why the demo (2,925 / 2,425) and lab test (2,302.0)
   did not change.
7. Workout logging, meal tracking, grocery-list connection, and
   wearables are OUT of scope for this project — they are what's next,
   not what's graded.
8. The rate slider changes ONE user's target from THEIR maintenance:
   0.5 / 1.0 / 1.5 lb/week = -250 / -500 / -750. Weeks to goal is
   (current - goal) / rate. The sample data has no outcomes, so it
   cannot prove a calorie level works for a rate — the line chart
   is a plan, not a prediction from past users.
9. Q1–Q3 stay in the notebook only. The Streamlit app is profile-only:
   form + rate slider + weight-over-time line chart.

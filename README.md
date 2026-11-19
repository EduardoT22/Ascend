# Ascend

![Ascend logo](ascend-logo.png)

### RISE. TRACK. BECOME MORE.

**My app helps new Ascend users create a personalized fitness profile by validating their information, checking whether their goal weight aligns with their fitness goal, and estimating their daily calorie needs based on their personal metrics and activity level.**

Ascend started in MIST 2090 as a fitness and wellness app — workout discovery, daily progress tracking, and motivation in one place. In MIST 4600, this project builds the working part: new-user profile setup only. Workout logging, meal tracking, and wearables are out of scope here.

> A course project for **MIST 4600: Computer Programming in Business** at the University of Georgia's Terry College of Business.

## Problem

New Ascend users need to create a personalized fitness profile, but it is hard to know whether their information is complete and realistic, whether their goal weight matches their fitness goal, and how many daily calories they need. Ascend helps a new user make that profile decision with validated inputs and a clear calorie estimate instead of guessing.

## What it does

My app answers four data questions (Q4 optional), exactly as submitted in my proposal:

| # | Sub-question | How the app answers it |
|---|---|---|
| 1 | How does the distribution of fitness goals compare among Ascend users? | Count + % per goal, with pandas |
| 2 | How does activity level affect the average recommended daily calorie intake? | Group by activity level, compare average estimated daily calories, with pandas |
| 3 | Among lose/gain users, what is the typical desired % weight change for each activity level? | Median desired % change, lose and gain kept separate, grouped by activity level, with pandas |
| 4 | (Optional) How do fitness goals and average daily calorie needs differ across age groups? | Group by age group (draft ranges 18-24, 25-34, 35-49 — not committed in the proposal) |

For each new user, the app also validates the 8 profile fields (name, age, height_inches, weight_lbs, fitness_goal, goal_weight_lbs, activity_level, sex), checks the goal weight (lose = goal < current, maintain = goal = current, gain = goal > current), and estimates goal-adjusted daily calories: Mifflin-St Jeor BMR x activity = maintenance, then lose -500, maintain 0, gain +500. Activity is calculator.net's 7 choices: BMR 1.0, Sedentary 1.2, Light 1.375, Moderate 1.55, Active 1.725, Very Active 1.9, Extra Active 1.95. This replaces the proposal's low / moderate / high (1.2 / 1.55 / 1.725) at Eduardo's request, Nov 19, 2026, to match calculator.net exactly. That ±500 is a simple documented rule, about 1 lb/week — my choice, not a medical recommendation. Validation and the goal-weight check are part of what the app does for a new user; they are not data questions.

The Streamlit web app (`app.py`) is an interactive profile form collecting the same 8 fields, with the Ascend branding from MIST 2090: dark navy, gradient pink → magenta → purple → blue, and the tagline above.

## Data

`sample_profiles.csv` is fabricated sample data, made up for this project because Ascend has no real users yet. It has 300 realistic profiles, stratified so the spread is even: 7 activity levels x 3 fitness goals, about 42-44 profiles per activity level and 15-19 per lose/gain x activity group. Ages 18-45, heights 60-76 in, weights from BMI 18-31, goal changes lose -4% to -12%, gain +4% to +9%, maintain 0%. No real users, no real names or personal metrics. Do not add real profiles to this public repo.

## Built with

- Python and pandas, in Google Colab (`ascend.ipynb`)
- Google Gemini API, called from the notebook for one personalized recommendation per new user
- Streamlit, for the interactive profile form (`app.py`)

## How to run it

1. Open `ascend.ipynb` in Google Colab.
2. Put `ascend.ipynb` and `sample_profiles.csv` in the same folder in your Google Drive.
3. Add your Gemini key to Colab Secrets (key icon on the left) with the name `GOOGLE_API_KEY`, and turn on **Notebook access**. Get the key at [aistudio.google.com](https://aistudio.google.com) with a personal Gmail account. Never type the key into the code.
4. Runtime → **Run all**. The Gemini cell calls Gemini once, so it takes a few seconds.

To run the Streamlit app locally:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Live Streamlit app link: https://ascend-eduardot22.streamlit.app/

## Example output

One profile — 20-year-old male, 72 in, 185 lb, lose to 176 lb, moderate activity:

```
Errors: []
Goal check: Goal weight 176 lb fits 'lose weight' at 185 lb.
Maintenance calories: 2925
Estimated daily calories (goal-adjusted, lose -500): 2425
Desired change %: -4.86
```

300 sample profiles:

- Q1: lose 126 (42.0%), gain 105 (35.0%), maintain 69 (23.0%)
- Q2: average goal-adjusted daily calories — BMR 1,614.4 (n=42), Sedentary 1,897.8 (n=43), Light 2,024.4 (n=43), Moderate 2,456.2 (n=44), Active 2,674.3 (n=43), Very Active 2,879.4 (n=43), Extra Active 2,955.2 (n=42)
- Q3: median desired % change — lose -10.00% (BMR, n=17), -7.03% (Sedentary, n=18), -8.27% (Light, n=18), -9.09% (Moderate, n=19), -8.95% (Active, n=18), -8.20% (Very Active, n=18), -8.53% (Extra Active, n=18); gain +6.81% (BMR, n=15), +5.19% (Sedentary, n=15), +7.14% (Light, n=15), +5.77% (Moderate, n=15), +6.86% (Active, n=15), +6.98% (Very Active, n=15), +5.99% (Extra Active, n=15)

These numbers describe the app's goal-adjusted estimates for the sample profiles. Because the estimate includes the goal (-500 / 0 / +500), activity groups may also differ in their mix of goals, so a higher average in one group is a difference in goal-adjusted estimates, not proof that activity alone caused it.

## AI Use Disclosure

- **Used AI?** Yes
- **Tools:** Muse (Meta's Muse agent) and Google Gemini (gemini-flash-lite-latest, in Colab)
- **What I asked:** Draft the notebook code and text from my question and sub-questions, draft the `UserProfile` class and calorie functions, draft the pandas code for Q1–Q3, draft the Streamlit app, generate the 300 sample profiles, apply my logo and brand colors, and deploy the app.
- **What I added / changed / fixed:** I chose the Ascend idea from MIST 2090, the one sentence, and Q1–Q4. I chose goal-adjusted calories instead of maintenance alone, I chose the 7 calculator.net activity levels instead of the original 3, I chose 300 rows, I chose the white background and transparent logo, and I checked the results — demo 2,925 / 2,425, lab test 2,302.0, Q1 lose 126 / gain 105 / maintain 69.
- **What I designed / wrote myself:** The project idea, the proposal, the sub-questions, the branding and logo, the recommendation, and the decisions above.
- **Understand every line?** Yes

## Author

Eduardo Torres

# Ascend
My app helps new Ascend users create a personalized fitness profile by validating their information, checking whether their goal weight aligns with their fitness goal, and estimating their daily calorie needs based on their personal metrics and activity level.

> A course project for **MIST 4600: Computer Programming in Business** at the University of Georgia's Terry College of Business.

## Problem
New Ascend users need to create a personalized fitness profile, but it is hard to know whether their information is complete and realistic, whether their goal weight matches their fitness goal, and how many daily calories they need. Ascend helps a new user make that profile decision with validated inputs and a clear calorie estimate instead of guessing.

## What it does
My app answers four questions:
1. **Profile validation:** How do we validate new user information so the profile is complete and realistic?
2. **Calories by activity:** How does activity level affect the average recommended daily calorie intake of Ascend users?
3. **Goal alignment:** Does the goal weight align with the fitness goal (lose, maintain, or gain)?
4. **Daily calories:** What daily calorie needs can we estimate from personal metrics and activity level?

## Data
Week 12 practice used the Steam games dataset (steam_games.csv) from the MIST 4600 Drive folder. The Ascend project data is the user profile collected by the Streamlit form: name, age, height_inches, weight_lbs, fitness_goal, goal_weight_lbs, activity_level, and sex.

## Built with
- Python and pandas, in Google Colab
- Gemini API (Week 12 practice)
- Streamlit (Ascend interactive profile form)

## How to run it
1. Open Module06.ipynb in Google Colab from this repo or Drive.
2. Run the setup cell to load steam_games.csv from the MIST 4600 Drive folder.
3. Run the Week 12 cells in order, then Project Step 1 with REPO_URL set to this repo.
4. For the Ascend function, call goal_adjusted_calories(sex, age, height_inches, weight_lbs, activity_level, fitness_goal), for example goal_adjusted_calories("male", 25, 70, 180, "moderate", "lose weight").

## Example output
Week 12 (20 games labeled): mode_counts both 9 / multiplayer 8 / single-player 3; mode_rating both 92.7, multiplayer 78.6, single-player 92.3.
Ascend function example: goal_adjusted_calories("male", 25, 70, 180, "moderate", "lose weight") prints 2302.0 (Mifflin-St Jeor maintenance about 2802.0 minus 500 for a lose-weight goal).

## AI Use Disclosure
Coming soon - to be completed by Eduardo.

## Author
Eduardo Torres

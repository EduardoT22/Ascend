"""
Ascend — MIST 4600 project (DRAFT, pending Eduardo's confirmation)

What this file does, in plain terms:
  1. Takes ONE new user's profile (the 8 inputs from the submitted proposal).
  2. Validates it — is every field filled in, and are the values sensible?
  3. Checks goal weight against the fitness goal — lose < current,
     maintain = current, gain > current.
  4. Estimates daily calories as a GOAL-ADJUSTED target (Eduardo's
     choice, Nov 15, 2026): first Mifflin-St Jeor BMR x an activity
     multiplier = maintenance (TDEE), then adjust for the goal.
     Lose weight: -500 cal/day for every 1 lb/week the user wants
     to lose (Nov 19, 2026: rate slider 0.5 / 1.0 / 1.5 lb/week,
     so -250 / -500 / -750). Maintain weight 0, gain weight +500
     (about 1 lb/week). The 500 per lb/week is a simple, documented
     rule — 1 lb of fat is about 3,500 cal, so 3,500 / 7 days = 500
     cal/day per lb/week — not a medical recommendation.
  5. Weeks to goal and a projected weight path: for lose users,
     (current - goal) / rate. That is a plan from the user's own
     numbers, not a prediction from past users — the sample data
     has no outcomes, so it cannot prove a calorie level works.

Proposal source of truth:
  - name, age, height_inches, weight_lbs, fitness_goal,
    goal_weight_lbs, activity_level, sex
  - fitness_goal: "lose weight" | "maintain weight" | "gain weight"
  - activity_level: originally "low" | "moderate" | "high" in the
    submitted proposal. Changed Nov 19, 2026, at Eduardo's request,
    to calculator.net's 7 activity choices (see below) — the lab
    function in Module06 Cell 35 must be changed to match.
  - sex: "male" | "female"
  - desired_weight_change_pct = (goal - current) / current * 100
"""

# Activity multipliers for the maintenance estimate — calculator.net's
# 7 choices, exactly as shown on calculator.net/calorie-calculator.html:
# BMR = rest only (1.0), Sedentary = little or no exercise (1.2),
# Light = exercise 1-3 times/week (1.375), Moderate = exercise
# 4-5 times/week (1.55), Active = daily exercise or intense exercise
# 3-4 times/week (1.725), Very Active = intense exercise 6-7 times/week
# (1.9), Extra Active = very intense exercise daily, or physical job
# (1.95, the top of calculator.net's 1.2-1.95 activity-factor range).
# Documented here so the README, app, and analysis all use the same numbers.
ACTIVITY_MULTIPLIERS = {
    "bmr": 1.0,
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
    "extra_active": 1.95,
}

FITNESS_GOALS = ("lose weight", "maintain weight", "gain weight")
ACTIVITY_LEVELS = ("bmr", "sedentary", "light", "moderate", "active", "very_active", "extra_active")
SEXES = ("male", "female")

# Goal adjustment, in calories/day, applied to maintenance (TDEE).
# Maintain 0, gain +500. Lose: -500 per lb/week wanted, so the
# rate slider (0.5 / 1.0 / 1.5) gives -250 / -500 / -750.
# 1 lb/week is the default, so the old -500 lose case is unchanged.
GOAL_ADJUSTMENTS = {
    "lose weight": -500,
    "maintain weight": 0,
    "gain weight": 500,
}

WEIGHT_LOSS_RATES = (0.5, 1.0, 1.5)


def weight_loss_deficit(weight_loss_rate_lb_per_week):
    """Deficit in cal/day for a lose rate. Takes in lb/week, returns a negative int.

    1 lb of fat is about 3,500 cal, so 3,500 / 7 days = 500 cal/day
    per lb/week. 0.5 -> -250, 1.0 -> -500, 1.5 -> -750.
    """
    return -int(weight_loss_rate_lb_per_week * 500)


def weeks_to_goal(weight_lbs, goal_weight_lbs, fitness_goal, weight_loss_rate_lb_per_week=1.0):
    """Weeks to reach the goal weight. Takes in current/goal/goal/rate, returns a float.

    Lose: (current - goal) / rate. Gain: (goal - current) / 1.0,
    because gain is +500, about 1 lb/week. Maintain: 0.
    Example: 185 -> 176 lose is 9 lb: 18 weeks at 0.5, 9 at 1.0, 6 at 1.5.
    This is a plan from the user's own numbers, not a prediction.
    """
    if fitness_goal == "lose weight":
        return (weight_lbs - goal_weight_lbs) / weight_loss_rate_lb_per_week
    if fitness_goal == "gain weight":
        return goal_weight_lbs - weight_lbs
    return 0.0


def projected_weight_path(weight_lbs, goal_weight_lbs, fitness_goal, weight_loss_rate_lb_per_week=1.0):
    """Weekly weight points from current to goal. Returns a list of (week, weight).

    Lose: one point per week, dropping by the rate each week, until
    the goal (last point is exactly the goal). Gain: +1 lb/week.
    Maintain: one point, the current weight. Used for the line chart.
    """
    if fitness_goal == "maintain weight":
        return [(0, float(weight_lbs))]
    if fitness_goal == "gain weight":
        total = int(goal_weight_lbs - weight_lbs)
        return [(w, float(weight_lbs + w)) for w in range(total + 1)]
    total_weeks = int((weight_lbs - goal_weight_lbs) / weight_loss_rate_lb_per_week)
    points = []
    for w in range(total_weeks + 1):
        points.append((w, float(weight_lbs - w * weight_loss_rate_lb_per_week)))
    points[-1] = (total_weeks, float(goal_weight_lbs))
    return points


def validate_profile(profile):
    """Check one profile dict. Takes in a dict, returns a list of error strings.

    An empty list means the profile is valid. Each error names the
    field and the problem, so the app can show it and let the user fix it.
    This is the 'did the user fill in every field?' validation check —
    it is NOT one of the four analysis questions.
    """
    errors = []

    # name: must be present and not blank
    name = profile.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append("name: enter a name for the profile.")

    # age: positive whole number
    age = profile.get("age")
    if isinstance(age, bool) or not isinstance(age, int) or age <= 0:
        errors.append("age: enter a positive whole number of years.")

    # height_inches / weight_lbs / goal_weight_lbs: positive numbers
    for field in ("height_inches", "weight_lbs", "goal_weight_lbs"):
        value = profile.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            errors.append(f"{field}: enter a positive number.")

    # fitness_goal / activity_level / sex: must be one of the allowed choices
    if profile.get("fitness_goal") not in FITNESS_GOALS:
        errors.append(f"fitness_goal: choose one of {', '.join(FITNESS_GOALS)}.")
    if profile.get("activity_level") not in ACTIVITY_LEVELS:
        errors.append(f"activity_level: choose one of {', '.join(ACTIVITY_LEVELS)}.")
    if profile.get("sex") not in SEXES:
        errors.append("sex: choose male or female.")

    return errors


def check_goal_weight(weight_lbs, goal_weight_lbs, fitness_goal):
    """Check goal weight against the fitness goal.

    Takes in current weight, goal weight, and fitness_goal.
    Returns (passes: bool, message: str).
    Rule: lose -> goal < current; maintain -> goal == current;
    gain -> goal > current. This checks that the answers agree
    with each other, not whether a target is medically appropriate.
    """
    if fitness_goal == "lose weight":
        passes = goal_weight_lbs < weight_lbs
        rule = "goal weight must be below current weight to lose weight"
    elif fitness_goal == "maintain weight":
        passes = goal_weight_lbs == weight_lbs
        rule = "goal weight must equal current weight to maintain weight"
    elif fitness_goal == "gain weight":
        passes = goal_weight_lbs > weight_lbs
        rule = "goal weight must be above current weight to gain weight"
    else:
        return False, "fitness_goal is not one of lose / maintain / gain weight."

    if passes:
        return True, f"Goal weight {goal_weight_lbs} lb fits '{fitness_goal}' at {weight_lbs} lb."
    return False, (
        f"Mismatch: {rule}, but you entered goal {goal_weight_lbs} lb "
        f"at current {weight_lbs} lb. Please correct the goal or the goal weight."
    )


def calculate_bmr(sex, age, height_inches, weight_lbs):
    """Calculate Basal Metabolic Rate with Mifflin-St Jeor.

    Takes in sex, age (years), height (inches), weight (lb).
    Returns BMR in calories/day (before activity).
      male:   10*kg + 6.25*cm - 5*age + 5
      female: 10*kg + 6.25*cm - 5*age - 161
    kg = lb / 2.20462, cm = inches * 2.54.
    """
    weight_kg = weight_lbs / 2.20462
    height_cm = height_inches * 2.54
    if sex == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


def activity_multiplier(activity_level):
    """Return the multiplier for an activity level. Takes in a string, returns a float."""
    return ACTIVITY_MULTIPLIERS[activity_level]


def estimate_maintenance_calories(sex, age, height_inches, weight_lbs, activity_level):
    """Estimate MAINTENANCE daily calories (TDEE).

    Takes in sex, age, height, weight, activity_level.
    Returns estimated calories/day, rounded to the nearest whole calorie.
    This is BMR x activity multiplier — what the user needs to
    maintain their current weight at their usual activity level.
    This is the starting point; estimate_daily_calories() then
    adjusts it for the user's goal.
    """
    bmr = calculate_bmr(sex, age, height_inches, weight_lbs)
    return round(bmr * activity_multiplier(activity_level))


def estimate_daily_calories(sex, age, height_inches, weight_lbs, activity_level, fitness_goal, weight_loss_rate_lb_per_week=1.0):
    """Estimate GOAL-ADJUSTED daily calories — the app's recommended intake.

    Takes in sex, age, height, weight, activity_level, fitness_goal,
    and (lose only) weight_loss_rate_lb_per_week, default 1.0.
    Returns estimated calories/day, rounded to the nearest whole calorie.
    This is maintenance (TDEE) + goal adjustment:
    lose weight -500 per lb/week wanted (-250 / -500 / -750 for
    0.5 / 1.0 / 1.5), maintain weight 0, gain weight +500.
    Example: maintenance 2,925, lose goal -> 2,675 at 0.5, 2,425 at
    1.0, 2,175 at 1.5; gain goal -> 3,425.
    """
    maintenance = estimate_maintenance_calories(
        sex, age, height_inches, weight_lbs, activity_level
    )
    if fitness_goal == "lose weight":
        return maintenance + weight_loss_deficit(weight_loss_rate_lb_per_week)
    return maintenance + GOAL_ADJUSTMENTS[fitness_goal]


def desired_weight_change_pct(weight_lbs, goal_weight_lbs):
    """Desired % weight change. Takes in current and goal weight, returns a float.

    (goal - current) / current * 100. Example: 200 -> 180 lb is -10%,
    150 -> 165 lb is +10%. This is what the user WANTS to change,
    not what they actually lost or gained.
    """
    return (goal_weight_lbs - weight_lbs) / weight_lbs * 100


class UserProfile:
    """One Ascend user profile. The class the app actually uses.

    Takes in the 8 proposal fields. Use .validate() before trusting
    the numbers, then .goal_check(), .estimated_daily_calories,
    and .desired_weight_change_pct for the profile's results.
    .to_dict() adds the two calculated columns for pandas.
    """

    def __init__(self, name, age, height_inches, weight_lbs,
                 fitness_goal, goal_weight_lbs, activity_level, sex,
                 weight_loss_rate_lb_per_week=1.0):
        self.name = name
        self.age = age
        self.height_inches = height_inches
        self.weight_lbs = weight_lbs
        self.fitness_goal = fitness_goal
        self.goal_weight_lbs = goal_weight_lbs
        self.activity_level = activity_level
        self.sex = sex
        # Lose only: 0.5 / 1.0 / 1.5 lb/week, default 1.0. Ignored
        # for maintain / gain. Sample profiles use the default, so
        # Q1-Q3 in analysis.py are unchanged by the slider.
        self.weight_loss_rate_lb_per_week = weight_loss_rate_lb_per_week

    def as_dict(self):
        """Return the 8 input fields as a dict."""
        return {
            "name": self.name,
            "age": self.age,
            "height_inches": self.height_inches,
            "weight_lbs": self.weight_lbs,
            "fitness_goal": self.fitness_goal,
            "goal_weight_lbs": self.goal_weight_lbs,
            "activity_level": self.activity_level,
            "sex": self.sex,
        }

    def validate(self):
        """Return a list of validation errors (empty = valid)."""
        errors = validate_profile(self.as_dict())
        if self.fitness_goal == "lose weight" and self.weight_loss_rate_lb_per_week not in WEIGHT_LOSS_RATES:
            errors.append("weight_loss_rate_lb_per_week: choose 0.5, 1.0, or 1.5 lb/week.")
        return errors

    def goal_check(self):
        """Return (passes, message) for the goal-weight check."""
        return check_goal_weight(self.weight_lbs, self.goal_weight_lbs, self.fitness_goal)

    @property
    def maintenance_calories(self):
        """Maintenance calorie estimate for this profile (before goal adjustment)."""
        return estimate_maintenance_calories(
            self.sex, self.age, self.height_inches, self.weight_lbs, self.activity_level
        )

    @property
    def estimated_daily_calories(self):
        """Goal-adjusted calorie estimate for this profile — the app's recommendation."""
        return estimate_daily_calories(
            self.sex, self.age, self.height_inches, self.weight_lbs,
            self.activity_level, self.fitness_goal,
            self.weight_loss_rate_lb_per_week,
        )

    @property
    def weeks_to_goal(self):
        """Weeks to reach the goal weight at this profile's rate."""
        return weeks_to_goal(
            self.weight_lbs, self.goal_weight_lbs, self.fitness_goal,
            self.weight_loss_rate_lb_per_week,
        )

    @property
    def desired_weight_change_pct(self):
        """Desired % weight change for this profile."""
        return desired_weight_change_pct(self.weight_lbs, self.goal_weight_lbs)

    def to_dict(self):
        """Return inputs + the 2 calculated columns, ready for a DataFrame row."""
        row = self.as_dict()
        row["estimated_daily_calories"] = self.estimated_daily_calories
        row["desired_weight_change_pct"] = round(self.desired_weight_change_pct, 2)
        return row


if __name__ == "__main__":
    # One-profile demo: the 185 lb example from the proposal.
    demo = UserProfile(
        name="Sample User",
        age=20,
        height_inches=72,
        weight_lbs=185,
        fitness_goal="lose weight",
        goal_weight_lbs=176,
        activity_level="moderate",
        sex="male",
    )
    print("Errors:", demo.validate())
    print("Goal check:", demo.goal_check())
    print("Maintenance calories:", demo.maintenance_calories)
    print("Estimated daily calories (goal-adjusted, lose -500 at 1.0 lb/week):", demo.estimated_daily_calories)
    print("Desired change %:", round(demo.desired_weight_change_pct, 2))
    print("Weeks to goal at 1.0 lb/week:", demo.weeks_to_goal)
    for rate in WEIGHT_LOSS_RATES:
        print(f"  at {rate} lb/week: {estimate_daily_calories(demo.sex, demo.age, demo.height_inches, demo.weight_lbs, demo.activity_level, demo.fitness_goal, rate)} cal/day, "
              f"{weeks_to_goal(demo.weight_lbs, demo.goal_weight_lbs, demo.fitness_goal, rate):.0f} weeks")

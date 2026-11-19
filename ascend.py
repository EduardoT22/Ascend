"""
Ascend — MIST 4600 project (DRAFT, pending Eduardo's confirmation)

What this file does, in plain terms:
  1. Takes ONE new user's profile (the 8 inputs from the submitted proposal).
  2. Validates it — is every field filled in, and are the values sensible?
  3. Checks goal weight against the fitness goal — lose < current,
     maintain = current, gain > current.
  4. Estimates daily calories as a GOAL-ADJUSTED target (Eduardo's
     choice, Nov 15, 2026): first Mifflin-St Jeor BMR x an activity
     multiplier = maintenance (TDEE), then adjust for the goal:
     lose weight -500, maintain weight 0, gain weight +500.
     The 500 is a simple, documented rule — about 1 lb/week —
     not a medical recommendation.

Proposal source of truth:
  - name, age, height_inches, weight_lbs, fitness_goal,
    goal_weight_lbs, activity_level, sex
  - fitness_goal: "lose weight" | "maintain weight" | "gain weight"
  - activity_level: "low" | "moderate" | "high"
  - sex: "male" | "female"
  - desired_weight_change_pct = (goal - current) / current * 100
"""

# Activity multipliers for the maintenance estimate.
# low = mostly sedentary, moderate = active most days,
# high = very active. Documented here so the README, app, and
# analysis all use the same numbers.
ACTIVITY_MULTIPLIERS = {
    "low": 1.2,
    "moderate": 1.55,
    "high": 1.725,
}

FITNESS_GOALS = ("lose weight", "maintain weight", "gain weight")
ACTIVITY_LEVELS = ("low", "moderate", "high")
SEXES = ("male", "female")

# Goal adjustment, in calories/day, applied to maintenance (TDEE).
# lose -500, maintain 0, gain +500. Simple and documented.
GOAL_ADJUSTMENTS = {
    "lose weight": -500,
    "maintain weight": 0,
    "gain weight": 500,
}


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


def estimate_daily_calories(sex, age, height_inches, weight_lbs, activity_level, fitness_goal):
    """Estimate GOAL-ADJUSTED daily calories — the app's recommended intake.

    Takes in sex, age, height, weight, activity_level, fitness_goal.
    Returns estimated calories/day, rounded to the nearest whole calorie.
    This is maintenance (TDEE) + goal adjustment:
    lose weight -500, maintain weight 0, gain weight +500.
    Example: maintenance 2,925, lose goal -> 2,425; gain goal -> 3,425.
    """
    maintenance = estimate_maintenance_calories(
        sex, age, height_inches, weight_lbs, activity_level
    )
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
                 fitness_goal, goal_weight_lbs, activity_level, sex):
        self.name = name
        self.age = age
        self.height_inches = height_inches
        self.weight_lbs = weight_lbs
        self.fitness_goal = fitness_goal
        self.goal_weight_lbs = goal_weight_lbs
        self.activity_level = activity_level
        self.sex = sex

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
        return validate_profile(self.as_dict())

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
    print("Estimated daily calories (goal-adjusted, lose -500):", demo.estimated_daily_calories)
    print("Desired change %:", round(demo.desired_weight_change_pct, 2))

"""Quick checks for Ascend — run: python3 test_ascend.py"""
from ascend import UserProfile, check_goal_weight, desired_weight_change_pct

def check(label, actual, expected):
    status = "PASS" if actual == expected else f"FAIL (got {actual}, expected {expected})"
    print(f"{label}: {status}")

# Valid: 185 -> 176 lose
p = UserProfile("Sample", 20, 72, 185, "lose weight", 176, "moderate", "male")
check("valid profile has no errors", p.validate(), [])
check("lose 185->176 passes", check_goal_weight(185, 176, "lose weight")[0], True)
check("maintain 185->185 passes", check_goal_weight(185, 185, "maintain weight")[0], True)
check("gain 185->195 passes", check_goal_weight(185, 195, "gain weight")[0], True)
check("200->180 is -10%", round(desired_weight_change_pct(200, 180), 2), -10.0)
check("150->165 is +10%", round(desired_weight_change_pct(150, 165), 2), 10.0)
check("185lb male 20y 72in moderate maintenance = 2925 cal", p.maintenance_calories, 2925)
check("same profile, lose goal -> 2425 cal (2925 - 500)", p.estimated_daily_calories, 2425)

# Invalid: lose goal but goal weight ABOVE current — must fail with a clear message
passes, msg = check_goal_weight(185, 195, "lose weight")
check("lose 185->195 fails", passes, False)
print("  message:", msg)

# Invalid: blank name, age 0, bad goal, bad activity, bad sex
bad = UserProfile("", 0, 72, 185, "get fit", 176, "extreme", "other")
print("invalid profile errors:", bad.validate())
check("invalid profile has 5 errors", len(bad.validate()), 5)

print("Done.")

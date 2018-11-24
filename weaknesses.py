weaknesses = {
    "squats": {
        "quads": 
            ["https://exrx.net/WeightExercises/Quadriceps/BBRearLunge", "https://exrx.net/WeightExercises/Quadriceps/BWSplitSquat", "https://exrx.net/WeightExercises/Quadriceps/BBFrontSquat", "https://exrx.net/WeightExercises/Quadriceps/BWStepDown", "https://exrx.net/WeightExercises/Quadriceps/BBSideSplitSqaut"],
        "cores": ["https://exrx.net/WeightExercises/RectusAbdominis/BBPushCrunch", "https://exrx.net/WeightExercises/RectusAbdominis/BWCrunch", "https://exrx.net/WeightExercises/RectusAbdominis/DBPushSitUp", "https://exrx.net/WeightExercises/RectusAbdominis/LVVerticalLegHipRaise"],
        "hips": ["https://exrx.net/WeightExercises/GluteusMaximus/BBDeadlift", "https://exrx.net/WeightExercises/GluteusMaximus/BWLunge", "https://exrx.net/WeightExercises/GluteusMaximus/BWSquat", "https://exrx.net/WeightExercises/GluteusMaximus/BBHipThrust", "https://exrx.net/WeightExercises/GluteusMaximus/TBDeadlift"]
    },
    "deadlift": {
        "backs": [
            "https://exrx.net/WeightExercises/TrapeziusUpper/BBShrug", "https://exrx.net/WeightExercises/TrapeziusUpper/CBBarShrug", "https://exrx.net/WeightExercises/TrapeziusUpper/SLXGripShrug", "https://exrx.net/Stretches/TrapeziusUpper/Trap", "https://exrx.net/Lists/ExList/BackWt#UpperTrap"
        ],
        "forearms": ["https://exrx.net/WeightExercises/Brachioradialis/BBReverseCurl", "https://exrx.net/WeightExercises/Brachioradialis/BBReversePreacherCurl", "https://exrx.net/WeightExercises/Brachioradialis/CBHammerCurl", "https://exrx.net/WeightExercises/Brachioradialis/DBHammerCurl", "https://exrx.net/WeightExercises/Brachioradialis/LVHammerPreacherCurl"],
        "upperarms": ["https://exrx.net/WeightExercises/Triceps/ASTriDip", "https://exrx.net/WeightExercises/Triceps/BBCloseGripBenchPress", "https://exrx.net/WeightExercises/Triceps/BBLyingTriExt", "https://exrx.net/WeightExercises/Triceps/CBBentoverTriExt", "https://exrx.net/WeightExercises/Triceps/BWBenchDip", "https://exrx.net/WeightExercises/Triceps/BWTriDip"]
    },
    "bench": {
		"shoulder": ["https://exrx.net/WeightExercises/DeltoidAnterior/BBBehindNeckPress", "https://exrx.net/WeightExercises/DeltoidAnterior/LVReclinedShoulderPress", "https://exrx.net/WeightExercises/DeltoidLateral/BBUprightRow"],
		"triceps": ["https://exrx.net/WeightExercises/Triceps/BBCloseGripBenchPress","https://exrx.net/WeightExercises/Triceps/BWBenchDip","https://exrx.net/WeightExercises/Biceps/BBCurl"],
	}
}

failures = {
    "depth": "You should aim to squat until your hips are lower than your knees"
}

good_lifts = {
    "squat": "Great squat! Form is looking solid.",
    "deadlift": "Great deadlift! Keep it up!",
    "bench": "Solid bench! It's looking strong."
}

if __name__ == "__main__":
    somestring = "you have weak Quads, upperarms"
    # string.find("weak") = get of k
    # 
    def tips_for_exercises(somestring):
        somestring = somestring.lower()
        if "weak" in somestring: 
            tips = []
            new_string = somestring[somestring.find("weak"):]
            if len(new_string) > 0:
                for exercise in weaknesses.keys():
                    for bodypart in weaknesses[exercise].keys():
                        if new_string.find(bodypart) > 0:
                            tips.append({bodypart: weaknesses[exercise][bodypart]})
        return tips

    print(tips_for_exercises(somestring))



import os
from datetime import date

from .logistic_regression import LogisticRegression


def calculate_age(dob, today=None):

    if today is None:
        today = date.today()

    age = today.year - dob.year

    if (today.month, today.day) < (dob.month, dob.day):
        age -= 1

    return age


def predict_no_show(
    age,
    date_diff,
    day_of_week,
    previous_missed,
    previous_completed
):

    model = LogisticRegression()

    base_dir = os.path.dirname(__file__)

    weights_path = os.path.join(
        base_dir,
        "weights.txt"
    )

    normalization_path = os.path.join(
        base_dir,
        "normalization.txt"
    )

    # Load learned weights and bias
    model.load_weights(weights_path)

    # Load training normalization values
    with open(normalization_path, "r") as file:

        values = [
            float(line.strip())
            for line in file
            if line.strip()
        ]

    min_age = values[0]
    max_age = values[1]

    min_date = values[2]
    max_date = values[3]

    min_day = values[4]
    max_day = values[5]

    min_missed = values[6]
    max_missed = values[7]

    min_completed = values[8]
    max_completed = values[9]

    # Normalize using TRAINING values

    age = (
        age - min_age
    ) / (max_age - min_age)

    date_diff = (
        date_diff - min_date
    ) / (max_date - min_date)

    day_of_week = (
        day_of_week - min_day
    ) / (max_day - min_day)

    previous_missed = (
        previous_missed - min_missed
    ) / (max_missed - min_missed)

    previous_completed = (
        previous_completed - min_completed
    ) / (max_completed - min_completed)

    features = [
        age,
        date_diff,
        day_of_week,
        previous_missed,
        previous_completed
    ]

    probability = model.predict_probability(
        features
    )

    prediction = model.predict(
        features
    )

    return probability, prediction
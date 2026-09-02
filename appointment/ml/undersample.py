import csv
import random

# Input and output files
INPUT_FILE = "training_dataset.csv"
OUTPUT_FILE = "training_dataset_balanced.csv"


# Read the original training dataset
with open(INPUT_FILE, "r", newline="") as file:

    reader = csv.reader(file)

    # Store column names
    header = next(reader)

    # Store all data rows
    rows = list(reader)


# Separate the two classes
# 0 = patient attends
# 1 = patient no-shows

attend_rows = []
no_show_rows = []

for row in rows:

    target = int(row[5])

    if target == 0:
        attend_rows.append(row)

    elif target == 1:
        no_show_rows.append(row)


# Display original class distribution

print("Original dataset")
print("----------------------------")
print("Attend:", len(attend_rows))
print("No-show:", len(no_show_rows))


# Undersample the majority class
#
# We keep all no-show records and randomly
# select the same number of attend records.

random.seed(42)

sample_size = len(no_show_rows)

attend_sample = random.sample(
    attend_rows,
    sample_size
)


# Combine the balanced classes

balanced_rows = attend_sample + no_show_rows


# Shuffle the dataset

random.shuffle(balanced_rows)


# Save the balanced dataset

with open(
    OUTPUT_FILE,
    "w",
    newline=""
) as file:

    writer = csv.writer(file)

    # Write column names
    writer.writerow(header)

    # Write balanced records
    writer.writerows(balanced_rows)


# Display final distribution

print()
print("Balanced dataset")
print("----------------------------")
print("Attend:", len(attend_sample))
print("No-show:", len(no_show_rows))
print("Total:", len(balanced_rows))

print()
print("Balanced dataset saved to:")
print(OUTPUT_FILE)
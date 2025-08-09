import csv

with open("referrals_log.csv", mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow([
        "Timestamp", "Email", "Phone", "21 or Older?",
        "Condition", "Appointment Type", "Other Info"
    ])

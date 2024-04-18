import csv

def loadTasks():
    tasks = []
    tasksheet = input("Enter Task Sheet Name:\n")
    reader = csv.DictReader(open( tasksheet + '.csv'))
    for row in reader:
        tasks.append(row)
    return tasks
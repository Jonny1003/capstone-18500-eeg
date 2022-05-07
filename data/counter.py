import os 

DIR = "./compiled"

print(os.listdir("./compiled"))

count = 0
for folder in os.listdir(DIR):
    dir = DIR + '/' + folder
    if os.path.isdir(dir):
        count += len(os.listdir(dir))

print(count)
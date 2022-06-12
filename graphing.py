import pandas as pd

columns = ['username']

# import the usernames
usernames = pd.read_csv("messages.csv", usecols=columns)

# count how many of each username appear. this gives us a message count
s = usernames['username'].value_counts().rename('Total messages')
# add the counts back to the list
usernames = usernames.join(s, on='username')

print(usernames.head)

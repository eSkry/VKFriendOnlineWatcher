import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import sqlite3

select_time_by_user = "SELECT ((strftime('%H', begin_online, 'unixepoch', 'localtime') * 60) + strftime('%M', begin_online, 'unixepoch', 'localtime')) as start, (strftime('%H', end_online, 'unixepoch', 'localtime') * 60 + strftime('%M', end_online, 'unixepoch', 'localtime')) as end FROM statistics WHERE user_id = {}"
select_users = "SELECT user_id, full_name FROM vk_users"
conn = sqlite3.connect('../db.db')

matplotlib.rcParams.update({'font.size': 12})

users_d = conn.execute(select_users).fetchall()
users = []

for i in users_d:
    users.append(i[1])

metrics = np.full((len(users), 1440), 0)

_idx = 0
for i in users_d:
    users.append(i[1])
    usrmtr = conn.execute( select_time_by_user.format(i[0]) )

    for mtr in usrmtr:
        if mtr[1] == None:
            continue
        for idx in range( int(mtr[0]), int(mtr[1]) ):
            metrics[_idx, idx] += 1

    _idx += 1


time_st = []

# for tm in range(1440):
#     hours = tm / 60
#     mins = tm % 60
#     time_st.append( '{}:{}'.format(hours, mins) )


# fig, ax = plt.subplots(figsize=(6, 6))
fig, ax = plt.subplots()
fig.set_size_inches(26, 18)
im = ax.imshow(metrics, extent=[0,1439,0,len(users)], aspect='auto', interpolation='nearest')

# We want to show all ticks...
ax.set_xticks(np.arange(1440))
ax.set_yticks(np.arange(len(users)))
# ... and label them with the respective list entries
ax.set_xticklabels(time_st)
ax.set_yticklabels(users)

# Rotate the tick labels and set their alignment.
# plt.setp(ax.get_xticklabels(), rotation=90, ha="right",
#          rotation_mode="anchor")

plt.savefig('foo.png', bbox_inches='tight', dpi=100)

# Loop over data dimensions and create text annotations.
# for i in range(len(users)):
#     for j in range(len(time_st)):
#         text = ax.text(j, i, metrics[j, i],
#                        ha="center", va="center", color="w")

# fig.tight_layout()
# plt.show()
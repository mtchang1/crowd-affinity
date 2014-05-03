import sqlite3
conn = sqlite3.connect('database test 1.db')
c = conn.cursor()

#question tree structure
#compare starting point to ending point
#how true are the ratings compared with expert ratings
#what questions had the best results

# for i in range(1,24):
# 	c.execute('SELECT * FROM crowd_affinity_answer WHERE question_id =?', i)
# 	print c.fetchone()

for row in c.execute('SELECT parent_id,question_text FROM crowd_affinity_question ORDER BY parent_id'):
	print row
        # print c.execute('SELECT parent_id FROM crowd_affinity_question ORDER BY id'):
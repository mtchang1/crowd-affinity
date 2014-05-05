import pprint
import sqlite3
conn = sqlite3.connect('database test 1.db')
c = conn.cursor()


#compare starting point to ending point
#how true are the ratings compared with expert ratings
#what questions had the best results

# for i in range(1,24):
# 	c.execute('SELECT * FROM crowd_affinity_answer WHERE question_id =?', i)
# 	print c.fetchone()

answers = []
for answer in c.execute('SELECT * FROM crowd_affinity_answer ORDER BY question_id'):
	answers.append(answer)

questionTree = {}
for question in c.execute('SELECT * FROM crowd_affinity_question ORDER BY parent_id'):
	if int(question[2]) == 0: 
		questionTree[question[0]] = {'Question':question[1],'Answers':[[answer[0], answer[4]/(answer[5]+.0001), answer[2]] for answer in answers if answer[1]== question[0]]}
	if question[3] in questionTree:
		questionTree[question[3]][question[0]] = {'Question':question[1], 'Answers':[[answer[0], answer[4]/(answer[5]+.0001), answer[2]] for answer in answers if answer[1]== question[0]]}

#question tree structure
pprint.pprint(questionTree, depth=10)
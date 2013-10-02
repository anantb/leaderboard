import csv, sys

'''
@author: Anant Bhardwaj
@date: Sep 22, 2013
'''

gold = {}

f = open(sys.argv[2], 'rU')
reader = csv.reader(f)
reader.next()
for row in reader:
    gold[row[0]] = row[1]




def compute_score(file_name):
    count = 0
    correct_ans = []
    precision = 0.0
    recall = 0.0
    try:
        f = open(file_name, 'rU')
        reader = csv.reader(f)
        reader.next()
        for row in reader:
            count += 1
            try:
                if(gold[row[0]] == row[1]):
                    correct_ans.append(row[0])
            except:
                pass

        precision = float(len(correct_ans)) / count
        recall = float(len(set(correct_ans))) / len(gold.keys())
        f1 = 2 * (precision * recall) / (precision + recall)
    except:
        pass
    return [precision, recall, f1]


print compute_score(sys.argv[1])

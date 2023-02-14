import pandas as pd
import sqlite3


con = sqlite3.connect('multi_db.db')

df = pd.read_sql_query(sql='SELECT * FROM multiplication', con=con)
df1 = df[df.user_id == 1].groupby(["a", "b"],as_index=False).agg({'duration':'mean', 'result' : 'mean'}).sort_values(by='duration', ascending=False)
df1 = df1[(df1.duration >= df1.duration.quantile(q=0.65)) | (df1.result <=0.75)]
a_list = df1.a.to_list()
b_list = df1.b.to_list()
all_examples = list(map(lambda a, b: [a, b], a_list, b_list))

for example in all_examples:
    while True:
        try:
            start_time = datetime.datetime.now()
            example.append(int(input(f"{example[0]} * {example[1]} = ")))
            example.append((datetime.datetime.now() - start_time).total_seconds())
            if example[0] * example[1] == example[2]:
                example.append(1)
            else:
                example.append(0)
            break
        except:
            print("Not correct input")
    # print(example)
    to_sql(user_id, session_id, example[0], example[1], example[2], example[3], example[4])
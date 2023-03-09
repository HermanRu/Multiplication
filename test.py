import pandas as pd
import sqlite3
import plotly.express as px
from matplotlib import pyplot as plt
import os
from tabulate import tabulate

con = sqlite3.connect('database/multi_db.db')

df = pd.read_sql_query(sql='SELECT * FROM multiplication', con=con)
df_t = df.groupby('user_id').agg({'duration':['min','max','mean','median','std','sum','count']})
df_t.columns= ['min','max','mean','median','std','sum','count']
df_t = df_t.reset_index().round(decimals = 1)
print(tabulate(df_t, headers="keys", tablefmt='psql'))

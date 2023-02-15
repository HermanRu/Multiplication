import pandas as pd
import sqlite3
import plotly.express as px
from matplotlib import pyplot as plt
import os


con = sqlite3.connect('multi_db.db')

df = pd.read_sql_query(sql='SELECT * FROM multiplication', con=con)

fig1 = px.density_heatmap(df[df.user_id == 1], x='a', y='b', z="duration", histfunc="avg",
                         nbinsx=9, nbinsy=9, text_auto='.1f', height=500, width=600)
fig2 = px.density_heatmap(df[df.user_id == 1], x='a', y='b', z="result", histfunc="avg",
                         nbinsx=9, nbinsy=9, text_auto='.1f', height=500, width=600)
fig1.update_xaxes(dtick=1)
fig1.update_yaxes(dtick=1)
fig2.update_xaxes(dtick=1)
fig2.update_yaxes(dtick=1)

fig1.write_image("duration_heatmap_tmp.png")
fig2.write_image("result_heatmap_tmp.png")

# img = plt.imread('density_heatmap_tmp.png')
# plt.imshow(img)
# plt.show()

# os.startfile("duration_heatmap_tmp.png")
# os.startfile("result_heatmap_tmp.png")


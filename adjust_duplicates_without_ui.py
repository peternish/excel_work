import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np

def load_excel():
    global df
    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
    if file_path:
        df = pd.read_excel(file_path)
        #process the data
        for i in df:
            for j in df[i]:
                same_value_positions = np.where(df.values == j)
                if same_value_positions[0].size >= 2:
                    for k in range(1,len(same_value_positions[0])):
                        dot_arr = '.' * k
                        l = [same_value_positions[0][k], same_value_positions[1][k]]
                        df[df.columns[l[1]+1]][l[0]] = f'{j}{dot_arr}'
        df.to_excel("output.xlsx", index=False)  # Provide the desired file name and path                
load_excel()
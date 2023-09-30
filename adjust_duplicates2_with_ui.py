import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np

def load_excel():
    global df
    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
    if file_path:
        df = pd.read_excel(file_path)
        label_load.pack()
def process_excel():
    label_load.pack_forget()
    for i in df.columns:
        for j in df[i]:
            same_value_positions = np.where(df.values == j)
            if same_value_positions[0].size >= 2:
                for k in range(1, len(same_value_positions[0])):
                    dot_arr = '.' * k
                    l = [same_value_positions[0][k], same_value_positions[1][k]]
                    df.iat[l[0], l[1]+1] = f'{j}{dot_arr}'
    df.to_excel("output.xlsx", index=False)
    label_done.pack()
root = tk.Tk()
root.geometry('700x400')
button = tk.Button(root, text="Load Excel", command=load_excel, font=('sans', 16))
button.pack(pady=20)
label_load = tk.Label(root, text="Excel file loaded", font=('sans', 16))
button = tk.Button(root, text="Process it", command=process_excel, font=('sans', 16))
button.pack(pady=20)
label_done = tk.Label(root, text="Process Done", font=('sans', 16))
root.mainloop()
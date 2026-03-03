Pandas DataFrame Selection Cheatsheet

iloc - Integer Position Based (0-indexed)

# Single cell

df.iloc[0, 0]          # Row 0, Col 0 (first cell)
df.iloc[2, 5]          # Row 2, Col 5

# Single row/col

df.iloc[0]             # Entire first row (as Series)
df.iloc[:, 0]          # Entire first column (as Series)

# Ranges (slicing) - [start:end] where end is EXCLUSIVE

df.iloc[0:5]           # Rows 0-4 (5 rows)
df.iloc[:, 0:3]        # Columns 0-2 (3 columns)
df.iloc[0:5, 0:3]      # Rows 0-4, Cols 0-2 (5x3 slice)

# Specific selections (non-contiguous)

df.iloc[[0, 3, 5]]     # Rows 0, 3, 5
df.iloc[:, [0, 2, 4]]  # Columns 0, 2, 4
df.iloc[[0, 2], [1, 3]] # Rows 0 & 2, Cols 1 & 3

# Negative indexing

df.iloc[-1]            # Last row
df.iloc[:, -1]         # Last column
df.iloc[-5:]           # Last 5 rows
df.iloc[:, -3:]        # Last 3 columns
---------------------------------------

loc - Label Based

# Single cell (uses row index & column NAMES)

df.loc[0, 'col_name']  # Row index 0, column 'col_name'
df.loc[0, :]           # Row 0, all columns

# By row label (if index is not default 0,1,2...)

df.loc['row_label']

# Slicing by label (end is INCLUSIVE)

df.loc[0:5]            # Rows 0 through 5 (labels)
df.loc[:, 'col_a':'col_c']  # Columns 'col_a' through 'col_c'

# Conditional selection

df.loc[df['col'] > 10]
df.loc[df['col'] == 'value', ['col_a', 'col_b']]
------------------------------------------------

Quick Reference Table

| Goal            | Syntax                                     |
| --------------- | ------------------------------------------ |
| Single cell     | df.iloc[0, 0] or df.loc[0, 'col']          |
| Row 0           | df.iloc[0] or df.loc[0]                    |
| Column "A"      | df.iloc[:, 0] or df['A'] or df.loc[:, 'A'] |
| Rows 0-9        | df.iloc[0:10]                              |
| Cols A-C        | df.iloc[:, 0:3]                            |
| Row 0, Col A    | df.iloc[0, 0]                              |
| Every other row | df.iloc[::2]                               |
| Last 5 rows     | df.iloc[-5:]                               |

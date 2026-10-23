import pandas as pd

# 1. CSV ko DataFrame me load karo
df = pd.read_csv("data/Training.csv")

# 2. Shape: (rows, columns)
print("Shape:", df.shape)

# 3. Pehle 3 rows
print(df.head(3))

# 4. Columns ke naam (last wala target hoga)
print("Columns:", list(df.columns[:5]), "...", list(df.columns[-3:]))

# 5. Missing values
print("Missing values per column (sirf wo jinme hain):")
missing = df.isnull().sum()
print(missing[missing > 0])

# 6. Target column: kitne diseases, har ek ki kitni rows
print("Number of diseases:", df["prognosis"].nunique())
print(df["prognosis"].value_counts().head(10))

# 7. Duplicate rows
print("Duplicate rows:", df.duplicated().sum())
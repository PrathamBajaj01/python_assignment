import json
import re
import os
import pandas as pd
from sqlalchemy import create_engine, text
import pymysql
from urllib.parse import quote_plus


JSON_FILENAME = "sample_data_for_assignment.json"
DB_NAME = "json_assignment_db"
TABLE_NAME = "json_to_sql_table"

DB_USER = "root"
DB_PASS = "dataGrokr@23"
DB_HOST = "localhost"
DB_PORT = 3306
auth_user = quote_plus(DB_USER)
auth_pass = quote_plus(DB_PASS)

ENGINE_URL = f"mysql+pymysql://{auth_user}:{auth_pass}@{DB_HOST}:{DB_PORT}/"


def load_json_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize_cols(cols):
    if not cols:
        return []
    if all(isinstance(c, str) for c in cols):
        return cols
    names = []
    for c in cols:
        if isinstance(c, dict):
            for k in ("name", "col", "column", "title"):
                if k in c:
                    names.append(str(c[k]))
                    break
            else:
                names.append(str(c))
        else:
            names.append(str(c))
    return names

def rows_to_dataframe(cols, data):
    if not data:
        return pd.DataFrame(columns=cols)
    if isinstance(data[0], dict):
        df = pd.DataFrame(data)
        for c in cols:
            if c not in df.columns:
                df[c] = pd.NA
        return df[cols]
    return pd.DataFrame(data, columns=cols)

def create_database_and_table(engine, db_name, table_name, df):
    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}`"))
    engine_db = create_engine(ENGINE_URL + db_name)
    df.to_sql(table_name, con=engine_db, if_exists="replace", index=False, method='multi')
    return engine_db

def phone_to_ascii_code(phone_value: str) -> str:
    if phone_value is None:
        return ""
    s = str(phone_value)
    digits = re.sub(r"\D", "", s)
    coded_chars = []
    for i in range(0, len(digits) - 1, 2):
        pair = digits[i:i+2]
        if len(pair) < 2:
            break
        try:
            val = int(pair)
        except:
            coded_chars.append("O")
            continue
        if val < 65:
            coded_chars.append("O")
        else:
            coded_chars.append(chr(val))
    return "".join(coded_chars)

def main():
    if not os.path.exists(JSON_FILENAME):
        raise FileNotFoundError(f"{JSON_FILENAME} not found.")
    j = load_json_file(JSON_FILENAME)
    cols_raw = j.get("cols") or j.get("columns") or list(j.get("data", [{}])[0].keys() if j.get("data") else [])
    data_raw = j.get("data", [])
    cols = normalize_cols(cols_raw)
    df = rows_to_dataframe(cols, data_raw)
    print("Initial DataFrame (first 5 rows):")
    print(df.head())

    engine = create_engine(ENGINE_URL)
    engine_db = create_database_and_table(engine, DB_NAME, TABLE_NAME, df)
    print(f"Data inserted into {DB_NAME}.{TABLE_NAME}")

    with engine_db.connect() as conn:
        df_db = pd.read_sql_table(TABLE_NAME, conn)

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 200)
    print("\nUnloaded DataFrame (first 5 rows):")
    print(df_db.head())
    print("\nFull DataFrame shape:", df_db.shape)

    if "email" in df_db.columns:
        df_db["email"] = df_db["email"].astype(str).fillna("") \
            .apply(lambda x: (x.split("@")[0] if "@" in x else x).strip()) \
            .replace("", "abc") + "@gmail.com"

    if "postalZip" in df_db.columns:
        df_db["postalZip_clean"] = df_db["postalZip"].astype(str).fillna("") \
            .apply(lambda s: re.sub(r"[^0-9]", "", s))
        df_db["postalZip_clean"] = pd.to_numeric(df_db["postalZip_clean"], errors="coerce").fillna(0).astype(int)
        df_db["postalZip"] = df_db["postalZip_clean"]
        df_db.drop(columns=["postalZip_clean"], inplace=True)

    if "phone" in df_db.columns:
        df_db["coded_phone_number"] = df_db["phone"].apply(phone_to_ascii_code)
        df_db.drop(columns=["phone"], inplace=True)

    print("\nFinal transformed DataFrame (first 10 rows):")
    print(df_db.head(10))

    
    # with engine_db.connect() as conn:
    #     df_db.to_sql(TABLE_NAME, conn, if_exists="replace", index=False, method='multi')
    #     print(f"Cleaned data written back to {DB_NAME}.{TABLE_NAME}")

if __name__ == "__main__":
    main()

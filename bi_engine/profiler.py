import pandas as pd


def profile_dataset(df):
    """
    Analyse automatiquement la structure du dataset.
    """

    profile = {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "data_types": {},
        "missing_values": {},
        "duplicates": int(df.duplicated().sum()),
        "numeric_columns": [],
        "categorical_columns": [],
        "date_columns": []
    }

    for column in df.columns:
        profile["data_types"][column] = str(df[column].dtype)

        missing = int(df[column].isna().sum())
        profile["missing_values"][column] = missing

        if pd.api.types.is_numeric_dtype(df[column]):
            profile["numeric_columns"].append(column)

        else:
            converted_dates = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            if converted_dates.notna().mean() > 0.8:
                profile["date_columns"].append(column)
            else:
                profile["categorical_columns"].append(column)

    return profile
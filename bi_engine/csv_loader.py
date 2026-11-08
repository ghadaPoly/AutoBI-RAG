import pandas as pd
from io import BytesIO


def load_csv(file):
    """
    Charge un CSV en essayant plusieurs séparateurs
    et encodages courants.
    """

    separators = [",", ";", "\t"]
    encodings = ["utf-8", "utf-8-sig", "latin-1"]

    errors = []

    for encoding in encodings:
        for separator in separators:
            try:
                if hasattr(file, "seek"):
                    file.seek(0)

                df = pd.read_csv(
                    file,
                    sep=separator,
                    encoding=encoding
                )

                # Évite d'accepter un fichier dont
                # toutes les colonnes sont fusionnées.
                if len(df.columns) > 1:
                    df.columns = [
                        str(col).strip()
                        for col in df.columns
                    ]
                    return df

            except Exception as error:
                errors.append(str(error))

    raise ValueError(
        "Impossible de lire ce CSV. "
        "Vérifiez son séparateur et son encodage."
    )
import os
import pandas as pd
import mysql.connector
import numpy as np
from urllib.parse import urlparse

# Obtener la URL de conexión desde la variable de entorno
db_url = os.getenv("DATABASE_URL")  # o el nombre que hayas puesto

print(db_url)
# Parsear la URL
parsed = urlparse(db_url)

db_config = {
    "host": parsed.hostname,
    "user": parsed.username,
    "password": parsed.password,
    "database": parsed.path.lstrip("/"),
    "port": parsed.port
}

# Cargar los datos desde el archivo Excel
file_path = 'techniques-copia.xlsx'  # Si el archivo está en la misma carpeta que el script
df_pasos = pd.read_excel(file_path, sheet_name='Pasos')

# Limpiar los nombres de columnas de posibles espacios extra
df_pasos.columns = df_pasos.columns.str.strip()

# Reemplazar NaN por None para que MySQL pueda manejarlos como NULL
df_pasos = df_pasos.replace({np.nan: None})

try:
    # Conexión a la base de datos MySQL
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Crear la tabla 'Techniques_Steps' si no existe
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS techniques_steps (
        id INT PRIMARY KEY,
        technique_id INT,
        step_number INT NULL,
        instruction TEXT NULL,
        url VARCHAR(225) NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (technique_id) REFERENCES Techniques(id) ON DELETE CASCADE
    )
    """)

    # Query de inserción para la tabla 'Techniques_Steps'
    insert_query = """
    INSERT INTO techniques_steps (id, technique_id, step_number, instruction, url)
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE step_number=VALUES(step_number), instruction=VALUES(instruction), url=VALUES(url);
    """

    # Insertar datos con lógica condicional
    for _, row in df_pasos.iterrows():
        if row["technique_type"] == "BREATHING":
            cursor.execute(insert_query, (row["id"], row["technique_id"], row["step_number"], row["instruction"], None))
        elif row["technique_type"] in ["MINDFULNESS", "MUSICTHERAPY"]:
            cursor.execute(insert_query, (row["id"], row["technique_id"], None, None, row["url"]))

    # Confirmar cambios en la base de datos
    conn.commit()
    print("Datos insertados correctamente en la tabla 'Techniques_Steps'.")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    cursor.close()
    conn.close()

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
file_path = 'techniques.xlsx'  # Si el archivo está en la misma carpeta que el script
df_tecnicas = pd.read_excel(file_path, sheet_name='Tecnicas')

# Limpiar los nombres de columnas de posibles espacios extra
df_tecnicas.columns = df_tecnicas.columns.str.strip()

# Reemplazar NaN por None para que MySQL pueda manejarlos como NULL
df_tecnicas = df_tecnicas.replace({np.nan: None})

try:
    # Conexión a la base de datos MySQL
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Crear la tabla 'Techniques' si no existe
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Techniques (
        id INT PRIMARY KEY,
        name VARCHAR(255),
        description TEXT,
        type ENUM('BREATHING', 'MINDFULNESS', 'MUSICTHERAPY') NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """)

    # Insertar datos en la tabla 'Techniques'
    insert_query = """
    INSERT INTO Techniques (id, name, description, type)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE name=VALUES(name), description=VALUES(description), type=VALUES(type);
    """

    for _, row in df_tecnicas.iterrows():
        cursor.execute(insert_query, (row["id"], row["name"], row["description"], row["type"]))

    # Confirmar cambios en la base de datos
    conn.commit()
    print("Datos insertados correctamente en la tabla 'Techniques'.")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    cursor.close()
    conn.close()

import os
import mysql.connector
from urllib.parse import urlparse

# Obtener la URL de conexión desde variable de entorno (como DATABASE_URL en Railway)
db_url = os.getenv("DATABASE_URL")
parsed = urlparse(db_url)

# Conexión
conn = mysql.connector.connect(
    host=parsed.hostname,
    user=parsed.username,
    password=parsed.password,
    database=parsed.path.lstrip("/"),
    port=parsed.port
)

cursor = conn.cursor()

# Renombrar tablas
try:
    
        # Eliminar tablas
    cursor.execute("DROP TABLE IF EXISTS techniques;")
    cursor.execute("DROP TABLE IF EXISTS techniques_Steps;")
    
    cursor.execute("RENAME TABLE Techniques TO techniques;")
    cursor.execute("RENAME TABLE Techniques_Steps TO techniques_Steps;")

    conn.commit()
    print("Tablas renombradas y eliminadas correctamente.")
except mysql.connector.Error as err:
    print("Error al ejecutar las operaciones:", err)
finally:
    cursor.close()
    conn.close()
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import hashlib
import os

app = Flask(__name__)

CORS(app)

db_config = {
    'host': 'database-1.ct46qcwkcp2t.us-west-2.rds.amazonaws.com',
    'user': 'postgres',
    'password': 'PlumSQL113.',
    'database': 'postgres'
}

def get_db_connection():
    connection = psycopg2.connect(**db_config)
    connection.cursor_factory = psycopg2.extras.RealDictCursor
    return connection

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/api/users', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        nombre = data['nombre']
        apellido = data['apellido']
        correo = data['correo']
        telefono = data['telefono']
        rut = data['rut']
        password = data['password']
        rol = data['rol']

        if not all([nombre, apellido, correo, telefono, rut, password, rol]):
            return jsonify({"error": "Todos los campos son requeridos"}), 400

        password_hash = hash_password(password)

        connection = get_db_connection()
        cursor = connection.cursor()

        insert_query = """
            INSERT INTO usuarios (nombre, apellido, correo, telefono, rut, password_hash, rol)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (nombre, apellido, correo, telefono, rut, password_hash, rol))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({"message": "Usuario registrado exitosamente"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        usuario = data['usuario']
        password = data['password']

        connection = get_db_connection()
        cursor = connection.cursor()

        query = "SELECT * FROM usuarios WHERE correo = %s"
        cursor.execute(query, (usuario,))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user is None:
            return jsonify({"error": "Usuario no encontrado"}), 404

        password_hash = hash_password(password)
        if password_hash != user['password_hash']:
            return jsonify({"error": "Contraseña incorrecta"}), 401

        return jsonify({"message": "Login exitoso", "user": user}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

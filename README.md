# BlockArtMx

Aplicación web para el **registro de obras** utilizando una **mini-blockchain** para garantizar
la integridad de la información y simular un registro de propiedad intelectual.

La app permite:
- Registrar usuarios.
- Iniciar sesión.
- Registrar nuevas obras (con subida de archivos).
- Consultar las obras registradas por cada usuario.
- Verificar la integridad de la cadena de bloques.
- Simular un ataque/modificación a la blockchain para mostrar la corrupción de datos.


## Estructura del proyecto

REGISTRO-IP-BLOCKCHAIN/
├── Logo/
│   └── blockartmx_Logo.png
├── static/
│   └── style.css
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── detalle_obra.html
│   ├── index.html
│   ├── login.html
│   ├── mis_obras.html
│   ├── nueva_obra.html
│   ├── register.html
│   ├── simular_ataque.html
│   └── verificar.html
├── uploads/
│   ├── user_1/
│   └── user_2/
├── app.py
├── blockchain.py
├── blockchain.json
├── config.py
├── requirements.txt
└── README.md

# Instalación
Clona o copia el proyecto en tu equipo:
git clone https://github.com/MiguelReaG/BlockArtMx.git
cd REGISTRO-IP-BLOCKCHAIN

O descarga el ZIP del repo

# Instala las dependencias
pip install -r requirements.txt

# Ejecución de la aplicación
python app.py

# Por defecto, Flask se ejecutará en:

http://127.0.0.1:5000

o

http://localhost:5000

Luego podrás acceder a:

/ → Página de inicio (index.html)

/register → Registro de usuario

/login → Inicio de sesión

/dashboard → Panel principal del usuario

/nueva_obra → Formulario para registrar una nueva obra

/mis_obras → Lista de obras del usuario

/verificar → Verificación de la cadena de bloques

/simular_ataque → Simulación de ataque/modificación a la blockchain


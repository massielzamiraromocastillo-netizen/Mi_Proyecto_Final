import html
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs


PRODUCTOS = {
    "flor-japon": {
        "nombre": "Jabón de Flor de Japón",
        "precio": 45000,
        "navidad": True,
    },
    "cafe-vainilla-canela": {
        "nombre": "Jabón exfoliante de café, vainilla y canela",
        "precio": 45000,
        "navidad": True,
    },
    "carbon-arcilla": {
        "nombre": "Jabón de carbón activado y arcilla blanca",
        "precio": 45000,
        "navidad": False,
    },
    "avena-lavanda": {
        "nombre": "Jabón de avena y lavanda",
        "precio": 45000,
        "navidad": True,
    },
    "manzanilla-mandarina": {
        "nombre": "Jabón de manzanilla y mandarina",
        "precio": 45000,
        "navidad": False,
    },
    "sandia-pepino": {
        "nombre": "Jabón de sandía y pepino",
        "precio": 45000,
        "navidad": False,
    },
    "maracuya": {
        "nombre": "Jabón de maracuyá",
        "precio": 45000,
        "navidad": False,
    },
    "mandarina": {
        "nombre": "Jabón de mandarina",
        "precio": 45000,
        "navidad": False,
    },
    "te-verde-mandarina": {
        "nombre": "Jabón de té verde y mandarina",
        "precio": 45000,
        "navidad": False,
    },
    "naranja": {
        "nombre": "Jabón de naranja",
        "precio": 45000,
        "navidad": False,
    },
    "estropajabon": {
        "nombre": "Estropajabón corporal",
        "precio": 15000,
        "navidad": False,
    },
    "set-regalo": {
        "nombre": "Set de regalo de 4 jabones artesanales",
        "precio": 165000,
        "navidad": False,
    },
    "jabonera": {
        "nombre": "Jabonera artesanal de madera",
        "precio": 16000,
        "navidad": False,
    },
}

CODIGO_NAVIDAD = "NAVIDAD10"


def pesos(valor):
    """Convierte un valor a pesos colombianos."""
    return "$" + f"{valor:,.0f}".replace(",", ".")


def calcular_pedido(seleccionados, cantidades, codigo):
    """Calcula el pedido conservando las reglas originales."""

    if not seleccionados:
        raise ValueError("Marca al menos un producto para calcular el pedido.")

    subtotal = 0
    descuento = 0
    unidades = 0
    subtotal_productos_navidad = 0
    detalle_productos = []

    for id_producto in seleccionados:

        producto = PRODUCTOS.get(id_producto)

        if producto is None:
            raise ValueError("Hay un producto que no reconozco.")

        try:
            cantidad = int(cantidades.get(id_producto, ""))
        except (TypeError, ValueError):
            raise ValueError(
                "Escribe una cantidad válida para cada producto marcado."
            )

        if cantidad < 1:
            raise ValueError(
                "La cantidad debe ser de al menos una unidad."
            )

        subtotal_linea = producto["precio"] * cantidad

        subtotal += subtotal_linea
        unidades += cantidad

        detalle_productos.append(
            f"{cantidad} × {producto['nombre']}"
        )

        if producto["navidad"]:
            subtotal_productos_navidad += subtotal_linea

    codigo = codigo.strip().upper()

    if codigo == CODIGO_NAVIDAD:
        descuento = subtotal_productos_navidad * 10 // 100

        if descuento:
            mensaje = (
                "Código NAVIDAD10 aplicado a los jabones participantes."
            )
        else:
            mensaje = (
                "El pedido no incluye jabones participantes en la promoción."
            )

    elif codigo:
        mensaje = "El código no es válido; se calculó sin descuento."

    else:
        mensaje = "Pedido calculado."

    return {
        "productos": detalle_productos,
        "unidades": unidades,
        "subtotal": subtotal,
        "descuento": descuento,
        "total": subtotal - descuento,
        "mensaje": mensaje,
    }


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.enviar_pagina(
            "<h2>Calculadora de Massiel Romo Essential Care</h2>"
            "<p>Ingresa a la página principal para realizar tu pedido.</p>"
            "<a href='/#calculadora'>Volver a la calculadora</a>"
        )

    def do_POST(self):

        longitud = int(self.headers.get("Content-Length", 0))
        datos = self.rfile.read(longitud).decode("utf-8")
        formulario = parse_qs(datos)

        if formulario.get("accion", [""])[0] == "limpiar":
            self.enviar_pagina(
                "<h2>Pedido limpiado</h2>"
                "<p>Puedes regresar a la calculadora para comenzar de nuevo.</p>"
                "<a href='/#calculadora'>Volver a la calculadora</a>"
            )
            return

        seleccionados = formulario.get("productos", [])
        codigo = formulario.get("codigo", [""])[0]

        cantidades = {
            id_producto: formulario.get(
                f"cantidad_{id_producto}", [""]
            )[0].strip()
            for id_producto in PRODUCTOS
        }

        try:
            resultado = calcular_pedido(
                seleccionados,
                cantidades,
                codigo,
            )

            lista_productos = "".join(
                f"<li>{html.escape(producto)}</li>"
                for producto in resultado["productos"]
            )

            contenido = f"""
                <h2>¡Tu pedido ha sido calculado!</h2>

                <p>{html.escape(resultado["mensaje"])}</p>

                <h3>Detalle de tu pedido</h3>
                <ul>{lista_productos}</ul>

                <p><strong>Cantidad total:</strong>
                {resultado["unidades"]} unidades</p>

                <p><strong>Subtotal:</strong>
                {pesos(resultado["subtotal"])}</p>

                <p><strong>Descuento:</strong>
                {pesos(resultado["descuento"])}</p>

                <div class="total">
                    <span>Total estimado</span>
                    <strong>{pesos(resultado["total"])}</strong>
                </div>

                <a class="boton" href="/#calculadora">
                    Volver a la calculadora
                </a>
            """

        except ValueError as error:

            contenido = f"""
                <h2>No se pudo calcular el pedido</h2>
                <p class="error">{html.escape(str(error))}</p>
                <a class="boton" href="/#calculadora">
                    Volver e intentarlo
                </a>
            """

        self.enviar_pagina(contenido)

    def enviar_pagina(self, contenido):

        pagina = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resultado del pedido | Massiel Romo Essential Care</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f5f3ed;
            color: #333;
            padding: 30px 15px;
            margin: 0;
        }}

        .contenedor {{
            max-width: 650px;
            margin: 40px auto;
            padding: 30px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 18px rgba(0,0,0,0.08);
        }}

        h2 {{
            color: #596447;
        }}

        li {{
            margin: 10px 0;
        }}

        .total {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 15px;
            padding: 18px;
            margin: 20px 0;
            background: #eef0e8;
            border-radius: 10px;
            font-size: 18px;
        }}

        .total strong {{
            color: #596447;
            font-size: 22px;
        }}

        .error {{
            color: #a52b2b;
        }}

        .boton {{
            display: inline-block;
            margin-top: 15px;
            padding: 12px 20px;
            background: #596447;
            color: white;
            text-decoration: none;
            border-radius: 8px;
        }}
    </style>
</head>
<body>
    <main class="contenedor">
        {contenido}
    </main>
</body>
</html>"""

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )
        self.end_headers()
        self.wfile.write(pagina.encode("utf-8"))
from pathlib import Path

from flask import Flask, abort, render_template, request, send_from_directory


# Carpeta principal: allí están index.html, css e img.
CARPETA_PROYECTO = Path(__file__).resolve().parent.parent

app = Flask(
    __name__,
    template_folder=str(CARPETA_PROYECTO),
    static_folder=None,
)


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
    """Da formato de pesos colombianos."""
    return "$" + f"{valor:,.0f}".replace(",", ".")


def mostrar_pagina(
    seleccionados=None,
    cantidades=None,
    codigo="",
    resultado=None,
    mensaje="",
    tipo_mensaje="",
):
    """Muestra index.html con los datos de la calculadora."""
    return render_template(
        "index.html",
        catalogo=PRODUCTOS,
        pesos=pesos,
        seleccionados=seleccionados or [],
        cantidades=cantidades or {},
        codigo=codigo,
        resultado=resultado,
        mensaje=mensaje,
        tipo_mensaje=tipo_mensaje,
    )


@app.route("/", methods=["GET", "POST"])
def inicio():
    if request.method == "GET":
        return mostrar_pagina()

    # Corrección: procesa el botón Limpiar y devuelve el formulario vacío.
    if request.form.get("accion") == "limpiar":
        return mostrar_pagina()

    seleccionados = request.form.getlist("productos")
    codigo = request.form.get("codigo", "").strip().upper()

    cantidades = {
        id_producto: request.form.get(
            f"cantidad_{id_producto}", ""
        ).strip()
        for id_producto in PRODUCTOS
    }

    if not seleccionados:
        return mostrar_pagina(
            cantidades=cantidades,
            codigo=codigo,
            mensaje="Marca al menos un producto para calcular el pedido.",
            tipo_mensaje="mensaje-error",
        )

    subtotal = 0
    descuento = 0
    unidades = 0
    subtotal_productos_navidad = 0
    detalle_productos = []

    for id_producto in seleccionados:
        producto = PRODUCTOS.get(id_producto)

        if producto is None:
            return mostrar_pagina(
                seleccionados=seleccionados,
                cantidades=cantidades,
                codigo=codigo,
                mensaje="Hay un producto que no reconozco.",
                tipo_mensaje="mensaje-error",
            )

        try:
            cantidad = int(cantidades[id_producto])
        except (TypeError, ValueError):
            return mostrar_pagina(
                seleccionados=seleccionados,
                cantidades=cantidades,
                codigo=codigo,
                mensaje="Escribe una cantidad válida para cada producto marcado.",
                tipo_mensaje="mensaje-error",
            )

        if cantidad < 1:
            return mostrar_pagina(
                seleccionados=seleccionados,
                cantidades=cantidades,
                codigo=codigo,
                mensaje="La cantidad debe ser de al menos una unidad.",
                tipo_mensaje="mensaje-error",
            )

        subtotal_linea = producto["precio"] * cantidad
        subtotal += subtotal_linea
        unidades += cantidad
        detalle_productos.append(
            f"{cantidad} × {producto['nombre']}"
        )

        if producto["navidad"]:
            subtotal_productos_navidad += subtotal_linea

    if codigo == CODIGO_NAVIDAD:
        descuento = subtotal_productos_navidad * 10 // 100

        if descuento:
            mensaje = "Código NAVIDAD10 aplicado a los jabones participantes."
        else:
            mensaje = (
                "El pedido no incluye jabones participantes en la promoción."
            )
    elif codigo:
        mensaje = "El código no es válido; se calculó sin descuento."
    else:
        mensaje = "Pedido calculado."

    resultado = {
        "productos": "; ".join(detalle_productos),
        "unidades": unidades,
        "subtotal": pesos(subtotal),
        "descuento": pesos(descuento),
        "total": pesos(subtotal - descuento),
    }

    return mostrar_pagina(
        seleccionados=seleccionados,
        cantidades=cantidades,
        codigo=codigo,
        resultado=resultado,
        mensaje=mensaje,
        tipo_mensaje="mensaje-exito",
    )


@app.get("/<path:archivo>")
def servir_archivos(archivo):
    """Sirve el CSS, las imágenes, los videos y otros archivos del sitio."""
    ruta = CARPETA_PROYECTO / archivo

    if not ruta.is_file():
        abort(404)

    return send_from_directory(CARPETA_PROYECTO, archivo)


if __name__ == "__main__":
    app.run(debug=True)
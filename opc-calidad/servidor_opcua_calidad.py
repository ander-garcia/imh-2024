"""
Servidor OPC UA que simula una estación de control de calidad por visión.

Cada ciclo (por defecto 2 s) publica, dentro del objeto "ControlCalidad":
  - Imagen     (ByteString)  imagen PNG en binario de la pieza inspeccionada
  - Cota_mm    (Double)      cota medida (imaginaria), nominal 25.00 mm ± 0.10 mm
  - Resultado  (Int16)       1 = OK, 0 = NOT OK (fuera de tolerancia)
  - Contador   (UInt32)      número de pieza inspeccionada

Requisitos:  pip install asyncua pillow
Ejecución:   python servidor_opcua_calidad.py [--periodo 2] [--puerto 4840]
Endpoint:    opc.tcp://localhost:4840/calidad
"""
import argparse
import asyncio
import io
import random

from asyncua import Server, ua
from PIL import Image, ImageDraw, ImageFont

NOMINAL = 25.00      # mm
TOLERANCIA = 0.10    # mm  (±)
NS_URI = "http://ejemplo.upv/calidad"
ANCHO, ALTO = 320, 240


def generar_imagen(cota: float, ok: bool, n: int) -> bytes:
    """Dibuja una pieza simulada con su cota y devuelve el PNG en bytes."""
    img = Image.new("RGB", (ANCHO, ALTO), (28, 32, 40))
    d = ImageDraw.Draw(img)
    try:
        fuente = ImageFont.load_default(size=16)
    except TypeError:                       # Pillow antiguo
        fuente = ImageFont.load_default()

    # Pieza: rectángulo cuya anchura es proporcional a la cota medida
    px_por_mm = 7.0
    ancho_pieza = cota * px_por_mm
    cx, cy = ANCHO / 2, ALTO / 2 - 5
    x0, x1 = cx - ancho_pieza / 2, cx + ancho_pieza / 2
    color = (90, 160, 110) if ok else (200, 80, 70)
    d.rounded_rectangle([x0, cy - 45, x1, cy + 45], radius=8,
                        fill=(120, 130, 145), outline=color, width=3)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=(28, 32, 40))

    # Línea de cota
    y = cy + 62
    d.line([x0, y, x1, y], fill=(240, 240, 240), width=1)
    d.line([x0, y - 6, x0, y + 6], fill=(240, 240, 240), width=1)
    d.line([x1, y - 6, x1, y + 6], fill=(240, 240, 240), width=1)
    d.text((cx - 38, y + 8), f"{cota:.3f} mm", fill=(240, 240, 240), font=fuente)

    # Ruido de sensor para que las imágenes no sean idénticas
    for _ in range(300):
        d.point((random.randrange(ANCHO), random.randrange(ALTO)),
                fill=(random.randrange(60, 120),) * 3)

    d.text((8, 6), f"Pieza #{n}", fill=(200, 210, 225), font=fuente)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


async def main(periodo: float, puerto: int):
    server = Server()
    await server.init()
    server.set_endpoint(f"opc.tcp://0.0.0.0:{puerto}/calidad")
    server.set_server_name("Simulador control de calidad")
    idx = await server.register_namespace(NS_URI)      # normalmente ns=2

    obj = await server.nodes.objects.add_object(f"ns={idx};s=ControlCalidad", "ControlCalidad")
    v_imagen = await obj.add_variable(f"ns={idx};s=Imagen", "Imagen", b"", ua.VariantType.ByteString)
    v_cota = await obj.add_variable(f"ns={idx};s=Cota_mm", "Cota_mm", 0.0, ua.VariantType.Double)
    v_res = await obj.add_variable(f"ns={idx};s=Resultado", "Resultado", 0, ua.VariantType.Int16)
    v_cnt = await obj.add_variable(f"ns={idx};s=Contador", "Contador", 0, ua.VariantType.UInt32)

    print(f"Servidor en opc.tcp://localhost:{puerto}/calidad  (namespace índice {idx})")
    print("Nodos: ns=%d;s=Imagen | Cota_mm | Resultado | Contador   (Ctrl+C para parar)" % idx)

    n = 0
    async with server:
        while True:
            n += 1
            # ~80 % de piezas buenas: la cota se desvía de forma aleatoria
            sigma = 0.05 if random.random() < 0.8 else 0.18
            cota = round(random.gauss(NOMINAL, sigma), 3)
            ok = abs(cota - NOMINAL) <= TOLERANCIA
            png = generar_imagen(cota, ok, n)

            # La imagen se escribe la última: el cliente recibe primero los datos
            await v_cota.write_value(ua.Variant(cota, ua.VariantType.Double))
            await v_res.write_value(ua.Variant(1 if ok else 0, ua.VariantType.Int16))
            await v_cnt.write_value(ua.Variant(n, ua.VariantType.UInt32))
            await v_imagen.write_value(ua.Variant(png, ua.VariantType.ByteString))

            print(f"#{n:04d}  cota={cota:7.3f} mm  {'OK' if ok else 'NOT OK'}  ({len(png)} bytes)")
            await asyncio.sleep(periodo)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--periodo", type=float, default=2.0, help="segundos entre piezas")
    ap.add_argument("--puerto", type=int, default=4840)
    a = ap.parse_args()
    try:
        asyncio.run(main(a.periodo, a.puerto))
    except KeyboardInterrupt:
        pass

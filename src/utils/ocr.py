"""
VeloApp — Módulo OCR
Escaneo de facturas: online (ocr.space) + fallback manual offline
"""
import base64
import re
import urllib.request


# =========================================================
# VERIFICAR INTERNET
# =========================================================

def check_internet(timeout: int = 3) -> bool:
    """Verifica conexión rápida a 1.1.1.1."""
    try:
        urllib.request.urlopen("https://1.1.1.1", timeout=timeout)
        return True
    except Exception:
        return False


# =========================================================
# MEJORAR IMAGEN PARA OCR
# =========================================================

def enhance_image(image_path: str) -> str:
    """
    Preprocesa la imagen para mejorar la precisión del OCR.
    Convierte a escala de grises, aumenta contraste y nitidez.
    Retorna la ruta de la imagen procesada.
    """
    try:
        from PIL import Image, ImageFilter, ImageEnhance, ImageOps
        img = Image.open(image_path)

        # Corregir orientación EXIF (facturas tomadas con teléfono)
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        # Escala de grises
        img = img.convert("L")

        # Aumentar contraste
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.5)

        # Nitidez
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)

        # Filtro de nitidez adicional
        img = img.filter(ImageFilter.SHARPEN)

        # Guardar imagen mejorada
        enhanced_path = image_path + "_enh.jpg"
        img.save(enhanced_path, quality=95)
        return enhanced_path
    except Exception as e:
        print(f"[OCR] Error al mejorar imagen: {e}")
        return image_path


# =========================================================
# OCR ONLINE — ocr.space API
# =========================================================

def ocr_online(image_path: str, api_key: str = "helloworld") -> str | None:
    """
    Envía la imagen a ocr.space para reconocimiento de texto.
    api_key "helloworld" = demo gratuita (250 req/día).
    El usuario puede obtener su clave en: https://ocr.space/ocrapi/freekey
    """
    try:
        import requests

        with open(image_path, "rb") as f:
            img_bytes = f.read()

        b64 = base64.b64encode(img_bytes).decode("utf-8")
        ext = image_path.lower().split(".")[-1]
        mime = "image/jpeg" if ext in ("jpg", "jpeg", "enh") else "image/png"

        payload = {
            "base64Image": f"data:{mime};base64,{b64}",
            "language": "spa",
            "isOverlayRequired": "false",
            "detectOrientation": "true",
            "scale": "true",
            "isTable": "true",
            "OCREngine": "2",
        }

        response = requests.post(
            "https://api.ocr.space/parse/image",
            data=payload,
            headers={"apikey": api_key},
            timeout=20,
        )

        result = response.json()
        if result.get("IsErroredOnProcessing"):
            print(f"[OCR] Error API: {result.get('ErrorMessage')}")
            return None

        parsed = result.get("ParsedResults", [])
        if parsed:
            return parsed[0].get("ParsedText", "")
        return None

    except Exception as e:
        print(f"[OCR] Error online: {e}")
        return None


# =========================================================
# PARSEAR TEXTO → LISTA DE PRODUCTOS Y PRECIOS
# =========================================================

def parse_invoice_items(text: str) -> list[dict]:
    """
    Extrae pares (producto, precio) del texto de una factura.
    Maneja formatos venezolanos: $, Bs, 1.200,00, 1,200.00
    """
    if not text:
        return []

    items = []
    lines = text.strip().split("\n")

    # Palabras clave que NO son productos
    skip_keywords = [
        "factura", "receipt", "ticket", "total", "subtotal",
        "iva", "impuesto", "tax", "rif", "fecha", "date",
        "hora", "time", "caja", "cajero", "gracias", "cliente",
        "nit", "ci", "no.", "tel", "tlf", "dirección", "address",
        "cambio", "efectivo", "pago", "debit", "credito",
    ]

    # Patrón para detectar precios al final de la línea
    price_pattern = re.compile(
        r"[\$Bs\.]*\s*(\d{1,7}[.,]\d{2})\s*$|"   # Con decimales
        r"\$\s*(\d{1,7})\s*$|"                      # Solo $número
        r"(\d{1,7}[.,]\d{2})\s*[Bb][Ss]?\s*$",      # Número Bs
        re.IGNORECASE
    )

    for line in lines:
        line = line.strip()
        if len(line) < 4:
            continue

        # Omitir líneas de encabezado
        lower = line.lower()
        if any(kw in lower for kw in skip_keywords):
            continue

        match = price_pattern.search(line)
        if match:
            price_str = match.group(1) or match.group(2) or match.group(3) or ""
            product = line[:match.start()].strip()
            product = re.sub(r"\s{2,}", " ", product)   # espacios dobles
            product = product.strip(".:,-|")

            if product and len(product) > 2 and price_str:
                items.append({
                    "producto": product.title(),
                    "precio": price_str,
                })

    return items


# =========================================================
# FUNCIÓN PRINCIPAL DE ESCANEO
# =========================================================

def scan_invoice(image_path: str, api_key: str = "helloworld") -> dict:
    """
    Escanea una factura. Retorna:
      {
        "online": bool,
        "raw_text": str | None,
        "items": list[dict],
        "error": str | None
      }
    """
    result = {"online": False, "raw_text": None, "items": [], "error": None}

    # Mejorar imagen siempre (offline también)
    enhanced_path = enhance_image(image_path)

    if check_internet():
        result["online"] = True
        raw = ocr_online(enhanced_path, api_key)
        if raw:
            result["raw_text"] = raw
            result["items"] = parse_invoice_items(raw)
        else:
            result["error"] = (
                "No se pudo procesar la imagen en línea. "
                "Verifica tu conexión o inténtalo offline."
            )
    else:
        result["error"] = "Sin internet — modo manual activado."

    return result

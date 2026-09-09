import math
import json
import os
import time

import requests

import config

SEARCH_URL = f"{config.PLACES_API_BASE}/places:searchText"

LIMITE_RESULTADOS_BUSCA = 60


def _buscar_pagina(query, lat, lng, raio_m, page_token=None):
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": config.GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": "places.id,places.displayName,nextPageToken",
    }
    body = {
        "textQuery": query,
        "languageCode": "pt-BR",
        "regionCode": "BR",
        "locationBias": {"circle": {"center": {"latitude": lat, "longitude": lng}, "radius": raio_m}},
    }
    if page_token:
        body["pageToken"] = page_token
    resp = requests.post(SEARCH_URL, headers=headers, json=body, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _buscar_area(query, cidade_nome, categoria, lat, lng, raio_m, vistos):
    """Busca uma área (cidade inteira ou uma célula da grade), pagina, atualiza `vistos`.

    Retorna o total BRUTO de resultados (antes de deduplicar) -- é esse número que diz
    se a área bateu no teto da busca e precisa ser refinada, não o total de negócios
    novos (que pode ser menor por causa de sobreposição com outras áreas/categorias).
    """
    page_token = None
    paginas = 0
    total_bruto = 0
    while True:
        data = _buscar_pagina(query, lat, lng, raio_m, page_token)
        places = data.get("places", [])
        total_bruto += len(places)
        for place in places:
            place_id = place.get("id")
            if place_id and place_id not in vistos:
                vistos[place_id] = {
                    "nome_busca": place.get("displayName", {}).get("text", ""),
                    "cidade": cidade_nome,
                    "categoria": categoria,
                }
        page_token = data.get("nextPageToken")
        paginas += 1
        if not page_token or paginas >= 3:
            break
        time.sleep(2)  # nextPageToken leva um instante pra ficar válido

    return total_bruto


def _distancia_m(lat1, lng1, lat2, lng2):
    dlat_m = (lat2 - lat1) * 111320
    dlng_m = (lng2 - lng1) * 111320 * math.cos(math.radians((lat1 + lat2) / 2))
    return math.hypot(dlat_m, dlng_m)


def _gerar_grade(lat0, lng0, raio_total_m, raio_celula_m):
    """Centros de círculos menores cobrindo (com sobreposição) a área do círculo maior."""
    espacamento = raio_celula_m * 1.3
    passo_lat = espacamento / 111320
    passo_lng = espacamento / (111320 * math.cos(math.radians(lat0)))
    n = math.ceil(raio_total_m / espacamento)
    pontos = []
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            lat = lat0 + i * passo_lat
            lng = lng0 + j * passo_lng
            if _distancia_m(lat0, lng0, lat, lng) <= raio_total_m + raio_celula_m:
                pontos.append((lat, lng))
    return pontos


def buscar_categoria(cidade, categoria, vistos):
    query = f"{categoria} em {cidade['nome']}"
    total_bruto = _buscar_area(
        query, cidade["nome"], categoria, cidade["lat"], cidade["lng"], cidade["raio_m"], vistos
    )

    if total_bruto < LIMITE_RESULTADOS_BUSCA:
        return  # busca única já trouxe tudo, não precisa refinar

    raio_celula = config.RAIO_CELULA_GRADE_M
    pontos = _gerar_grade(cidade["lat"], cidade["lng"], cidade["raio_m"], raio_celula)
    print(
        f"    saturou ({total_bruto} resultados) -- refinando com {len(pontos)} "
        f"sub-áreas de {raio_celula / 1000:.0f}km"
    )
    for lat, lng in pontos:
        _buscar_area(query, cidade["nome"], categoria, lat, lng, raio_celula, vistos)


def descobrir():
    os.makedirs(config.DATA_DIR, exist_ok=True)
    vistos = {}
    if os.path.exists(config.PLACE_IDS_FILE):
        with open(config.PLACE_IDS_FILE, encoding="utf-8") as f:
            vistos = json.load(f)
        print(f"Retomando descoberta: {len(vistos)} negócios já salvos em {config.PLACE_IDS_FILE}")

    for cidade in config.CIDADES:
        for categoria in config.CATEGORIAS:
            antes = len(vistos)
            try:
                buscar_categoria(cidade, categoria, vistos)
            except requests.RequestException as exc:
                print(f"  {cidade['nome']} / {categoria}: ERRO ({exc}), pulando")
                continue
            print(f"  {cidade['nome']} / {categoria}: +{len(vistos) - antes} novos (total {len(vistos)})")
            if len(vistos) != antes:
                _salvar(vistos)

    _salvar(vistos)
    return vistos


def _salvar(vistos):
    with open(config.PLACE_IDS_FILE, "w", encoding="utf-8") as f:
        json.dump(vistos, f, ensure_ascii=False, indent=2)

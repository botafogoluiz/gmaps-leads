import json
import os
import time

import requests

import config

DETAILS_FIELD_MASK = "displayName,websiteUri"


def _carregar_cache():
    if os.path.exists(config.DETAILS_CACHE_FILE):
        with open(config.DETAILS_CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _salvar_cache(cache):
    with open(config.DETAILS_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def _buscar_detalhes(place_id):
    url = f"{config.PLACES_API_BASE}/places/{place_id}"
    headers = {
        "X-Goog-Api-Key": config.GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": DETAILS_FIELD_MASK,
    }
    for tentativa in range(5):
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 429:
            espera = 2**tentativa
            print(f"    Limite de taxa (429), esperando {espera}s...")
            time.sleep(espera)
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError(f"Falhou após várias tentativas para {place_id}")


def buscar_todos(place_ids, limite=None):
    """Busca detalhes de todos os place_ids que ainda não estão no cache (retomável)."""
    cache = _carregar_cache()
    pendentes = [pid for pid in place_ids if pid not in cache]
    if limite is not None:
        pendentes = pendentes[:limite]

    print(f"{len(cache)} já em cache, {len(pendentes)} pendentes.")
    for i, place_id in enumerate(pendentes, 1):
        try:
            dados = _buscar_detalhes(place_id)
        except (requests.RequestException, RuntimeError) as exc:
            print(f"  [{i}/{len(pendentes)}] ERRO em {place_id}: {exc}")
            continue
        cache[place_id] = dados
        _salvar_cache(cache)  # salva a cada item -- uma queda no meio não perde nem repaga nada
        nome = dados.get("displayName", {}).get("text", place_id)
        print(f"  [{i}/{len(pendentes)}] {nome}")

    return cache

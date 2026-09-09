import csv
import json
import os

import config


def _classificar_site(site):
    """Muito negócio pequeno usa o link do Instagram/Facebook como "site" no Google
    Meu Negócio -- diferencia isso de um site próprio de verdade."""
    if not site:
        return ""
    site_lower = site.lower()
    if "instagram.com" in site_lower:
        return "Instagram"
    if "facebook.com" in site_lower:
        return "Facebook"
    return "Site próprio"


def _carregar_instagram_encontrado():
    if os.path.exists(config.INSTAGRAM_CACHE_FILE):
        with open(config.INSTAGRAM_CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def exportar():
    with open(config.DETAILS_CACHE_FILE, encoding="utf-8") as f:
        cache = json.load(f)
    instagram_encontrado = _carregar_instagram_encontrado()

    with open(config.OUTPUT_CSV_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Nome", "Site", "Tipo de Site", "Instagram", "Duvidoso", "Oportunidade"])
        for place_id, dados in cache.items():
            nome = dados.get("displayName", {}).get("text", "")
            site = dados.get("websiteUri", "")
            tipo_site = _classificar_site(site)

            achado = instagram_encontrado.get(place_id, {})
            duvidoso = achado.get("duvidoso", "")
            if tipo_site == "Instagram":
                instagram = site
            else:
                # só usa o Instagram achado na busca web se a confirmação de cidade bateu
                instagram = achado.get("instagram", "") if duvidoso == "Não" else ""

            tem_presenca = bool(tipo_site) or bool(instagram)
            oportunidade = "Já está nas redes" if tem_presenca else "Não está nas redes"

            writer.writerow([nome, site, tipo_site, instagram, duvidoso, oportunidade])

    print(f"CSV salvo em {config.OUTPUT_CSV_FILE} ({len(cache)} negócios).")


if __name__ == "__main__":
    exportar()

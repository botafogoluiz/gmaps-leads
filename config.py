import os

# Vazio (em vez de exigir a env var) porque scripts que não chamam a Places API --
# como a busca de Instagram via web, que só usa WebSearch -- também importam este
# módulo (pra reaproveitar DATA_DIR etc.) e não devem quebrar por falta dessa chave.
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")

# Cota mensal gratuita por SKU informada pelo usuário (conferida na página de preços do
# Google). A Fase 2 usa o SKU "Place Details Pro" (displayName + websiteUri) -- só paga
# a partir da chamada 5001 nesse SKU, no mesmo mês, somando com qualquer outro uso desse
# mesmo SKU que já tenha existido no projeto.
CHAMADAS_GRATIS_MENSAIS_POR_SKU = 5000

# Custo estimado (USD) de UMA chamada de Place Details ACIMA da cota gratuita, com os
# campos usados aqui (displayName, websiteUri, nível "Pro" da API). Confira o valor
# atual em https://mapsplatform.google.com/pricing/. Fica em 0 de propósito até ser
# preenchido: o script nunca assume um preço por conta própria -- só importa se o total
# de negócios ultrapassar a cota gratuita acima.
CUSTO_POR_DETALHE_USD = 0.0

# Quando uma busca única bate no teto prático da API (~60 resultados), a área é refeita
# como uma grade de círculos deste raio, cobrindo a mesma região com sobreposição --
# célula menor = cobertura mais fina, porém mais chamadas de busca. Só entra em ação nas
# categorias que de fato saturam, não em todas.
RAIO_CELULA_GRADE_M = 4000

CIDADES = [
    {"nome": "São Pedro da Aldeia, RJ", "lat": -22.8367, "lng": -42.1028, "raio_m": 15000},
    {"nome": "Araruama, RJ", "lat": -22.8725, "lng": -42.3444, "raio_m": 15000},
]

CATEGORIAS = [
    "restaurante",
    "lanchonete",
    "salão de beleza",
    "barbearia",
    "academia",
    "clínica médica",
    "consultório odontológico",
    "pet shop",
    "loja de roupas",
    "supermercado",
    "mercearia",
    "imobiliária",
    "oficina mecânica",
    "loja de autopeças",
    "farmácia",
    "hotel",
    "pousada",
    "escritório de advocacia",
    "escritório de contabilidade",
    "loja de material de construção",
    "padaria",
    "pizzaria",
]

PLACES_API_BASE = "https://places.googleapis.com/v1"

DATA_DIR = os.environ.get("DATA_DIR", "data")
PLACE_IDS_FILE = os.path.join(DATA_DIR, "place_ids.json")
DETAILS_CACHE_FILE = os.path.join(DATA_DIR, "details_cache.json")
INSTAGRAM_CACHE_FILE = os.path.join(DATA_DIR, "instagram_cache.json")
OUTPUT_CSV_FILE = os.path.join(DATA_DIR, "negocios.csv")

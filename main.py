import sys

import config
import details
import discover
import export


def main():
    print("=== Fase 1: descoberta de negócios ===")
    vistos = discover.descobrir()
    total = len(vistos)
    print(f"\n{total} negócios únicos encontrados.")

    cota = config.CHAMADAS_GRATIS_MENSAIS_POR_SKU
    excedente = max(0, total - cota)

    if excedente == 0:
        print(
            f"A Fase 2 faz {total} chamadas no SKU 'Place Details Pro', dentro da cota "
            f"gratuita de {cota}/mês -- custo estimado: US$ 0,00 (supondo que essa cota "
            f"não tenha sido usada por mais nada neste projeto/mês)."
        )
    elif config.CUSTO_POR_DETALHE_USD > 0:
        estimativa = excedente * config.CUSTO_POR_DETALHE_USD
        print(
            f"A Fase 2 faz {total} chamadas no SKU 'Place Details Pro'. As primeiras "
            f"{cota} entram na cota gratuita mensal; as {excedente} restantes são "
            f"cobradas. Estimativa aproximada: US$ {estimativa:.2f} "
            f"(baseado em config.CUSTO_POR_DETALHE_USD -- confira o valor real em "
            f"Faturamento > Relatórios no Cloud Console)."
        )
    else:
        print(
            f"A Fase 2 faz {total} chamadas no SKU 'Place Details Pro' -- {excedente} "
            f"delas ultrapassam a cota gratuita de {cota}/mês e serão cobradas, mas "
            f"config.CUSTO_POR_DETALHE_USD está em 0, então não dá pra estimar o valor "
            f"ainda. Veja o preço atual em https://mapsplatform.google.com/pricing/ "
            f"(nível Pro da Place Details) e preencha essa constante se quiser a "
            f"estimativa antes de continuar."
        )

    resposta = input("\nContinuar para a Fase 2 (Place Details)? [s/N] ").strip().lower()
    if resposta != "s":
        print("Parando por aqui. Nada foi gasto na Fase 2.")
        sys.exit(0)

    print("\n=== Fase 2: detalhes de cada negócio ===")
    details.buscar_todos(list(vistos.keys()))

    print("\n=== Exportando CSV ===")
    export.exportar()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Junta todas as fontes em um banco único: questoes/banco.json e questoes/banco.csv.

Fontes:
  dados/*.json            provas oficiais já importadas (importar_medbench.py, importar_prova_pdf.py)
  questoes/questoes.json  questões de páginas salvas (extrair_questoes.py)
  questoes/resolucoes.json links de correções gratuitas por prova

Uma questão salva que também está numa prova oficial não é duplicada: fica a versão
oficial (com o gabarito oficial), completada com subárea e tópico da página salva.

Uso:
    python3 scripts/montar_banco.py
"""
import csv
import glob
import json
import re
import unicodedata

AREAS_SITE = {
    "CLÍNICA MÉDICA": "Clínica Médica",
    "CIRURGIA": "Cirurgia",
    "GINECOLOGIA E OBSTETRÍCIA": "Ginecologia e Obstetrícia",
    "PEDIATRIA": "Pediatria",
    "MEDICINA PREVENTIVA / SAÚDE COLETIVA": "Medicina Preventiva e Social",
    "OUTROS": "Outros",
}


def chave(enunciado):
    texto = unicodedata.normalize("NFKD", enunciado.lower())
    return re.sub(r"\W+", "", texto)[:150]


def da_pagina_salva(q):
    return {
        "id": f"pagina-salva-{q['id']}",
        "instituicao": q["instituicao"],
        "ano": q["ano"],
        "numero": None,
        "area": AREAS_SITE.get(q["area"], q["area"].title()),
        "subarea": q["subarea"],
        "topico": q["topico"],
        "enunciado": q["enunciado"],
        "alternativas": q["alternativas"],
        "gabarito": q["gabarito"],
        "anulada": False,
        "situacao_gabarito": "informado pelo site" if q["gabarito"] else "sem gabarito",
        "tem_imagem": bool(q.get("imagens")),
        "tem_tabela": False,
        "observacao": "",
        "fonte": q["fonte"],
        "origem": "página salva pelo usuário",
    }


def main():
    banco, por_chave = [], {}
    for caminho in sorted(glob.glob("dados/*.json")):
        with open(caminho, encoding="utf-8") as f:
            for q in json.load(f):
                banco.append(q)
                por_chave[chave(q["enunciado"])] = q

    with open("questoes/questoes.json", encoding="utf-8") as f:
        salvas = json.load(f)
    unidas = 0
    for s in map(da_pagina_salva, salvas):
        oficial = por_chave.get(chave(s["enunciado"]))
        if oficial is None:
            banco.append(s)
            continue
        unidas += 1
        for campo in ("subarea", "topico"):
            if not oficial[campo] and s[campo]:
                oficial[campo] = s[campo]

    with open("questoes/resolucoes.json", encoding="utf-8") as f:
        resolucoes = json.load(f)
    for q in banco:
        q["resolucoes"] = resolucoes.get(f"{q['instituicao']} {q['ano']}", [])

    with open("questoes/banco.json", "w", encoding="utf-8") as f:
        json.dump(banco, f, ensure_ascii=False, indent=1)

    with open("questoes/banco.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "instituicao", "ano", "numero", "area", "subarea", "topico", "enunciado",
                    "alternativa_A", "alternativa_B", "alternativa_C", "alternativa_D", "alternativa_E",
                    "gabarito", "anulada", "situacao_gabarito", "tem_imagem", "tem_tabela",
                    "observacao", "fonte", "resolucoes"])
        for q in banco:
            a = q["alternativas"]
            w.writerow([q["id"], q["instituicao"], q["ano"], q["numero"] or "", q["area"], q["subarea"],
                        q["topico"], q["enunciado"], *[a.get(l, "") for l in "ABCDE"],
                        q["gabarito"] or "", "sim" if q["anulada"] else "", q["situacao_gabarito"],
                        "sim" if q["tem_imagem"] else "", "sim" if q["tem_tabela"] else "",
                        q["observacao"], q["fonte"], " | ".join(r["url"] for r in q["resolucoes"])])

    provas = {}
    for q in banco:
        provas.setdefault(f"{q['instituicao']} {q['ano']}", []).append(q)
    print(f"{len(banco)} questões ({unidas} página(s) salva(s) unida(s) à prova oficial)")
    for nome, qs in sorted(provas.items()):
        print(f"  {nome:16} {len(qs):4} questões, {sum(q['anulada'] for q in qs)} anuladas, "
              f"gabarito {qs[0]['situacao_gabarito']}, {len(qs[0]['resolucoes'])} link(s) de resolução")


if __name__ == "__main__":
    main()

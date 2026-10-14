#!/usr/bin/env python3
"""Converte as edições do dataset medbench-brasil (Revalida e ENAMED, INEP) para dados/.

O medbench-brasil (https://github.com/Precisa-Saude/medbench-brasil, Apache-2.0)
traz as questões extraídas dos cadernos oficiais do INEP com o gabarito oficial.

Uso:
    git clone --depth 1 https://github.com/Precisa-Saude/medbench-brasil
    python3 scripts/importar_medbench.py medbench-brasil/packages/dataset/data
"""
import glob
import json
import os
import sys

AREAS = {
    "cirurgia": ("Cirurgia", ""),
    "clinica-medica": ("Clínica Médica", ""),
    "ginecologia-obstetricia": ("Ginecologia e Obstetrícia", ""),
    "pediatria": ("Pediatria", ""),
    "medicina-familia-comunidade": ("Medicina Preventiva e Social", "Medicina de Família e Comunidade"),
    "saude-publica": ("Medicina Preventiva e Social", "Saúde Pública"),
}


def converter(edicao):
    familia, _, resto = edicao["id"].partition("-")
    ano = resto.replace("-", ".")  # revalida-2024-1 -> 2024.1
    situacao = edicao.get("answerKeyStatus", "definitivo")
    saida = []
    for q in edicao["questions"]:
        area, subarea = AREAS[q["specialty"][0]] if q["specialty"] else ("", "")
        saida.append({
            "id": q["id"],
            "instituicao": familia.upper(),
            "ano": ano,
            "numero": q["number"],
            "area": area,
            "subarea": subarea,
            "topico": "",
            "enunciado": q["stem"],
            "alternativas": q["options"],
            "gabarito": None if q["annulled"] else q["correct"],
            "anulada": q["annulled"],
            "situacao_gabarito": situacao,
            "tem_imagem": q["hasImage"],
            "tem_tabela": q["hasTable"],
            "observacao": q.get("notes", ""),
            "fonte": edicao["source"],
            "origem": "medbench-brasil (Apache-2.0), cadernos oficiais do INEP",
        })
    return saida


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    os.makedirs("dados", exist_ok=True)
    for caminho in sorted(glob.glob(os.path.join(sys.argv[1], "*", "*.json"))):
        with open(caminho, encoding="utf-8") as f:
            edicao = json.load(f)
        questoes = converter(edicao)
        if not questoes:
            continue
        destino = os.path.join("dados", edicao["id"] + ".json")
        with open(destino, "w", encoding="utf-8") as f:
            json.dump(questoes, f, ensure_ascii=False, indent=2)
        print(f"{len(questoes)} questões -> {destino}")


if __name__ == "__main__":
    main()

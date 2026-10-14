#!/usr/bin/env python3
"""Importa uma prova oficial em PDF de duas colunas (modelo ENARE / Instituto AOCP).

Lê o caderno de questões coluna por coluna, separa enunciado e alternativas,
cruza com o gabarito oficial em PDF e grava um JSON por edição em dados/.

Exemplo (ENARE 2023/2024, caderno Tipo 01 = "PROVA 1" do gabarito):
    python3 scripts/importar_prova_pdf.py \
        --prova enare_2023_prova.pdf --paginas 2-27 \
        --gabarito enare_2023_gabarito.pdf \
        --secao "ACESSO DIRETO - TODOS OS PROGRAMAS - PROVA 1" \
        --instituicao ENARE --ano 2023 --situacao preliminar \
        --fonte https://enare.ebserh.gov.br --saida dados/enare-2023.json

Requer: pip install pdfplumber
"""
import argparse
import json
import re
import sys

import pdfplumber

# Cabeçalhos e rodapés que se repetem em todas as páginas.
RUIDO = re.compile(
    r"^(EXAME NACIONAL DE RESID[ÊE]NCIA.*|Exame Nacional de Resid[êe]ncia.*|INSTITUTO AOCP|"
    r"Instituto AOCP|PRM - .*|PROGRAMA DE RESID[ÊE]NCIA.*|PROGRAMAS.*|Tipo \d+.*|.*P[áa]gina \d+)$"
)

AREAS = {
    "clínica médica": "Clínica Médica",
    "cirurgia": "Cirurgia",
    "cirurgia geral": "Cirurgia",
    "pediatria": "Pediatria",
    "ginecologia e obstetrícia": "Ginecologia e Obstetrícia",
    "obstetrícia e ginecologia": "Ginecologia e Obstetrícia",
    "ginecologia": "Ginecologia e Obstetrícia",
    "obstetrícia": "Ginecologia e Obstetrícia",
    "medicina preventiva e social": "Medicina Preventiva e Social",
    "medicina preventiva": "Medicina Preventiva e Social",
    "medicina de família e comunidade": "Medicina Preventiva e Social",
    "medicina de família e comunidade - saúde coletiva": "Medicina Preventiva e Social",
    "saúde coletiva": "Medicina Preventiva e Social",
    "medicina social e preventiva": "Medicina Preventiva e Social",
}

IMAGEM = re.compile(
    r"\b(imagem|imagens|figura|fotografia|foto)\b|"
    r"(eletrocardiograma|radiografia|tomografia|ultrassonografia|gráfico)\s+(a seguir|abaixo)",
    re.IGNORECASE,
)


def intervalo(texto):
    ini, _, fim = texto.partition("-")
    return range(int(ini), int(fim or ini) + 1)


def linhas_da_prova(caminho, paginas):
    """Texto do caderno em ordem de leitura: coluna esquerda, depois direita, página a página."""
    linhas = []
    with pdfplumber.open(caminho) as pdf:
        for n in paginas:
            p = pdf.pages[n - 1]
            meio = p.width / 2
            for caixa in ((0, 0, meio, p.height), (meio, 0, p.width, p.height)):
                texto = p.crop(caixa).extract_text() or ""
                linhas += [l.strip() for l in texto.splitlines() if l.strip()]
    return [l for l in linhas if not RUIDO.match(l)]


def juntar(linhas):
    texto = ""
    for l in linhas:
        if not texto:
            texto = l
        elif texto.endswith("-"):
            texto += l
        else:
            texto += " " + l
    return re.sub(r"\s+", " ", texto).strip()


def separar_questoes(linhas, total):
    questoes, atual, area, esperado = [], None, "", 1
    pular = False
    for i, l in enumerate(linhas):
        if pular:
            pular = False
            continue
        chave = l.lower().rstrip(" -")
        if chave in AREAS:
            area = AREAS[chave]
            continue
        # Título de seção quebrado em duas linhas, ex.: "Medicina de Família e" / "Comunidade - ..."
        duas = f"{chave} {linhas[i + 1].lower()}" if i + 1 < len(linhas) else ""
        if duas in AREAS:
            area, pular = AREAS[duas], True
            continue
        if l == str(esperado) and esperado <= total:
            atual = {"numero": esperado, "area": area, "linhas": []}
            questoes.append(atual)
            esperado += 1
            continue
        if atual is not None:
            atual["linhas"].append(l)

    resultado = []
    for q in questoes:
        enunciado, alternativas, letra = [], {}, None
        for l in q["linhas"]:
            m = re.match(r"^\(([A-E])\)\s*(.*)$", l)
            if m:
                letra = m.group(1)
                alternativas[letra] = [m.group(2)]
            elif letra:
                alternativas[letra].append(l)
            else:
                enunciado.append(l)
        resultado.append({
            "numero": q["numero"],
            "area": q["area"],
            "enunciado": juntar(enunciado),
            "alternativas": {k: juntar(v) for k, v in alternativas.items()},
        })
    return resultado


def ler_gabarito(caminho, secao, total):
    """Lê a tabela 'números / letras' logo abaixo do título da seção pedida."""
    with pdfplumber.open(caminho) as pdf:
        texto = "\n".join(p.extract_text() or "" for p in pdf.pages)
    linhas = texto.splitlines()
    inicio = next((i for i, l in enumerate(linhas) if secao.lower() in l.lower()), None)
    if inicio is None:
        sys.exit(f"seção '{secao}' não encontrada no gabarito")
    gabarito, numeros = {}, None
    for l in linhas[inicio + 1:]:
        partes = l.split()
        if partes and all(p.isdigit() for p in partes):
            numeros = [int(p) for p in partes]
        elif numeros and partes and all(re.fullmatch(r"[A-EX*]", p) for p in partes):
            gabarito.update(zip(numeros, partes))
            numeros = None
            if len(gabarito) >= total:
                break
    return gabarito


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prova", required=True)
    ap.add_argument("--paginas", required=True, help="páginas do caderno, ex.: 2-27")
    ap.add_argument("--gabarito", required=True)
    ap.add_argument("--secao", required=True, help="trecho do título da tabela certa no gabarito")
    ap.add_argument("--instituicao", required=True)
    ap.add_argument("--ano", required=True)
    ap.add_argument("--situacao", choices=["definitivo", "preliminar"], required=True)
    ap.add_argument("--fonte", required=True, help="URL oficial onde a prova é publicada")
    ap.add_argument("--total", type=int, default=100)
    ap.add_argument("--saida", required=True)
    args = ap.parse_args()

    questoes = separar_questoes(linhas_da_prova(args.prova, intervalo(args.paginas)), args.total)
    gabarito = ler_gabarito(args.gabarito, args.secao, args.total)

    problemas = []
    if len(questoes) != args.total:
        problemas.append(f"{len(questoes)} questões encontradas, esperado {args.total}")
    if len(gabarito) != args.total:
        problemas.append(f"{len(gabarito)} respostas no gabarito, esperado {args.total}")

    prefixo = f"{args.instituicao.lower()}-{args.ano}".replace(".", "-")
    saida = []
    for q in questoes:
        letras = sorted(q["alternativas"])
        if letras != list("ABCDE")[:len(letras)] or len(letras) < 4:
            problemas.append(f"questão {q['numero']}: alternativas {letras}")
        resposta = gabarito.get(q["numero"])
        anulada = resposta in ("X", "*")
        texto = q["enunciado"] + " " + " ".join(q["alternativas"].values())
        saida.append({
            "id": f"{prefixo}-q{q['numero']:03d}",
            "instituicao": args.instituicao,
            "ano": args.ano,
            "numero": q["numero"],
            "area": q["area"],
            "subarea": "",
            "topico": "",
            "enunciado": q["enunciado"],
            "alternativas": q["alternativas"],
            "gabarito": None if anulada else resposta,
            "anulada": anulada,
            "situacao_gabarito": args.situacao,
            "tem_imagem": bool(IMAGEM.search(texto)),
            "tem_tabela": False,
            "observacao": "Questão anulada no gabarito oficial." if anulada else "",
            "fonte": args.fonte,
            "origem": "PDF oficial da prova e do gabarito",
        })

    with open(args.saida, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)
    for p in problemas:
        print(f"aviso: {p}", file=sys.stderr)
    print(f"{len(saida)} questões, {sum(q['anulada'] for q in saida)} anuladas -> {args.saida}")


if __name__ == "__main__":
    main()

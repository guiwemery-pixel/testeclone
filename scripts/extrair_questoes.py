#!/usr/bin/env python3
"""Extrai questões de páginas do QBank do El Doctor Gabo salvas pelo navegador.

Aceita arquivos .mhtml (Chrome/Android: "Download" da página) ou .html.
Cada página salva traz apenas a questão que estava na tela.

Uso:
    python3 scripts/extrair_questoes.py pagina1.mhtml pagina2.mhtml ... \
        --saida questoes/questoes

Gera <saida>.json e <saida>.csv. Os comentários do site (justificativa de cada
alternativa e "Raciocínio da questão") são conteúdo autoral do El Doctor Gabo e
só são incluídos com --com-comentarios, para uso pessoal.
"""
import argparse
import csv
import email
import json
import re
import sys
from email import policy
from html.parser import HTMLParser


def ler_html(caminho):
    with open(caminho, "rb") as f:
        bruto = f.read()
    if b"multipart/related" in bruto[:4000]:
        msg = email.message_from_bytes(bruto, policy=policy.default)
        for parte in msg.walk():
            if parte.get_content_type() == "text/html":
                return parte.get_payload(decode=True).decode("utf-8", "replace")
        raise ValueError(f"{caminho}: nenhuma parte HTML no MHTML")
    return bruto.decode("utf-8", "replace")


class ParserQuestao(HTMLParser):
    """Percorre o card da questão guardando texto por região (enunciado, alternativas...)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pilha = []  # (tag, regiao) de cada elemento aberto
        self.prova = ""
        self.taxonomia = ""
        self.enunciado = []
        self.imagens = []
        self.alternativas = []  # dicts: letra, texto, correta, justificativa
        self.raciocinio = []
        self._buf = None

    VAZIAS = {"br", "img", "hr", "input", "meta", "link", "source", "wbr"}

    def _regiao(self):
        return self.pilha[-1][1] if self.pilha else None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        ident = a.get("id")
        regiao = self._regiao()

        nova = regiao
        if ident == "prova-badge":
            nova = "prova"
        elif ident == "tax-badge":
            nova = "taxonomia"
        elif ident == "enunciado-text":
            nova = "enunciado"
        elif tag == "button" and "alt" in classes and a.get("data-letra"):
            self.alternativas.append({
                "letra": a["data-letra"],
                "texto": "",
                "correta": True if "correct" in classes else (False if "wrong" in classes else None),
                "justificativa": "",
            })
            nova = "alt"
        elif regiao == "alt" and "alt-txt" in classes:
            nova = "alt-txt"
        elif "alt-just" in classes:
            nova = "alt-just"
        elif regiao == "alt-just" and "just-label" in classes:
            nova = "ignorar"
        elif "feedback" in classes:
            nova = "raciocinio"
        elif "chosen-inline" in classes or "letra" in classes:
            nova = "ignorar"

        if tag == "img" and regiao == "enunciado" and a.get("src"):
            self.imagens.append(a["src"])
        if tag in ("p", "li", "h4", "div", "br") and nova in ("enunciado", "raciocinio", "alt-just"):
            self._quebra(nova)
        if tag not in self.VAZIAS:
            self.pilha.append((tag, nova))

    def handle_endtag(self, tag):
        for i in range(len(self.pilha) - 1, -1, -1):
            if self.pilha[i][0] == tag:
                del self.pilha[i:]
                break

    def _quebra(self, regiao):
        alvo = self._alvo(regiao)
        if alvo is not None and alvo and alvo[-1] != "\n":
            alvo.append("\n")

    def _alvo(self, regiao):
        if regiao == "enunciado":
            return self.enunciado
        if regiao == "raciocinio":
            return self.raciocinio
        return None

    def handle_data(self, data):
        regiao = self._regiao()
        if regiao == "prova":
            self.prova += data
        elif regiao == "taxonomia":
            self.taxonomia += data
        elif regiao in ("enunciado", "raciocinio"):
            self._alvo(regiao).append(data)
        elif regiao == "alt-txt" and self.alternativas:
            self.alternativas[-1]["texto"] += data
        elif regiao == "alt-just" and self.alternativas:
            self.alternativas[-1]["justificativa"] += data


def limpar(texto):
    linhas = [re.sub(r"[ \t ]+", " ", l).strip() for l in texto.split("\n")]
    return "\n".join(l for l in linhas if l)


def extrair(caminho, com_comentarios):
    html = ler_html(caminho)
    p = ParserQuestao()
    p.feed(html)
    enunciado = limpar("".join(p.enunciado))
    if not enunciado or not p.alternativas:
        raise ValueError(f"{caminho}: questão não encontrada (a página foi salva com a questão aberta?)")

    prova = limpar(p.prova)
    m = re.match(r"(.*?)\s+(\d{4}\S*)$", prova)
    instituicao, ano = (m.group(1), m.group(2)) if m else (prova, "")
    tax = [t.strip() for t in limpar(p.taxonomia).split(" / ")] + ["", "", ""]

    gabarito = next((a["letra"] for a in p.alternativas if a["correta"]), None)
    if gabarito is None:
        m = re.search(r"Gabarito:\s*([A-E])", html)
        gabarito = m.group(1) if m else None

    questao = {
        "instituicao": instituicao,
        "ano": ano,
        "area": tax[0],
        "subarea": tax[1],
        "topico": " / ".join(t for t in tax[2:] if t),
        "enunciado": enunciado,
        "alternativas": {a["letra"]: limpar(a["texto"]) for a in p.alternativas},
        "gabarito": gabarito,
        "imagens": p.imagens,
        "fonte": f"{prova} (via El Doctor Gabo QBank)",
    }
    if com_comentarios:
        questao["comentarios_alternativas"] = {
            a["letra"]: limpar(a["justificativa"]) for a in p.alternativas
        }
        questao["raciocinio"] = limpar("".join(p.raciocinio))
    return questao


def chave(q):
    return (q["instituicao"], q["ano"], q["enunciado"][:200])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("arquivos", nargs="+")
    ap.add_argument("--saida", default="questoes/questoes", help="prefixo dos arquivos de saída")
    ap.add_argument("--com-comentarios", action="store_true",
                    help="inclui os comentários autorais do site (uso pessoal)")
    args = ap.parse_args()

    # Acrescenta ao JSON existente, sem duplicar questões já extraídas.
    try:
        with open(args.saida + ".json", encoding="utf-8") as f:
            questoes = json.load(f)
    except FileNotFoundError:
        questoes = []
    vistas = {chave(q): q for q in questoes}

    novas = completadas = 0
    for caminho in args.arquivos:
        try:
            q = extrair(caminho, args.com_comentarios)
        except ValueError as e:
            print(f"aviso: {e}", file=sys.stderr)
            continue
        existente = vistas.get(chave(q))
        if existente is not None:
            # A mesma questão salva de novo depois de respondida completa o que faltava.
            if not existente.get("gabarito") and q["gabarito"]:
                for campo in ("gabarito", "comentarios_alternativas", "raciocinio"):
                    if campo in q:
                        existente[campo] = q[campo]
                completadas += 1
            continue
        if not q["gabarito"]:
            print(f"aviso: {caminho}: sem gabarito (salve a página depois de responder)", file=sys.stderr)
        vistas[chave(q)] = q
        questoes.append(q)
        novas += 1

    for i, q in enumerate(questoes, 1):
        q["id"] = i
    with open(args.saida + ".json", "w", encoding="utf-8") as f:
        json.dump(questoes, f, ensure_ascii=False, indent=2)

    letras = sorted({l for q in questoes for l in q["alternativas"]})
    with open(args.saida + ".csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "instituicao", "ano", "area", "subarea", "topico", "enunciado",
                    *[f"alternativa_{l}" for l in letras], "gabarito", "fonte"])
        for q in questoes:
            w.writerow([q["id"], q["instituicao"], q["ano"], q["area"], q["subarea"], q["topico"],
                        q["enunciado"], *[q["alternativas"].get(l, "") for l in letras],
                        q["gabarito"] or "", q["fonte"]])

    sem_gabarito = sum(1 for q in questoes if not q.get("gabarito"))
    print(f"{novas} questão(ões) nova(s), {completadas} completada(s); total {len(questoes)} "
          f"({sem_gabarito} sem gabarito) em {args.saida}.json/.csv")


if __name__ == "__main__":
    main()

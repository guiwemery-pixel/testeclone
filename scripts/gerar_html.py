#!/usr/bin/env python3
"""Gera questoes/banco.html: o banco inteiro numa página única, que funciona offline.

Uso:
    python3 scripts/gerar_html.py
"""
import json

CAMPOS = ["id", "instituicao", "ano", "numero", "area", "subarea", "topico", "enunciado",
          "alternativas", "gabarito", "anulada", "situacao_gabarito", "tem_imagem",
          "tem_tabela", "observacao", "explicacao"]

MODELO = r"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Banco de Questões</title>
<style>
:root {
  --bg: #f5f6f8; --surface: #ffffff; --surface-2: #eef1f5; --text: #1b2027; --muted: #5a6472;
  --border: #d8dde4; --accent: #2353c9; --accent-soft: #e7edfb;
  --ok: #1a7343; --ok-soft: #e2f3e9; --bad: #b3261e; --bad-soft: #fce8e6;
  --warn: #7a5200; --warn-soft: #fbf1d9; --shadow: 0 1px 2px rgba(16,24,40,.06), 0 1px 3px rgba(16,24,40,.08);
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #12151a; --surface: #1b1f26; --surface-2: #232933; --text: #e6e9ee; --muted: #9aa4b2;
    --border: #2f3640; --accent: #7ea2ff; --accent-soft: #1f2a44;
    --ok: #5cc98b; --ok-soft: #173326; --bad: #ff8a80; --bad-soft: #3a1d1b;
    --warn: #f1c26b; --warn-soft: #362a12; --shadow: none;
  }
}
:root[data-theme="dark"] {
  --bg: #12151a; --surface: #1b1f26; --surface-2: #232933; --text: #e6e9ee; --muted: #9aa4b2;
  --border: #2f3640; --accent: #7ea2ff; --accent-soft: #1f2a44;
  --ok: #5cc98b; --ok-soft: #173326; --bad: #ff8a80; --bad-soft: #3a1d1b;
  --warn: #f1c26b; --warn-soft: #362a12; --shadow: none;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0; background: var(--bg); color: var(--text);
  font: 16px/1.55 system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
.wrap { max-width: 780px; margin: 0 auto; padding: 16px 16px 48px; }
header h1 { font-size: 1.35rem; margin: 4px 0 2px; letter-spacing: -.01em; }
header p { margin: 0; color: var(--muted); font-size: .92rem; }
.panel {
  background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
  box-shadow: var(--shadow); margin-top: 14px;
}
details.panel > summary {
  cursor: pointer; padding: 12px 16px; font-weight: 600; list-style: none;
  display: flex; justify-content: space-between; align-items: center; gap: 8px;
}
details.panel > summary::-webkit-details-marker { display: none; }
details.panel > summary::after { content: "▾"; color: var(--muted); transition: transform .15s; }
details.panel[open] > summary::after { transform: rotate(180deg); }
.panel-body { padding: 0 16px 16px; }
.filtros { display: grid; grid-template-columns: 1fr; gap: 10px; }
@media (min-width: 620px) { .filtros { grid-template-columns: 1fr 1fr; } .filtros .largo { grid-column: 1 / -1; } }
label.campo { display: flex; flex-direction: column; gap: 4px; font-size: .85rem; color: var(--muted); }
select, input[type="search"] {
  font: inherit; color: var(--text); background: var(--surface-2); border: 1px solid var(--border);
  border-radius: 8px; padding: 9px 10px; width: 100%; min-width: 0;
}
.checks { display: flex; flex-wrap: wrap; gap: 6px 18px; font-size: .92rem; }
.checks label { display: inline-flex; align-items: center; gap: 6px; cursor: pointer; }
.linha { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; justify-content: space-between; margin-top: 12px; }
.contagem { font-size: .92rem; color: var(--muted); }
.contagem b { color: var(--text); }
button {
  font: inherit; cursor: pointer; border-radius: 8px; border: 1px solid var(--border);
  background: var(--surface-2); color: var(--text); padding: 8px 12px;
}
button:hover:not(:disabled) { border-color: var(--accent); }
button:focus-visible, select:focus-visible, input:focus-visible, a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
button.primario { background: var(--accent); border-color: var(--accent); color: #fff; }
:root[data-theme="dark"] button.primario { color: #0d1420; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) button.primario { color: #0d1420; } }
button:disabled { opacity: .45; cursor: default; }
.card { padding: 18px 16px 16px; }
.meta { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin-bottom: 4px; }
.badge {
  font-size: .78rem; font-weight: 600; padding: 3px 8px; border-radius: 999px;
  background: var(--accent-soft); color: var(--accent);
}
.tax { font-size: .85rem; color: var(--muted); margin: 2px 0 10px; }
.aviso { font-size: .86rem; border-radius: 8px; padding: 8px 10px; margin: 8px 0; background: var(--warn-soft); color: var(--warn); }
.aviso.ruim { background: var(--bad-soft); color: var(--bad); }
.enunciado p { margin: 0 0 10px; }
.alts { display: flex; flex-direction: column; gap: 8px; margin-top: 12px; }
.alt-row { display: flex; gap: 6px; align-items: stretch; }
.alt {
  flex: 1; display: flex; gap: 10px; align-items: flex-start; text-align: left;
  background: var(--surface); padding: 10px 12px; line-height: 1.45;
}
.alt .letra {
  flex: none; width: 26px; height: 26px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: .85rem; background: var(--surface-2); border: 1px solid var(--border);
}
.alt.riscada .txt { text-decoration: line-through; color: var(--muted); }
.alt.certa { border-color: var(--ok); background: var(--ok-soft); }
.alt.certa .letra { background: var(--ok); border-color: var(--ok); color: var(--surface); }
.alt.errada { border-color: var(--bad); background: var(--bad-soft); }
.alt.errada .letra { background: var(--bad); border-color: var(--bad); color: var(--surface); }
.alt .tag { margin-left: auto; flex: none; font-size: .78rem; font-weight: 700; padding-left: 8px; }
.alt.certa .tag { color: var(--ok); }
.alt.errada .tag { color: var(--bad); }
.riscar { flex: none; width: 38px; padding: 0; color: var(--muted); font-size: .9rem; }
.resultado { margin-top: 14px; font-weight: 700; }
.resultado.ok { color: var(--ok); }
.resultado.bad { color: var(--bad); }
.links { margin-top: 10px; font-size: .9rem; }
.links h3 { font-size: .85rem; margin: 10px 0 4px; color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: .04em; }
.links ul { margin: 0; padding-left: 18px; }
.links li { margin: 3px 0; }
a { color: var(--accent); overflow-wrap: anywhere; }
.nav { display: grid; grid-template-columns: 1fr auto 1fr; gap: 8px; align-items: center; padding: 12px 16px; border-top: 1px solid var(--border); }
.nav .pos { font-size: .9rem; color: var(--muted); text-align: center; }
.nav .prox { justify-self: end; }
.vazio { padding: 28px 16px; text-align: center; color: var(--muted); }
.stats table { width: 100%; border-collapse: collapse; font-size: .9rem; }
.stats th, .stats td { text-align: left; padding: 6px 4px; border-bottom: 1px solid var(--border); }
.stats td.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.barra { height: 6px; border-radius: 3px; background: var(--surface-2); overflow: hidden; margin-top: 3px; }
.barra span { display: block; height: 100%; background: var(--accent); }
.rodape { margin-top: 18px; font-size: .8rem; color: var(--muted); }
.explic { margin-top: 16px; padding: 12px 14px; border-radius: 10px; background: var(--surface-2); border: 1px solid var(--border); }
.explic h3 { font-size: .95rem; margin: 0 0 2px; }
.explic .ia { font-size: .78rem; color: var(--muted); margin: 0 0 8px; }
.explic p { margin: 0 0 10px; }
.explic ul { margin: 0 0 10px; padding-left: 0; list-style: none; }
.explic li { margin: 4px 0; font-size: .92rem; }
.explic li b { display: inline-block; min-width: 1.4em; }
.explic .fontes { font-size: .85rem; }
.explic .fontes li { margin: 6px 0; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>Banco de Questões</h1>
    <p id="resumo"></p>
  </header>

  <details class="panel" id="painel-filtros" open>
    <summary>Filtros</summary>
    <div class="panel-body">
      <div class="filtros">
        <label class="campo">Prova<select id="f-prova"></select></label>
        <label class="campo">Área<select id="f-area"></select></label>
        <label class="campo largo">Buscar no enunciado e nas alternativas
          <input type="search" id="f-busca" placeholder="ex.: pré-eclâmpsia, Child-Pugh, sífilis"></label>
        <label class="campo">Mostrar<select id="f-situacao">
          <option value="todas">Todas</option>
          <option value="novas">Não respondidas</option>
          <option value="erradas">Que errei</option>
          <option value="certas">Que acertei</option>
        </select></label>
        <div class="checks" style="align-self:end">
          <label><input type="checkbox" id="f-anuladas"> Incluir anuladas</label>
          <label><input type="checkbox" id="f-imagem" checked> Incluir com imagem</label>
          <label><input type="checkbox" id="f-explicacao"> Só com explicação</label>
        </div>
      </div>
      <div class="linha">
        <span class="contagem" id="contagem"></span>
        <button type="button" id="b-embaralhar">Embaralhar</button>
      </div>
    </div>
  </details>

  <section class="panel" id="questao" aria-live="polite"></section>

  <details class="panel stats" id="painel-stats">
    <summary>Seu desempenho</summary>
    <div class="panel-body" id="stats"></div>
  </details>

  <p class="rodape">Questões de provas oficiais (INEP: Revalida e ENAMED; EBSERH: ENARE), com gabarito oficial.
  As explicações foram elaboradas com IA a partir das fontes citadas em cada uma. O progresso fica salvo só neste navegador. Atalhos no teclado: A–E responde, ← → navega.</p>
</div>

<script type="application/json" id="dados">__DADOS__</script>
<script>
(function () {
  "use strict";
  var D = JSON.parse(document.getElementById("dados").textContent);
  var Q = D.questoes, PROVAS = D.provas;
  var CHAVE = "banco-questoes-v1";

  function ler() { try { return JSON.parse(localStorage.getItem(CHAVE)) || {}; } catch (e) { return {}; } }
  function gravar() { try { localStorage.setItem(CHAVE, JSON.stringify(estado)); } catch (e) {} }
  var estado = ler();
  estado.respostas = estado.respostas || {};
  estado.filtros = estado.filtros || {};

  var riscadas = {};
  var lista = [], pos = 0, embaralhado = false;

  function el(tag, attrs, filhos) {
    var n = document.createElement(tag);
    if (attrs) for (var k in attrs) {
      if (k === "class") n.className = attrs[k];
      else if (k === "text") n.textContent = attrs[k];
      else if (k.slice(0, 2) === "on") n.addEventListener(k.slice(2), attrs[k]);
      else n.setAttribute(k, attrs[k]);
    }
    (filhos || []).forEach(function (f) { if (f) n.appendChild(typeof f === "string" ? document.createTextNode(f) : f); });
    return n;
  }
  function norm(s) { return (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); }
  function nomeProva(q) { return q.instituicao + " " + q.ano; }
  Q.forEach(function (q) {
    q._prova = nomeProva(q);
    q._busca = norm(q.enunciado + " " + Object.keys(q.alternativas).map(function (k) { return q.alternativas[k]; }).join(" "));
  });

  var $ = function (id) { return document.getElementById(id); };
  var fProva = $("f-prova"), fArea = $("f-area"), fBusca = $("f-busca"), fSit = $("f-situacao"),
      fAnul = $("f-anuladas"), fImg = $("f-imagem"), fExp = $("f-explicacao");

  function contar(chave) {
    var c = {};
    Q.forEach(function (q) { c[q[chave]] = (c[q[chave]] || 0) + 1; });
    return c;
  }
  function preencher(sel, rotuloTodas, contagens, ordem) {
    sel.appendChild(el("option", { value: "", text: rotuloTodas }));
    ordem.forEach(function (v) { sel.appendChild(el("option", { value: v, text: v + " (" + contagens[v] + ")" })); });
  }
  var porProva = contar("_prova"), porArea = contar("area");
  preencher(fProva, "Todas as provas", porProva, Object.keys(porProva).sort());
  preencher(fArea, "Todas as áreas", porArea, Object.keys(porArea).sort(function (a, b) { return porArea[b] - porArea[a]; }));
  $("resumo").textContent = Q.length + " questões de " + Object.keys(porProva).length + " provas oficiais, com gabarito";

  var f = estado.filtros;
  if (f.prova && porProva[f.prova]) fProva.value = f.prova;
  if (f.area && porArea[f.area]) fArea.value = f.area;
  if (f.busca) fBusca.value = f.busca;
  if (f.situacao) fSit.value = f.situacao;
  if (typeof f.anuladas === "boolean") fAnul.checked = f.anuladas;
  if (typeof f.imagem === "boolean") fImg.checked = f.imagem;
  if (typeof f.explicacao === "boolean") fExp.checked = f.explicacao;
  var comExplicacao = Q.filter(function (q) { return q.explicacao; }).length;
  fExp.parentNode.lastChild.textContent = " Só com explicação (" + comExplicacao + ")";

  function embaralhar(arr) {
    for (var i = arr.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = arr[i]; arr[i] = arr[j]; arr[j] = t; }
    return arr;
  }

  function filtrar(manterAtual) {
    var atual = lista[pos];
    var termos = norm(fBusca.value).split(/\s+/).filter(Boolean);
    var sit = fSit.value;
    lista = Q.filter(function (q) {
      if (fProva.value && q._prova !== fProva.value) return false;
      if (fArea.value && q.area !== fArea.value) return false;
      if (!fAnul.checked && q.anulada) return false;
      if (!fImg.checked && q.tem_imagem) return false;
      if (fExp.checked && !q.explicacao) return false;
      var r = estado.respostas[q.id];
      if (sit === "novas" && r) return false;
      if (sit === "erradas" && !(r && r !== q.gabarito)) return false;
      if (sit === "certas" && !(r && r === q.gabarito)) return false;
      for (var i = 0; i < termos.length; i++) if (q._busca.indexOf(termos[i]) < 0) return false;
      return true;
    });
    if (embaralhado) embaralhar(lista);
    pos = 0;
    if (manterAtual && atual) { var i = lista.indexOf(atual); if (i >= 0) pos = i; }
    estado.filtros = { prova: fProva.value, area: fArea.value, busca: fBusca.value, situacao: sit,
      anuladas: fAnul.checked, imagem: fImg.checked, explicacao: fExp.checked,
      atual: lista[pos] ? lista[pos].id : null };
    gravar();
    $("contagem").innerHTML = "";
    $("contagem").appendChild(el("b", { text: String(lista.length) }));
    $("contagem").appendChild(document.createTextNode(lista.length === 1 ? " questão com esses filtros" : " questões com esses filtros"));
    mostrar();
  }

  function responder(q, letra) {
    if (estado.respostas[q.id] || q.anulada || !q.gabarito) return;
    estado.respostas[q.id] = letra;
    gravar();
    mostrar();
    estatisticas();
  }

  function mostrar() {
    var box = $("questao");
    box.innerHTML = "";
    if (!lista.length) {
      box.appendChild(el("div", { class: "vazio", text: "Nenhuma questão com esses filtros." }));
      return;
    }
    var q = lista[pos];
    estado.filtros.atual = q.id; gravar();
    var resp = estado.respostas[q.id];
    var card = el("div", { class: "card" });

    var meta = el("div", { class: "meta" }, [
      el("span", { class: "badge", text: q._prova }),
      q.numero ? el("span", { class: "badge", text: "Questão " + q.numero }) : null
    ]);
    card.appendChild(meta);
    card.appendChild(el("div", { class: "tax", text: [q.area, q.subarea, q.topico].filter(Boolean).join(" / ") }));

    if (q.anulada) card.appendChild(el("div", { class: "aviso ruim", text: "Questão anulada pela banca. Serve para estudo, mas não tem gabarito válido." }));
    if (q.tem_imagem) card.appendChild(el("div", { class: "aviso", text: "Esta questão tem uma imagem que não está aqui. Consulte o caderno oficial da prova." }));
    if (q.tem_tabela) card.appendChild(el("div", { class: "aviso", text: "Esta questão tem uma tabela; o texto pode ter perdido a formatação." }));
    if (q.situacao_gabarito === "preliminar") card.appendChild(el("div", { class: "aviso", text: "Gabarito preliminar: pode mudar depois dos recursos." }));
    if (q.situacao_gabarito === "informado pelo site") card.appendChild(el("div", { class: "aviso", text: "Gabarito informado pelo site de onde a questão foi salva, não conferido com a banca." }));

    var en = el("div", { class: "enunciado" });
    q.enunciado.split(/\n+/).forEach(function (p) { if (p.trim()) en.appendChild(el("p", { text: p })); });
    card.appendChild(en);

    var alts = el("div", { class: "alts", role: "group", "aria-label": "Alternativas" });
    var riscQ = riscadas[q.id] || (riscadas[q.id] = {});
    Object.keys(q.alternativas).sort().forEach(function (letra) {
      var cls = "alt";
      var tag = null;
      if (resp) {
        if (letra === q.gabarito) { cls += " certa"; tag = letra === resp ? "✓ sua resposta" : "✓ gabarito"; }
        else if (letra === resp) { cls += " errada"; tag = "✗ sua resposta"; }
      }
      if (riscQ[letra]) cls += " riscada";
      var bloqueado = !!resp || q.anulada || !q.gabarito;
      var b = el("button", { type: "button", class: cls, "aria-label": "Alternativa " + letra,
        onclick: function () { responder(q, letra); } }, [
        el("span", { class: "letra", text: letra }),
        el("span", { class: "txt", text: q.alternativas[letra] }),
        tag ? el("span", { class: "tag", text: tag }) : null
      ]);
      if (bloqueado) b.setAttribute("aria-disabled", "true");
      var risc = el("button", { type: "button", class: "riscar", title: "Riscar alternativa", "aria-label": "Riscar alternativa " + letra,
        text: "✕", onclick: function () { riscQ[letra] = !riscQ[letra]; mostrar(); } });
      alts.appendChild(el("div", { class: "alt-row" }, [b, resp ? null : risc]));
    });
    card.appendChild(alts);

    if (resp) {
      var acertou = resp === q.gabarito;
      card.appendChild(el("div", { class: "resultado " + (acertou ? "ok" : "bad"),
        text: acertou ? "Você acertou! Gabarito: " + q.gabarito : "Resposta certa: " + q.gabarito }));
      card.appendChild(el("button", { type: "button", style: "margin-top:8px", text: "Responder de novo",
        onclick: function () { delete estado.respostas[q.id]; gravar(); mostrar(); estatisticas(); } }));
    }
    if (q.observacao) card.appendChild(el("div", { class: "tax", style: "margin-top:10px", text: q.observacao }));

    if (resp && q.explicacao) {
      var ex = q.explicacao;
      var box2 = el("div", { class: "explic" }, [
        el("h3", { text: "Explicação" }),
        el("p", { class: "ia", text: "Elaborada com IA para justificar o gabarito oficial, com base nas fontes abaixo. Confira a recomendação na fonte." }),
        el("p", { text: ex.explicacao })
      ]);
      if (ex.alternativas) {
        var ula = el("ul");
        Object.keys(ex.alternativas).sort().forEach(function (l) {
          ula.appendChild(el("li", null, [el("b", { text: l + ")" }), " " + ex.alternativas[l]]));
        });
        box2.appendChild(ula);
      }
      if (ex.fontes && ex.fontes.length) {
        box2.appendChild(el("h3", { text: "Fontes" }));
        var ulf = el("ul", { class: "fontes" });
        ex.fontes.forEach(function (fo) {
          ulf.appendChild(el("li", null, fo.url
            ? [el("a", { href: fo.url, target: "_blank", rel: "noopener noreferrer", text: fo.citacao })]
            : [fo.citacao]));
        });
        box2.appendChild(ulf);
      }
      card.appendChild(box2);
    }

    if (resp || q.anulada) {
      var info = PROVAS[q._prova] || {};
      var links = el("div", { class: "links" });
      if (info.resolucoes && info.resolucoes.length) {
        links.appendChild(el("h3", { text: "Correções gratuitas desta prova" }));
        var ul = el("ul");
        info.resolucoes.forEach(function (r) {
          ul.appendChild(el("li", null, [el("a", { href: r.url, target: "_blank", rel: "noopener noreferrer", text: r.titulo })]));
        });
        links.appendChild(ul);
      }
      if (info.fonte && /^https?:/.test(info.fonte)) {
        links.appendChild(el("h3", { text: "Prova e gabarito oficiais" }));
        links.appendChild(el("a", { href: info.fonte, target: "_blank", rel: "noopener noreferrer", text: info.fonte }));
      }
      card.appendChild(links);
    }
    box.appendChild(card);

    box.appendChild(el("div", { class: "nav" }, [
      el("button", { type: "button", text: "← Anterior",
        onclick: function () { if (pos > 0) { pos--; mostrar(); topo(); } } }),
      el("span", { class: "pos", text: (pos + 1) + " de " + lista.length }),
      el("button", { type: "button", class: "primario prox", text: "Próxima →",
        onclick: function () { if (pos < lista.length - 1) { pos++; mostrar(); topo(); } } })
    ]));
    var bt = box.querySelectorAll(".nav button");
    bt[0].disabled = pos === 0;
    bt[1].disabled = pos >= lista.length - 1;
  }

  function topo() {
    var r = $("questao").getBoundingClientRect();
    if (r.top < 0) window.scrollTo({ top: window.scrollY + r.top - 8, behavior: "smooth" });
  }

  function estatisticas() {
    var box = $("stats");
    box.innerHTML = "";
    var total = 0, certas = 0, area = {}, prova = {};
    Q.forEach(function (q) {
      var r = estado.respostas[q.id];
      if (!r || !q.gabarito) return;
      var ok = r === q.gabarito;
      total++; if (ok) certas++;
      [[area, q.area], [prova, q._prova]].forEach(function (p) {
        var g = p[0][p[1]] || (p[0][p[1]] = { t: 0, c: 0 }); g.t++; if (ok) g.c++;
      });
    });
    if (!total) { box.appendChild(el("p", { class: "contagem", text: "Responda algumas questões para ver seu desempenho." })); return; }
    box.appendChild(el("p", null, [el("b", { text: certas + " de " + total }), " certas (" + Math.round(100 * certas / total) + "%)"]));
    function tabela(titulo, grupos) {
      var t = el("table");
      t.appendChild(el("tr", null, [el("th", { text: titulo }), el("th", { text: "Acertos", style: "text-align:right" })]));
      Object.keys(grupos).sort().forEach(function (k) {
        var g = grupos[k], pct = Math.round(100 * g.c / g.t);
        var barra = el("div", { class: "barra" }, [el("span", { style: "width:" + pct + "%" })]);
        t.appendChild(el("tr", null, [el("td", null, [k, barra]), el("td", { class: "num", text: g.c + "/" + g.t + " · " + pct + "%" })]));
      });
      return t;
    }
    box.appendChild(tabela("Área", area));
    box.appendChild(el("div", { style: "height:10px" }));
    box.appendChild(tabela("Prova", prova));
    box.appendChild(el("button", { type: "button", style: "margin-top:12px", text: "Zerar progresso",
      onclick: function () {
        if (confirm("Apagar todas as suas respostas salvas neste navegador?")) {
          estado.respostas = {}; gravar(); filtrar(true); estatisticas();
        }
      } }));
  }

  [fProva, fArea, fSit, fAnul, fImg, fExp].forEach(function (c) { c.addEventListener("change", function () { filtrar(false); }); });
  var espera;
  fBusca.addEventListener("input", function () { clearTimeout(espera); espera = setTimeout(function () { filtrar(false); }, 200); });
  $("b-embaralhar").addEventListener("click", function () {
    embaralhado = !embaralhado;
    this.textContent = embaralhado ? "Ordem original" : "Embaralhar";
    filtrar(false);
  });
  document.addEventListener("keydown", function (e) {
    if (e.target.tagName === "INPUT" || e.target.tagName === "SELECT" || e.metaKey || e.ctrlKey || e.altKey) return;
    var q = lista[pos];
    if (e.key === "ArrowRight" && pos < lista.length - 1) { pos++; mostrar(); }
    else if (e.key === "ArrowLeft" && pos > 0) { pos--; mostrar(); }
    else if (q && /^[a-eA-E]$/.test(e.key) && q.alternativas[e.key.toUpperCase()]) responder(q, e.key.toUpperCase());
  });

  if (window.matchMedia && window.matchMedia("(max-width: 619px)").matches && estado.filtros.atual) {
    $("painel-filtros").removeAttribute("open");
  }
  var salvo = estado.filtros.atual;
  filtrar(false);
  if (salvo) { var i = lista.findIndex(function (q) { return q.id === salvo; }); if (i > 0) { pos = i; mostrar(); } }
  estatisticas();
})();
</script>
</body>
</html>
"""


def main():
    with open("questoes/banco.json", encoding="utf-8") as f:
        banco = json.load(f)
    with open("questoes/resolucoes.json", encoding="utf-8") as f:
        resolucoes = json.load(f)

    provas = {}
    for q in banco:
        nome = f"{q['instituicao']} {q['ano']}"
        provas.setdefault(nome, {"fonte": q["fonte"], "resolucoes": resolucoes.get(nome, [])})

    dados = {"questoes": [{k: q[k] for k in CAMPOS} for q in banco], "provas": provas}
    # "<" escapado mantém o JSON válido e impede que um "</script>" no texto feche a tag.
    texto = json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    with open("questoes/banco.html", "w", encoding="utf-8") as f:
        f.write(MODELO.replace("__DADOS__", texto))
    print(f"{len(banco)} questões -> questoes/banco.html")


if __name__ == "__main__":
    main()

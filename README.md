# Banco de questões

Questões de provas de residência médica, ENAMED e Revalida, com gabarito oficial,
em `questoes/banco.html` (página para estudar, funciona offline), `questoes/banco.csv`
(abre no Excel) e `questoes/banco.json`.

A página `banco.html` filtra por prova, área e palavra, corrige ao clicar na alternativa,
mostra os links de correção da prova e guarda o progresso no próprio navegador.

## O que tem

| Prova | Questões | Anuladas | Gabarito | Origem |
|---|---|---|---|---|
| Revalida 2024.1 | 100 | 5 | definitivo | INEP, via medbench-brasil |
| Revalida 2024.2 | 100 | 6 | definitivo | INEP, via medbench-brasil |
| Revalida 2025.1 | 100 | 3 | definitivo | INEP, via medbench-brasil |
| ENAMED 2025 | 100 | 10 | definitivo | INEP, via medbench-brasil |
| ENAMED 2026 | 100 | 0 | **preliminar** | INEP, via medbench-brasil |
| ENARE 2020/2021 (acesso direto) | 100 | 9 | definitivo (pós-recursos) | PDF oficial EBSERH/AOCP |
| ENARE 2023/2024 (acesso direto) | 100 | 0 | **preliminar** | PDF oficial EBSERH/AOCP |
| Revalida 2021 | 1 | 0 | do site | página salva do El Doctor Gabo |

Cada questão traz instituição, ano, número, grande área, enunciado, alternativas,
gabarito, se foi anulada, a situação do gabarito, se depende de imagem/tabela, a fonte
oficial e links de correções gratuitas da prova (`resolucoes`).

Cuidados:
- Questões com `tem_imagem` dependem de uma figura que não está no banco; veja o caderno oficial.
  No ENARE essa marcação é por palavras-chave ("imagem", "figura"...) e pode falhar.
- Gabarito **preliminar** pode mudar após os recursos; confira o definitivo da banca.
- Os links de resolução são páginas de cursinhos encontradas por busca, por prova (não por
  questão). O texto delas não é copiado para o banco.

## Explicações

`dados/explicacoes/<prova>.json` traz explicações elaboradas com IA para justificar o gabarito
oficial: por que a alternativa certa está certa, um comentário por alternativa e as fontes.
Fontes aceitas: diretrizes do Ministério da Saúde, sociedades médicas brasileiras, CDC/FDA e
revisões ou diretrizes em NEJM, Lancet, JAMA, BMJ e periódicos BMC. Cada fonte foi localizada
por busca (existência, autoria, ano, endereço); o texto integral não foi aberto, então confira a
recomendação na fonte. O `montar_banco.py` avisa se uma explicação marcar como correta uma letra
diferente do gabarito oficial.

Feitas até agora: Revalida 2025.1, questões 1 a 30 (28 válidas; a 7 e a 23 foram anuladas).

## Como refazer o banco

```bash
pip install pdfplumber

# Revalida e ENAMED (INEP)
git clone --depth 1 https://github.com/Precisa-Saude/medbench-brasil
python3 scripts/importar_medbench.py medbench-brasil/packages/dataset/data

# Provas em PDF de duas colunas (modelo ENARE/AOCP), caderno + gabarito oficiais
python3 scripts/importar_prova_pdf.py --prova caderno.pdf --paginas 2-27 \
    --gabarito gabarito.pdf --secao "ACESSO DIRETO - TODOS OS PROGRAMAS - PROVA 1" \
    --instituicao ENARE --ano 2023 --situacao preliminar \
    --fonte https://enare.ebserh.gov.br --saida dados/enare-2023.json

# Junta tudo em questoes/banco.json e questoes/banco.csv
python3 scripts/montar_banco.py

# Gera a página questoes/banco.html
python3 scripts/gerar_html.py
```

Use sempre o gabarito da mesma versão (tipo) do caderno.

## Páginas salvas do QBank El Doctor Gabo

1. Responda a questão no site e salve a página (Chrome no Android: ⋮ → ícone ↓; gera `.mhtml`).
2. Coloque os arquivos em `paginas/` (essa pasta não vai para o Git: a página traz nome e e-mail da conta).
3. Rode `python3 scripts/extrair_questoes.py paginas/*.mhtml` e depois `python3 scripts/montar_banco.py`.

Se a questão salva também estiver numa prova oficial do banco, ela não é duplicada: vale o
gabarito oficial. Os comentários do site são conteúdo autoral do El Doctor Gabo e só entram
com `--com-comentarios`, para uso pessoal.

## Fontes e licenças

- Revalida e ENAMED: [medbench-brasil](https://github.com/Precisa-Saude/medbench-brasil)
  (Apache-2.0, Precisa Saúde), extraído dos cadernos e gabaritos oficiais do INEP; convertido
  para o formato deste banco. Licença em `licencas/medbench-brasil-LICENSE.txt`.
- ENARE: caderno de questões e gabarito oficiais publicados pela EBSERH (https://enare.ebserh.gov.br).

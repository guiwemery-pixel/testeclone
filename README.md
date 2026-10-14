# Banco de questões

Extração de questões de residência médica, ENAMED e Revalida para JSON/CSV.

## Páginas salvas do QBank El Doctor Gabo

1. Abra a questão no site e salve a página (Chrome no Android: ⋮ → ícone ↓; gera `.mhtml`).
   Responda a questão antes de salvar, senão o gabarito não aparece na página.
2. Coloque os arquivos em `paginas/` (essa pasta não vai para o Git).
3. Rode:

```bash
python3 scripts/extrair_questoes.py paginas/*.mhtml --saida questoes/questoes
```

O script acrescenta as questões novas a `questoes/questoes.json` e `questoes/questoes.csv`
sem duplicar as que já estão lá.

Por padrão saem só enunciado, alternativas, gabarito e classificação. Os comentários do site
são conteúdo autoral do El Doctor Gabo; `--com-comentarios` os inclui, para uso pessoal.

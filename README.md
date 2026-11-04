# Receita médica em PDF com Gotenberg 8

Cliente que monta uma receita simples em A4 e envia o HTML para o [Gotenberg 8](https://gotenberg.dev/). O script Python é o contrato de layout: os mesmos três documentos e os mesmos campos do formulário são o que uma API Go precisa mandar para gerar o PDF.

O resultado é uma folha com timbre da clínica, dados do paciente, prescrição em HTML livre, assinatura e rodapé com paginação.

## O que o PDF contém

| Faixa | Conteúdo | Onde vive |
| --- | --- | --- |
| Cabeçalho | Logo, clínica, médica e CRM. Repete em toda página. | `header.html` |
| Conteúdo | Título, paciente, prescrição e assinatura. | `index.html` |
| Rodapé | Endereço, contato e página atual. Repete em toda página. | `footer.html` |

A prescrição chega como HTML (`<strong>`, `<em>`, `<u>`, `<br>`). As quebras de linha do texto também são mantidas (`white-space: pre-wrap`).

## Stack

- Gotenberg 8 (`gotenberg/gotenberg:8`), Chromium em `POST /forms/chromium/convert/html`
- Python 3.13 e `requests`, usados como cliente de referência
- Papel A4, margens em milímetros, fundo de impressão ligado

## Como executar

A rede Docker do Compose é externa. Crie uma vez se ela ainda não existir:

```bash
docker network create local_network_docker
docker compose up -d
```

O Gotenberg fica em `http://localhost:3008`.

```bash
python -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python teste-request-pdf.py
```

O arquivo gerado é `relatorio.pdf`.

Dados de exemplo (clínica, paciente, logo e o HTML da prescrição) ficam no topo de `teste-request-pdf.py`.

## Contrato da requisição

Todos os arquivos vão no campo multipart `files`. O Gotenberg escolhe o papel de cada um pelo nome:

- `index.html` — corpo
- `header.html` — cabeçalho
- `footer.html` — rodapé

```text
paperWidth        210mm
paperHeight       297mm
marginTop         22mm
marginBottom      16mm
marginLeft        14mm
marginRight       14mm
printBackground   true
emulatedMediaType print
```

No Chromium, a altura do cabeçalho é `marginTop` e a do rodapé é `marginBottom`. O miolo começa abaixo dessa faixa. Valor sem unidade é interpretado em polegadas.

A paginação usa as classes que o Chromium preenche sozinho: `pageNumber` e `totalPages`.

## Decisões de layout

A logo entra no cabeçalho como data URI. Esse documento não baixa imagem remota.

O cabeçalho é uma tabela. Flexbox e posição absoluta colapsam nesse contexto do Chromium.

`border` e `box-shadow` no cabeçalho ou no rodapé são desenhados de novo na borda da folha. A faixa entre o timbre e o título fica no `index.html`.

A assinatura fica no fim do miolo. O rodapé repete em toda página e só leva contato e número da página.

## Estrutura

```text
docker-compose.yml    Gotenberg 8 na porta 3008
teste-request-pdf.py  HTML da receita e chamada da API
pyproject.toml        Dependência do cliente Python
relatorio.pdf         Saída da última execução
```

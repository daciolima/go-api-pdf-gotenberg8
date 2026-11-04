import base64

import requests
from pathlib import Path

GOTENBERG_URL = "http://localhost:3008"

# Dados da clínica — no Go, isto vira struct preenchida pela API.
LOGO_URL = "https://placehold.co/140x80"
CLINICA = "Clínica Exemplo Saúde"
MEDICO = "Dra. Ana Beatriz Lima"
CRM = "CRM-PB 12345"
ESPECIALIDADE = "Clínico Geral"
ENDERECO = "Av. Exemplo, 123 - Centro - João Pessoa/PB"
CONTATO = "Tel (83) 3333-0000 · contato@clinicaexemplo.com.br"

# HTML da receita. Entra no miolo sem escape, para o Chromium aplicar as tags.
PRESCRICAO = """1. Dipirona 500 mg — comprimido
<strong>Tomar 1 comprimido de 6 em 6 horas, se dor ou febre.</strong>
Via oral · Duração: 5 dias · Quantidade: 20 comprimidos

2. Loratadina 10 mg — comprimido
<strong>Tomar 1 comprimido uma vez ao dia.</strong>
Via oral · Duração: 10 dias · Quantidade: 10 comprimidos

3. Soro fisiológico 0,9% — solução nasal
<strong>Aplicar 2 jatos em cada narina, 3 vezes ao dia.</strong>
Uso nasal · Duração: enquanto houver sintomas · Quantidade: 1 frasco

<strong>Orientações</strong>
Retornar em 7 dias se não houver melhora. Não usar outro analgésico junto com a dipirona sem orientação."""

# Margens em mm. No Chromium a faixa do header é exatamente marginTop
# e a do footer é marginBottom. O miolo começa abaixo dessa faixa.
MARGEM_TOPO = "22mm"
MARGEM_BASE = "16mm"
MARGEM_LATERAL = "14mm"


def mime_imagem(conteudo: bytes, header: str) -> str:
    if conteudo.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if conteudo.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if conteudo.startswith(b"GIF87a") or conteudo.startswith(b"GIF89a"):
        return "image/gif"
    if conteudo.startswith(b"RIFF") and conteudo[8:12] == b"WEBP":
        return "image/webp"
    if header.startswith("image/"):
        return header.split(";", 1)[0].strip()
    return "image/jpeg"


logo_response = requests.get(LOGO_URL, timeout=30)
logo_response.raise_for_status()
logo_mime = mime_imagem(
    logo_response.content,
    logo_response.headers.get("Content-Type", ""),
)
logo_base64 = base64.b64encode(logo_response.content).decode("ascii")
LOGO_SRC = f"data:{logo_mime};base64,{logo_base64}"

# Header e footer são documentos isolados. O Chromium injeta o texto
# nas classes pageNumber e totalPages. Imagem remota não carrega aqui:
# a logo precisa ir em data URI. Tabela é o layout que o header do
# Chromium respeita. border e box-shadow aqui são redesenhados na
# borda da folha, então a faixa entre timbre e receita fica no miolo.
HEADER = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        html, body {{
            width: 100%;
            font-family: Arial, Helvetica, sans-serif;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }}

        body {{
            padding: 2px {MARGEM_LATERAL} 0;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        td {{
            vertical-align: middle;
        }}

        .logo {{
            width: 85px;
        }}

        .logo img {{
            width: 100%;
            height: auto;
            object-fit: contain;
            object-position: center center;
        }}

        .info {{
            text-align: right;
            line-height: 1.25;
            padding-bottom: 6px;
        }}

        .clinica {{
            font-size: 13px;
            font-weight: 700;
            color: #1a5276;
            letter-spacing: 0.3px;
        }}

        .medico {{
            font-size: 11px;
            font-weight: 700;
            color: #222;
        }}

        .meta {{
            font-size: 9px;
            color: #555;
        }}
    </style>
</head>
<body>
    <table>
        <tr>
            <td class="logo"><img src="{LOGO_SRC}" alt="Logo"></td>
            <td class="info">
                <div class="clinica">{CLINICA}</div>
                <div class="medico">{MEDICO}</div>
                <div class="meta">{CRM} · {ESPECIALIDADE}</div>
            </td>
        </tr>
    </table>
</body>
</html>
"""

FOOTER = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        html, body {{
            width: 100%;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 8px;
            color: #555;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }}

        body {{
            padding: 0 {MARGEM_LATERAL};
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        td {{
            vertical-align: top;
            padding-top: 4px;
            line-height: 1.35;
        }}

        .endereco {{
            text-align: left;
        }}

        .pagina {{
            width: 90px;
            text-align: right;
            white-space: nowrap;
            color: #333;
        }}
    </style>
</head>
<body>
    <table>
        <tr>
            <td class="endereco">
                {ENDERECO}<br>
                {CONTATO}
            </td>
            <td class="pagina">
                Página <span class="pageNumber"></span> de <span class="totalPages"></span>
            </td>
        </tr>
    </table>
</body>
</html>
"""

# Miolo da receita. A assinatura fica no corpo, só no fim do documento.
# O footer repete em toda página e não deve carregar a assinatura.
HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * {
            box-sizing: border-box;
        }

        html, body {
            margin: 0;
            padding: 0;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 11px;
            color: #222;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }

        .titulo {
            margin: 0 0 12px;
            padding-top: 25px;
            border-top: 2px solid #1a5276;
            text-align: center;
            font-size: 15px;
            font-weight: 700;
            letter-spacing: 2px;
            color: #1a5276;
        }

        .paciente {
            width: 100%;
            border-collapse: collapse;
            margin-top: 25px;
            margin-bottom: 16px;
            background: #f4f8fb;
            border: 1px solid #d6e2ec;
        }

        .paciente td {
            padding: 5px 10px;
            vertical-align: top;
        }

        .paciente .rotulo {
            width: 118px;
            color: #5d6d7e;
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }

        .paciente .valor {
            font-size: 11px;
            font-weight: 700;
        }

        .secao {
            margin: 0 0 8px;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.8px;
            text-transform: uppercase;
            color: #1a5276;
        }

        .prescricao {
            min-height: 220px;
            padding: 10px 12px;
            border: 1px solid #c5d4e0;
            background: #fff;
            font-size: 12px;
            line-height: 1.5;
            white-space: pre-wrap;
            overflow-wrap: break-word;
        }

        .assinatura {
            margin-top: 28px;
            page-break-inside: avoid;
            break-inside: avoid;
        }

        .local-data {
            text-align: right;
            margin-bottom: 26px;
        }

        .bloco-assinatura {
            width: 240px;
            margin-left: auto;
            text-align: center;
        }

        .linha {
            border-top: 1px solid #222;
            margin-bottom: 4px;
        }

        .nome-medico {
            font-weight: 700;
        }

        .crm {
            font-size: 10px;
            color: #444;
        }
    </style>
</head>
<body>
    <h1 class="titulo">RECEITA MÉDICA</h1>

    <table class="paciente">
        <tr>
            <td class="rotulo">Paciente</td>
            <td class="valor">Maria das Dores Silva</td>
            <td class="rotulo">Emissão</td>
            <td class="valor">04/11/2026</td>
        </tr>
        <tr>
            <td class="rotulo">Nascimento</td>
            <td class="valor">12/03/1985</td>
            <td class="rotulo">CPF</td>
            <td class="valor">123.456.789-09</td>
        </tr>
    </table>

    <p class="secao">Prescrição</p>

    <div class="prescricao">__PRESCRICAO__</div>

    <div class="assinatura">
        <div class="local-data">João Pessoa, 04 de novembro de 2026</div>
        <div class="bloco-assinatura">
            <div class="linha"></div>
            <div class="nome-medico">Dra. Ana Beatriz Lima</div>
            <div class="crm">CRM-PB 12345 · Clínico Geral</div>
        </div>
    </div>
</body>
</html>
"""
HTML = HTML.replace("__PRESCRICAO__", PRESCRICAO)

# Gotenberg 8 identifica header/footer pelo nome do arquivo.
# Todos os arquivos vão no campo "files". Campo com outro nome é ignorado.
url = f"{GOTENBERG_URL}/forms/chromium/convert/html"
arquivos = [
    ("files", ("index.html", HTML.encode("utf-8"), "text/html; charset=utf-8")),
    ("files", ("header.html", HEADER.encode("utf-8"), "text/html; charset=utf-8")),
    ("files", ("footer.html", FOOTER.encode("utf-8"), "text/html; charset=utf-8")),
]
formulario = {
    "paperWidth": "210mm",
    "paperHeight": "297mm",
    "marginTop": MARGEM_TOPO,
    "marginBottom": MARGEM_BASE,
    "marginLeft": MARGEM_LATERAL,
    "marginRight": MARGEM_LATERAL,
    "printBackground": "true",
    "emulatedMediaType": "print",
    "scale": "1",
}

response = requests.post(url, files=arquivos, data=formulario, timeout=120)

if response.status_code == 200:
    Path("relatorio.pdf").write_bytes(response.content)
    print("PDF gerado com sucesso: relatorio.pdf")
else:
    print(f"Erro: {response.status_code}")
    print(response.text)

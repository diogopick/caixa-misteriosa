"""
Verifica a página da Caixa Misteriosa da WebContinental e avisa no Telegram
quando os contadores mudam (ex.: novas caixas liberadas).

Usa só a biblioteca padrão do Python (nada para instalar).
Variáveis de ambiente necessárias: TELEGRAM_TOKEN e TELEGRAM_CHAT_ID.
"""

import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

URL = "https://www.webcontinental.com.br/caixa-misteriosa"
ARQUIVO_ESTADO = Path("estado.json")

TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
}


def baixar_pagina() -> str:
    req = urllib.request.Request(URL, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extrair_texto(pagina_html: str) -> str:
    """Remove scripts, estilos e tags, deixando só o texto da página."""
    sem_scripts = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", pagina_html)
    sem_tags = re.sub(r"(?s)<[^>]+>", " ", sem_scripts)
    return re.sub(r"\s+", " ", html.unescape(sem_tags))


def ler_contador(texto: str, rotulo: str):
    """Os dígitos aparecem separados antes do rótulo, ex.: '5 2 2 Caixas já foram liberadas'."""
    m = re.search(r"((?:\d\s*){1,7})" + rotulo, texto, re.IGNORECASE)
    if not m:
        return None
    return int(re.sub(r"\D", "", m.group(1)))


def enviar_telegram(mensagem: str) -> None:
    if not TOKEN or not CHAT_ID:
        print("[aviso] Telegram não configurado. Mensagem:\n" + mensagem)
        return
    dados = urllib.parse.urlencode(
        {"chat_id": CHAT_ID, "text": mensagem, "disable_web_page_preview": "true"}
    ).encode()
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    urllib.request.urlopen(url, data=dados, timeout=30)


def carregar_estado() -> dict:
    if ARQUIVO_ESTADO.exists():
        return json.loads(ARQUIVO_ESTADO.read_text(encoding="utf-8"))
    return {}


def salvar_estado(estado: dict) -> None:
    ARQUIVO_ESTADO.write_text(json.dumps(estado, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    estado = carregar_estado()

    try:
        texto = extrair_texto(baixar_pagina())
    except Exception as erro:  # site fora do ar, bloqueio etc.
        print(f"Erro ao acessar a página: {erro}")
        if not estado.get("erro_avisado"):
            enviar_telegram(f"⚠️ Não consegui acessar a página da caixa misteriosa: {erro}")
            estado["erro_avisado"] = True
            salvar_estado(estado)
        sys.exit(0)

    liberadas = ler_contador(texto, r"Caixas j[áa] foram liberadas")
    disponiveis = ler_contador(texto, r"Caixas ainda dispon[íi]veis")
    print(f"Liberadas: {liberadas} | Disponíveis: {disponiveis}")

    if liberadas is None and disponiveis is None:
        # A página mudou de formato ou os números passaram a vir por JavaScript.
        if not estado.get("erro_avisado"):
            enviar_telegram(
                "⚠️ Não encontrei os contadores na página da caixa misteriosa. "
                "Talvez o site tenha mudado. Confira: " + URL
            )
            estado["erro_avisado"] = True
            salvar_estado(estado)
        return

    anterior_lib = estado.get("liberadas")
    anterior_disp = estado.get("disponiveis")

    if anterior_lib is None:
        enviar_telegram(
            "✅ Monitor da Caixa Misteriosa ativado!\n"
            f"Liberadas: {liberadas}\nDisponíveis: {disponiveis}\n{URL}"
        )
    elif liberadas != anterior_lib:
        enviar_telegram(
            "🎁 NOVAS CAIXAS LIBERADAS!\n"
            f"Liberadas: {anterior_lib} → {liberadas}\n"
            f"Disponíveis: {anterior_disp} → {disponiveis}\n"
            f"Corre: {URL}"
        )
    else:
        print("Sem novas liberações.")

    salvar_estado({"liberadas": liberadas, "disponiveis": disponiveis, "erro_avisado": False})


if __name__ == "__main__":
    main()

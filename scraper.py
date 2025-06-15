import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def buscar_fontes():
    try:
        response = supabase.table("fontes_monitoradas").select("*").eq("ativo", True).execute()
        return response.data
    except Exception as e:
        print(f"Erro ao buscar fontes: {e}")
        return []

def coletar_e_salvar(fonte):
    try:
        html = requests.get(fonte["url"], timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        titulos = soup.select(fonte["seletor_titulo"])[:5]

        for t in titulos:
            titulo = t.get_text(strip=True)
            link_tag = t.find_parent("a") or t.find("a")
            link = link_tag["href"] if link_tag and link_tag.has_attr("href") else fonte["url"]
            prazo_tag = soup.select_one(fonte["seletor_prazo"]) if fonte["seletor_prazo"] else None
            prazo = prazo_tag.get_text(strip=True) if prazo_tag else "Não informado"

            registro = {
                "titulo": titulo,
                "tipo": fonte["tipo"],
                "area": "Audiovisual",
                "valor": "Ver edital",
                "prazo": prazo,
                "link": link
            }

            supabase.table("oportunidades").insert(registro).execute()
            print(f"Inserido: {titulo}")

    except Exception as e:
        print(f"Erro ao processar fonte '{fonte['nome']}': {e}")

def main():
    fontes = buscar_fontes()
    for fonte in fontes:
        coletar_e_salvar(fonte)

if __name__ == "__main__":
    main()

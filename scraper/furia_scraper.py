import cloudscraper
from bs4 import BeautifulSoup
import json
import os

# URL da página da FURIA na HLTV
URL = "https://www.hltv.org/team/8297/furia"

def scrape_furia():
    scraper = cloudscraper.create_scraper()

    response = scraper.get(URL)
    if response.status_code != 200:
        print(f"Erro ao acessar a HLTV: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # --- Elenco ---
    elenco = []
    bodyshot_section = soup.find('div', class_='bodyshot-team')
    if bodyshot_section:
        players_links = bodyshot_section.find_all('a')
        for player_link in players_links:
            nome = player_link.get('title', '').strip()
            perfil = "https://www.hltv.org" + player_link.get('href')
            if nome:
                elenco.append({
                    "nome": nome,
                    "perfil": perfil
                })

    # --- Ranking e estatísticas ---
    ranking_section = soup.find('div', class_='profile-team-stat')
    if ranking_section:
        ranking = ranking_section.get_text(strip=True)
    else:
        ranking = "Não encontrado"

    # --- Partidas recentes ---
    partidas = []
    matches_url = "https://www.hltv.org/results?team=8297"
    matches_response = scraper.get(matches_url)
    if matches_response.status_code == 200:
        matches_soup = BeautifulSoup(matches_response.text, 'html.parser')
        match_containers = matches_soup.find_all('div', class_='result-con')

        for match in match_containers[:10]:  # Últimas 10 partidas
            teams = match.find_all('div', class_='team')
            scores = match.find('td', class_='result-score')

            if len(teams) == 2 and scores:
                partidas.append({
                    "adversario": teams[1].get_text(strip=True),
                    "resultado": scores.get_text(strip=True)
                })

    # --- Organizando dados ---
    furia_data = {
        "elenco": elenco,
        "ranking": ranking,
        "partidas_recentes": partidas
    }

    # --- Salvando em JSON na pasta /data ---
    output_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'furia.json')

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(furia_data, f, ensure_ascii=False, indent=4)

    print(f"Dados da FURIA salvos em {output_path}!")

if __name__ == "__main__":
    scrape_furia()

import cloudscraper
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# URL da página da FURIA na HLTV
URL = "https://www.hltv.org/team/8297/furia"

def get_upcoming_matches(scraper, modo_teste=False):
    # Acessa a página específica da FURIA com a aba de partidas
    url = "https://www.hltv.org/team/8297/furia#tab-matchesBox"
    response = scraper.get(url)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    matches = []
    
    # Encontra a seção "Upcoming matches" (usando o ID da div)
    upcoming_section = soup.find('div', {'id': 'matchesBox'})
    if not upcoming_section:
        return []

    # Extrai todas as linhas de partidas
    match_rows = upcoming_section.find_all('div', class_='match')
    
    for row in match_rows:
        # Extrai times
        team1 = row.find('div', class_='team1')
        team2 = row.find('div', class_='team2')
        
        if team1 and team2:
            team1_name = team1.get_text(strip=True)
            team2_name = team2.get_text(strip=True)

            # Filtra apenas partidas da FURIA (a menos que seja modo teste)
            if modo_teste or 'FURIA' in team1_name or 'FURIA' in team2_name:
                # Extrai data e evento
                time = row.find('div', class_='time')
                event = row.find('div', class_='event')
                
                match_data = {
                    "adversario": team2_name if 'FURIA' in team1_name else team1_name,
                    "data": time.get_text(strip=True) if time else "Em breve",
                    "campeonato": event.get_text(strip=True) if event else "Campeonato não definido",
                    "status": "upcoming",
                    "timestamp": int(datetime.now().timestamp())
                }

                # Extrai logo do adversário (se existir)
                opponent_team = team2 if 'FURIA' in team1_name else team1
                opponent_img = opponent_team.find('img')
                if opponent_img and 'src' in opponent_img.attrs:
                    match_data["logo_adversario"] = "https://www.hltv.org" + opponent_img['src']
                
                matches.append(match_data)

    return matches[:5]

def get_live_match_details(scraper, match_id):
    """Busca detalhes específicos de uma partida ao vivo"""
    url = f"https://www.hltv.org/live{match_id}/_"
    response = scraper.get(url)
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Obter times
    team1 = soup.find('div', class_='team1-gradient')
    team2 = soup.find('div', class_='team2-gradient')
    
    if not team1 or not team2:
        return None
    
    team1_name = team1.find('div', class_='teamName').get_text(strip=True) if team1 else None
    team2_name = team2.find('div', class_='teamName').get_text(strip=True) if team2 else None
    
    # Obter placar
    score_team1 = team1.find('div', class_='currentMapScore').get_text(strip=True) if team1.find('div', class_='currentMapScore') else '0'
    score_team2 = team2.find('div', class_='currentMapScore').get_text(strip=True) if team2.find('div', class_='currentMapScore') else '0'
    
    # Obter mapa atual
    current_map = soup.find('div', class_='mapname-holder').get_text(strip=True) if soup.find('div', class_='mapname-holder') else 'Mapa desconhecido'
    
    # Obter evento/torneio
    event = soup.find('div', class_='event').get_text(strip=True) if soup.find('div', class_='event') else 'Evento desconhecido'
    
    # Obter link da transmissão
    stream_link = None
    stream_div = soup.find('div', class_='stream-box')
    if stream_div and stream_div.find('a'):
        stream_link = stream_div.find('a')['href']
    
    return {
        "adversario": team2_name if 'FURIA' in team1_name else team1_name,
        "resultado": f"{score_team1}-{score_team2}",
        "data": "AO VIVO AGORA",
        "campeonato": event,
        "status": "live",
        "current_map": current_map,
        "logo_adversario": f"https://www.hltv.org{team2.find('img')['src']}" if 'FURIA' in team1_name and team2.find('img') else f"https://www.hltv.org{team1.find('img')['src']}" if team1.find('img') else None,
        "link_transmissao": stream_link
    }

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
            perfil = "https://www.hltv.org/team/8297/furia" + player_link.get('href')
            nickname = player_link.find('div', class_='nickname')
            nickname = nickname.get_text(strip=True) if nickname else nome.split()[0]
            
            player_id = player_link.get('href').split('/')[-2] if player_link.get('href') else ''
            
            if nome:
                elenco.append({
                    "nome": nome,
                    "nickname": nickname,
                    "perfil": perfil,
                    "player_id": player_id
                })

    #Ranking e estatísticas
    ranking_section = soup.find('div', class_='profile-team-stat')
    if ranking_section:
        ranking = ranking_section.get_text(strip=True)
    else:
        ranking = "Não encontrado"

    #Partidas recentes
    partidas = []
    matches_url = "https://www.hltv.org/results?team=8297"
    matches_response = scraper.get(matches_url)
    if matches_response.status_code == 200:
        matches_soup = BeautifulSoup(matches_response.text, 'html.parser')
        match_containers = matches_soup.find_all('div', class_='result-con')

        for match in match_containers[:5]:  # Últimas 5 partidas
            teams = match.find_all('div', class_='team')
            scores = match.find('td', class_='result-score')
            event = match.find('span', class_='event-name')
            
            if len(teams) == 2 and scores:
                partidas.append({
                    "adversario": teams[1].get_text(strip=True),
                    "resultado": scores.get_text(strip=True),
                    "campeonato": event.get_text(strip=True) if event else "Campeonato não definido",
                    "status": "completed"
                })

    #Partidas futuras/ao vivo
    partidas_futuras = get_upcoming_matches(scraper, modo_teste=False)

    #Organizando dados
    furia_data = {
        "elenco": elenco,
        "ranking": ranking,
        "partidas_recentes": partidas,
        "partidas_futuras": partidas_futuras,
        "ultima_atualizacao": datetime.now().isoformat()
    }

    #Salvando em JSON
    output_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'furia.json')

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(furia_data, f, ensure_ascii=False, indent=4)

    print(f"Dados da FURIA salvos em {output_path}!")

if __name__ == "__main__":
    scrape_furia()
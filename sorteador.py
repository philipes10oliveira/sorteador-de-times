import streamlit as st
import random
from collections import defaultdict

# Configuração da página
st.set_page_config(page_title="Sorteador de Times", page_icon="⚽", layout="centered")

# --- INJEÇÃO DE CSS CUSTOMIZADO (IGUAL AO SEU DESIGN) ---
st.markdown("""
<style>
    /* Fundo escuro idêntico ao design */
    .stApp {
        background-color: #0f192c !important;
        color: #ffffff;
    }

    /* Centraliza o bloco principal */
    .main .block-container {
        max-width: 620px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Esconde elementos padrão do Streamlit */
    #MainMenu, header, footer {visibility: hidden;}

    /* Título com destaque verde */
    .custom-title {
        text-align: center;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 25px;
        color: #ffffff;
    }
    .custom-title span {
        color: #10b981;
    }

    /* Estilização das Caixas de Texto (Efeito de Borda Verde Neon) */
    .stTextArea textarea, .stTextInput input {
        background-color: #182238 !important;
        color: #ffffff !important;
        border: 1px solid #2a374e !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    .stTextArea textarea:hover, .stTextArea textarea:focus,
    .stTextInput input:hover, .stTextInput input:focus {
        border-color: #10b981 !important;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.3) !important;
    }

    /* Botão Principal Expandido (100% da largura da tela) */
    div.stButton {
        width: 100% !important;
    }
    div.stButton > button {
        background: linear-gradient(180deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
        border: 1px solid #10b981 !important;
        border-radius: 10px !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        padding: 16px !important;
        width: 100% !important;
        display: block !important;
        margin-top: 15px !important;
        transition: transform 0.15s ease, box-shadow 0.2s ease !important;
    }
    div.stButton > button:hover {
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.4) !important;
        transform: translateY(-2px) !important;
    }
    div.stButton > button:active {
        transform: scale(0.95) !important;
    }

    /* Estilização dos Cards de Resultado (Segunda Tela) */
    .racha-title-display {
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-top: 30px;
        margin-bottom: 20px;
        animation: slideDown 0.5s ease-out;
    }

    .team-card-result {
        background-color: #132231;
        border: 1px solid #1e3a40;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 15px;
        animation: slideDown 0.5s ease-out;
    }

    .team-card-header {
        font-size: 18px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 10px;
    }

    .player-line {
        font-size: 15px;
        color: #e2e8f0;
        margin: 6px 0;
        font-weight: 500;
    }

    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
st.markdown('<h1 class="custom-title"><span>Sorteador</span> de Times</h1>', unsafe_allow_html=True)

# --- FORMULÁRIO DE ENTRADA ---
st.markdown("**Insira o nome dos atletas**")
exemplo_padrao = """Felipe, meio campo, 3
Pedro, atacante, 3
Marcos, zagueiro, 4
Arthur, goleiro, 4"""

texto_jogadores = st.text_area("", value=exemplo_padrao, height=150, label_visibility="collapsed")
st.caption("Adicione uma “ , ” para separar o nome da posição e o valor de estrelas, ex: Felipe, Meio campo, 3")

st.write("")

col1, col2 = st.columns([1, 1])
with col1:
    num_times = int(st.number_input("Quantidade de Times:", min_value=2, max_value=10, value=2))

nome_racha = st.text_input("", placeholder="Ex: Racha do Venancio (Opcional)", label_visibility="collapsed")

st.write("")


# --- LÓGICA DE PROCESSAMENTO E SORTEIO ---
def processar_jogadores(texto):
    jogadores = []
    linhas = texto.strip().split("\n")
    for linha in linhas:
        partes = [p.strip() for p in linha.split(",") if p.strip()]
        if len(partes) >= 3:
            nome = partes[0]
            posicao = partes[1].capitalize()
            try:
                nota_str = partes[2].replace(",", ".")
                nivel = float(nota_str)
                nivel = max(1.0, min(5.0, nivel))
            except ValueError:
                nivel = 3.0
            jogadores.append({"nome": nome, "posicao": posicao, "nivel": nivel})
    return jogadores


def sortear_times_equilibrados(jogadores, num_times):
    # Dicionário auxiliar para controlar quantas vezes cada posição já entrou no time
    times = [{"jogadores": [], "soma_nivel": 0.0, "posicoes_count": defaultdict(int)} for _ in range(num_times)]

    # 1. Isolamento e distribuição de 1 estrela (nota <= 1.0)
    jogadores_uma_estrela = [j for j in jogadores if j["nivel"] <= 1.0]
    demais_jogadores = [j for j in jogadores if j["nivel"] > 1.0]

    random.shuffle(jogadores_uma_estrela)

    for idx, jogador in enumerate(jogadores_uma_estrela):
        time_destino = times[idx % num_times]
        time_destino["jogadores"].append(jogador)
        time_destino["soma_nivel"] += jogador["nivel"]
        time_destino["posicoes_count"][jogador["posicao"]] += 1

    # 2. Agrupamento dos DEMAIS por posição
    posicoes = defaultdict(list)
    for j in demais_jogadores:
        posicoes[j["posicao"]].append(j)

    for pos in posicoes:
        random.shuffle(posicoes[pos])
        posicoes[pos].sort(key=lambda x: x["nivel"], reverse=True)

    # 3. Distribuição garantindo a REGRA DE POSIÇÕES ÚNICAS
    for pos, lista_jogadores in posicoes.items():
        total_na_posicao = len(lista_jogadores)

        # Se a quantidade de jogadores da posição for <= número de times,
        # CADA TIME SÓ PODE RECEBER NO MÁXIMO 1 DESSA POSIÇÃO
        max_por_time = 1 if total_na_posicao <= num_times else 999

        for jogador in lista_jogadores:
            # Filtra apenas os times elegíveis que ainda não estouraram o limite dessa posição
            times_elegiveis = [
                t for t in times if t["posicoes_count"][pos] < max_por_time
            ]

            # Caso de emergência (se todos os elegíveis esgotarem)
            if not times_elegiveis:
                times_elegiveis = times

            # Ordena os elegíveis para priorizar quem tem menos jogadores e menor soma de nível
            times_elegiveis.sort(key=lambda t: (len(t["jogadores"]), t["soma_nivel"]))

            time_escolhido = times_elegiveis[0]
            time_escolhido["jogadores"].append(jogador)
            time_escolhido["soma_nivel"] += jogador["nivel"]
            time_escolhido["posicoes_count"][pos] += 1

    return times


# --- BOTÃO DE AÇÃO E EXIBIÇÃO DO RESULTADO ---
if st.button("Sortear Times"):
    jogadores = processar_jogadores(texto_jogadores)

    if len(jogadores) < num_times:
        st.error(f"Você precisa cadastrar pelo menos {num_times} jogadores válidos!")
    else:
        times_sorteados = sortear_times_equilibrados(jogadores, num_times)

        # Exibe o Nome do Racha (se preenchido)
        titulo_exibicao = nome_racha if nome_racha.strip() else "Times Sorteados"
        st.markdown(f'<div class="racha-title-display">{titulo_exibicao}</div>', unsafe_allow_html=True)

        cols_resultado = st.columns(num_times)

        for idx, time in enumerate(times_sorteados):
            with cols_resultado[idx % num_times]:
                html_card = f'<div class="team-card-result"><div class="team-card-header">Time {idx + 1}</div>'
                for j in time["jogadores"]:
                    html_card += f'<div class="player-line">{j["nome"]}, {j["posicao"]}, {int(j["nivel"])}</div>'
                html_card += '</div>'
                st.markdown(html_card, unsafe_allow_html=True)
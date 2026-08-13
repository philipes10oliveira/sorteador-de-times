import streamlit as st
import random
from collections import defaultdict

# Configuração da página
st.set_page_config(page_title="Sorteador de Times Pro", page_icon="⚽", layout="wide")

# CSS para estilização visual
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
        color: white;
        font-weight: bold;
        font-size: 18px;
        border: none;
        border-radius: 8px;
        padding: 10px;
        margin-top: 10px;
    }
    .player-badge {
        display: inline-block;
        background-color: #262730;
        border: 1px solid #464b5d;
        border-radius: 6px;
        padding: 4px 8px;
        margin: 3px;
        font-size: 14px;
    }
    .pos-badge {
        background-color: #007bff;
        color: white;
        border-radius: 4px;
        padding: 2px 6px;
        font-size: 11px;
        font-weight: bold;
    }
    .stars {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚽ Racha dos Venancio e Amigos")
st.caption("Separe os times garantindo equilíbrio de nível e distribuição por posições!")

col_esq, col_dir = st.columns([1.2, 0.8])

with col_esq:
    st.markdown("### 📋 Lista de Jogadores")
    st.info("Digite um jogador por linha no formato: **Nome, Posição, Nível (1 a 5)**\n\n*Exemplo: Felipe, Meia, 4*")

    exemplo_padrao = """Felipe, Meia, 4
Carlos, Goleiro, 5
Lucas, Ataque, 3
Matheus, Zagueiro, 4
Gabriel, Goleiro, 4
Bruno, Meia, 5
Rodrigo, Ataque, 4
André, Zagueiro, 3
Thiago, Meia, 3
Leo, Ataque, 5"""

    texto_jogadores = st.text_area("Lista de Entrada:", value=exemplo_padrao, height=280)

with col_dir:
    st.markdown("### ⚙️ Configurações do Sorteio")
    num_times = int(st.number_input("Número de times:", min_value=2, max_value=10, value=2))

    st.markdown("---")
    st.markdown("💡 **Posições recomendadas:** Goleiro, Zagueiro, Meia, Ataque.")


# Lógica de processamento e sorteio
def processar_jogadores(texto):
    jogadores = []
    linhas = texto.strip().split("\n")
    for linha in linhas:
        partes = [p.strip() for p in linha.split(",") if p.strip()]
        if len(partes) >= 3:
            nome = partes[0]
            posicao = partes[1].capitalize()
            try:
                # Mudamos de int() para float() para aceitar decimais (ex: 4.5 ou 3.5)
                # Aceita tanto ponto (4.5) quanto vírgula (4,5) se o usuário digitar
                nota_str = partes[2].replace(",", ".")
                nivel = float(nota_str)
                nivel = max(1.0, min(5.0, nivel))  # Força ficar entre 1.0 e 5.0
            except ValueError:
                nivel = 3.0  # Valor padrão se a nota for inválida

            jogadores.append({"nome": nome, "posicao": posicao, "nivel": nivel})
    return jogadores


def sortear_times_equilibrados(jogadores, num_times):
    times = [{"jogadores": [], "soma_nivel": 0.0} for _ in range(num_times)]

    # 1. Separa jogadores com 1 estrela (nota <= 1.0) dos demais
    jogadores_uma_estrela = [j for j in jogadores if j["nivel"] <= 1.0]
    demais_jogadores = [j for j in jogadores if j["nivel"] > 1.0]

    # Embaralha para que o sorteio de 1 estrela seja aleatório entre os times
    random.shuffle(jogadores_uma_estrela)

    # 2. REGRA ESPECIAL: Distribui os de 1 estrela (1 por time sequencialmente)
    for idx, jogador in enumerate(jogadores_uma_estrela):
        time_destino = times[idx % num_times]
        time_destino["jogadores"].append(jogador)
        time_destino["soma_nivel"] += jogador["nivel"]

    # 3. Agrupa os DEMAIS jogadores por posição para manter o equilíbrio de posições e notas
    posicoes = defaultdict(list)
    for j in demais_jogadores:
        posicoes[j["posicao"]].append(j)

    for pos in posicoes:
        random.shuffle(posicoes[pos])
        posicoes[pos].sort(key=lambda x: x["nivel"], reverse=True)

    # 4. Distribui os demais jogadores priorizando times com menor quantidade e menor soma de nota
    for pos, lista_jogadores in posicoes.items():
        for jogador in lista_jogadores:
            # Ordena os times para dar prioridade ao time com menos jogadores ou menor nota total
            times.sort(key=lambda t: (len(t["jogadores"]), t["soma_nivel"]))
            times[0]["jogadores"].append(jogador)
            times[0]["soma_nivel"] += jogador["nivel"]

    # Ordena os times pelo número/índice para manter a exibição organizada
    return times


if st.button("🚀 Sortear Times"):
    jogadores = processar_jogadores(texto_jogadores)

    if len(jogadores) < num_times:
        st.error(f"Você precisa cadastrar pelo menos {num_times} jogadores válidos!")
    else:
        st.balloons()
        times_sorteados = sortear_times_equilibrados(jogadores, num_times)

        st.markdown("## 📊 Resultado do Sorteio")
        cols_resultado = st.columns(num_times)

        for idx, time in enumerate(times_sorteados):
            qtd = len(time["jogadores"])
            media = time["soma_nivel"] / qtd if qtd > 0 else 0

            with cols_resultado[idx]:
                st.subheader(f"Time {idx + 1}")
                st.caption(f"Média do Time: **{media:.1f}★** ({qtd} jogadores)")
                st.markdown("---")

                for j in time["jogadores"]:
                    # Pega apenas a parte inteira para desenhar as estrelas
                    qtd_estrelas = int(j["nivel"])
                    estrelas = "★" * qtd_estrelas
                    st.markdown(
                        f"""<div class="player-badge">
                            <b>{j['nome']}</b> <span class="pos-badge">{j['posicao']}</span> 
                            <span class="stars">{estrelas}</span>
                        </div>""",
                        unsafe_allow_html=True
                    )
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime

def conectar_banco():
    conn = sqlite3.connect("sisfin.db", check_same_thread=False)
    return conn

conn = conectar_banco()
cursor = conn.cursor()

def criar_tabelas():

    # ==========================
    # USUÁRIOS
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        usuario TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        nivel TEXT NOT NULL,
        ativo INTEGER DEFAULT 1
    )
    """)

    # ==========================
    # RECEITAS
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receitas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT NOT NULL,
        descricao TEXT NOT NULL,
        categoria TEXT NOT NULL,
        conta TEXT,
        forma_recebimento TEXT,
        valor REAL NOT NULL,
        observacao TEXT,
        usuario TEXT
    )
    """)

    # ==========================
    # DESPESAS
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS despesas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT NOT NULL,
        descricao TEXT NOT NULL,
        categoria TEXT NOT NULL,
        conta TEXT,
        forma_pagamento TEXT,
        valor REAL NOT NULL,
        observacao TEXT,
        usuario TEXT
    )
    """)

    # ==========================
    # METAS
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS metas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT NOT NULL,
        categoria TEXT,
        prioridade TEXT,
        valor_meta REAL NOT NULL,
        valor_atual REAL DEFAULT 0,
        aporte_mensal REAL DEFAULT 0,
        data_criacao TEXT
    )
    """)

    # ==========================
    # COMPRAS PLANEJADAS
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS compras_planejadas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto TEXT NOT NULL,
        valor_compra REAL NOT NULL,
        tipo_pagamento TEXT,
        parcelas INTEGER,
        valor_parcela REAL,
        juros REAL,
        prioridade TEXT,
        observacao TEXT,
        data_cadastro TEXT
    )
    """)

    # ==========================
    # FECHAMENTO MENSAL
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fechamento_mensal(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        competencia TEXT UNIQUE,
        receitas REAL DEFAULT 0,
        despesas REAL DEFAULT 0,
        saldo REAL DEFAULT 0,
        economia REAL DEFAULT 0,
        data_fechamento TEXT
    )
    """)

    # ==========================
    # CONTAS
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        saldo REAL DEFAULT 0
    )
    """)

    # ==========================
    # INVESTIMENTOS
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS investimentos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT,
        descricao TEXT,
        tipo TEXT,
        valor_aplicado REAL,
        rentabilidade REAL,
        observacao TEXT
    )
    """)

    # ==========================
    # CONFIGURAÇÕES
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS configuracoes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chave TEXT,
        valor TEXT
    )
    """)

    conn.commit()

    cursor.execute("""
    SELECT COUNT(*)
    FROM usuarios
    """)

    if cursor.fetchone()[0] == 0:

        cursor.execute("""
        INSERT INTO usuarios
        (
            nome,
            usuario,
            senha,
            nivel
        )
        VALUES
        (
            'Administrador',
            'admin',
            '123',
            'admin'
        )
        """)

    conn.commit()
def receitas():

    st.title("💰 Gestão de Receitas")

    # ==========================
    # OPERAÇÕES
    # ==========================

    st.subheader("⚙️ Operações")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        incluir = st.button(
            "➕ Incluir",
            use_container_width=True
        )

    with col2:
        localizar = st.button(
            "🔍 Localizar",
            use_container_width=True
        )

    with col3:
        alterar = st.button(
            "✏️ Alterar",
            use_container_width=True
        )

    with col4:
        excluir = st.button(
            "🗑️ Excluir",
            use_container_width=True
        )

    # ==========================
    # CONTROLE DE TELA
    # ==========================

    if incluir:
        st.session_state["acao_receita"] = "incluir"

    if localizar:
        st.session_state["acao_receita"] = "localizar"

    if alterar:
        st.session_state["acao_receita"] = "alterar"

    if excluir:
        st.session_state["acao_receita"] = "excluir"

    acao = st.session_state.get(
        "acao_receita",
        "incluir"
    )

    st.divider()

    # ==========================
    # INCLUIR
    # ==========================

    if acao == "incluir":

        st.subheader("➕ Nova Receita")

        with st.form("form_incluir_receita"):

            col1, col2 = st.columns(2)

            with col1:

                data = st.date_input(
                    "Data"
                )

                descricao = st.text_input(
                    "Descrição"
                )

                categoria = st.selectbox(
                    "Categoria",
                    [
                        "Salário",
                        "13º Salário",
                        "Férias",
                        "Freelance",
                        "Comissão",
                        "Investimento",
                        "Aluguel",
                        "Venda",
                        "Outros"
                    ]
                )

            with col2:

                conta = st.selectbox(
                    "Conta",
                    [
                        "Conta Corrente",
                        "Poupança",
                        "Carteira",
                        "Investimentos"
                    ]
                )

                forma_recebimento = st.selectbox(
                    "Forma de Recebimento",
                    [
                        "PIX",
                        "Transferência",
                        "Dinheiro",
                        "Cartão",
                        "Depósito"
                    ]
                )

                valor = st.number_input(
                    "Valor",
                    min_value=0.0,
                    format="%.2f"
                )

            observacao = st.text_area(
                "Observação"
            )

            salvar = st.form_submit_button(
                "💾 Salvar Receita"
            )

        if salvar:

            cursor.execute("""
                INSERT INTO receitas
                (
                    data,
                    descricao,
                    categoria,
                    conta,
                    forma_recebimento,
                    valor,
                    observacao,
                    usuario
                )
                VALUES
                (?,?,?,?,?,?,?,?)
            """,
            (
                str(data),
                descricao,
                categoria,
                conta,
                forma_recebimento,
                valor,
                observacao,
                st.session_state.get(
                    "usuario",
                    "Sistema"
                )
            ))

            conn.commit()

            st.success(
                "Receita cadastrada com sucesso!"
            )

            st.rerun()

elif acao == "localizar":

    st.subheader("🔍 Localizar Receita")

    filtro = st.text_input(
        "Pesquisar por descrição"
    )

    if filtro:

        df = pd.read_sql(
            """
            SELECT *
            FROM receitas
            WHERE descricao LIKE ?
            ORDER BY data DESC
            """,
            conn,
            params=(f"%{filtro}%",)
        )

    else:

        df = pd.read_sql(
            """
            SELECT *
            FROM receitas
            ORDER BY data DESC
            """,
            conn
        )

    if not df.empty:

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        receita_id = st.selectbox(
            "Selecione a Receita",
            df["id"]
        )

        dados = df[
            df["id"] == receita_id
        ].iloc[0]

        st.divider()

        st.subheader("📄 Dados da Receita")

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                f"**Data:** {dados['data']}"
            )

            st.write(
                f"**Descrição:** {dados['descricao']}"
            )

            st.write(
                f"**Categoria:** {dados['categoria']}"
            )

        with col2:

            st.write(
                f"**Conta:** {dados['conta']}"
            )

            st.write(
                f"**Forma Recebimento:** {dados['forma_recebimento']}"
            )

            st.write(
                f"**Valor:** R$ {dados['valor']:,.2f}"
            )

        st.write(
            f"**Observação:** {dados['observacao']}"
        )

        # Guarda para alteração ou exclusão
        st.session_state["receita_id"] = int(
            dados["id"]
        )

    else:

        st.warning(
            "Nenhuma receita encontrada."
        )
    # ALTERAR
    # ==========================

    elif acao == "alterar":

        st.subheader("✏️ Alterar Receita")

        st.info(
            "Tela de alteração será criada após a localização."
        )

    # ==========================
    # EXCLUIR
    # ==========================

    elif acao == "excluir":

        st.subheader("🗑️ Excluir Receita")

        st.info(
            "Tela de exclusão será criada no próximo passo."
        )
def login_usuario():

    st.title("🔐 Login do Sistema")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):

        cursor.execute("""
            SELECT usuario, senha, nivel
            FROM usuarios
            WHERE usuario = ? AND senha = ?
        """, (usuario, senha))

        result = cursor.fetchone()

        if result:

            st.session_state["logado"] = True
            st.session_state["usuario"] = result[0]
            st.session_state["nivel"] = result[2]

            st.success(
                f"Bem-vindo {result[0]} ({result[2]})"
            )

            st.rerun()

        else:

            st.error(
                "Usuário ou senha inválidos"
            )
# ==========================
# MENU PRINCIPAL
# ==========================        
def main():

    criar_tabelas()

    st.title("💰 SISFIN IA")

    menu = st.sidebar.radio(
        "Menu",
        [
            "Dashboard",
            "Receitas",
            "Despesas",
            "Metas",
            "Assistente",
            "Planejamento",
            "Relatórios"
        ]
    )

    if menu == "Dashboard":
        dashboard()

    elif menu == "Receitas":
        receitas()

    elif menu == "Despesas":
        despesas()

    elif menu == "Metas":
        metas()

    elif menu == "Assistente":
        assistente()
        
    elif menu == "Planejamento":
        planejamento_compras()
        
    elif menu == "Relatórios":
        relatorios()
    
# ==========================
# EXECUÇÃO
# ==========================

if __name__ == "__main__":

    criar_tabelas()

    if "logado" not in st.session_state:
        st.session_state["logado"] = False

    if "usuario" not in st.session_state:
        st.session_state["usuario"] = None

    if "nivel" not in st.session_state:
        st.session_state["nivel"] = None
    # ==========================
    # BLOQUEIO DE ACESSO
    # ==========================

    if not st.session_state["logado"]:
        login_usuario()
        st.stop()

    # ==========================
    # SIDEBAR (APÓS LOGIN)
    # ==========================

    st.sidebar.write(f"👤 {st.session_state.get('usuario')}")
    st.sidebar.write(f"🔐 Nível: {st.session_state.get('nivel')}")

    if st.sidebar.button("🚪 Sair"):

        st.session_state["logado"] = False
        st.session_state["usuario"] = None
        st.session_state["nivel"] = None

        st.rerun()

    # ==========================
    # CONTROLE DE PERMISSÕES
    # ==========================

    def checar_admin():
        if st.session_state.get("nivel") != "admin":
            st.warning("Acesso restrito (apenas admin)")
            st.stop()

    def checar_operador_admin():
        if st.session_state.get("nivel") not in ["admin", "operador"]:
            st.warning("Sem permissão")
            st.stop()

    # ==========================
    # EXECUÇÃO DO SISTEMA
    # ==========================

    main()

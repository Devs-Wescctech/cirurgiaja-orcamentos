from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

TABELA = os.getenv("ORCAMENTOS_TABELA", "public.orcamentos_cirurgiaja")

def conectar():
    host = os.getenv("POSTGRES_HOST")
    db = os.getenv("POSTGRES_DB")
    user = os.getenv("POSTGRES_USER")
    pwd = os.getenv("POSTGRES_PASSWORD")
    port = int(os.getenv("POSTGRES_PORT", "5432"))

    missing = [k for k, v in {
        "POSTGRES_HOST": host,
        "POSTGRES_DB": db,
        "POSTGRES_USER": user,
        "POSTGRES_PASSWORD": pwd
    }.items() if not v]

    if missing:
        raise Exception(f"Faltam variáveis de ambiente: {', '.join(missing)}")

    return psycopg2.connect(
        host=host,
        database=db,
        user=user,
        password=pwd,
        port=port
    )

def normalizar_nome(v):
    if v is None:
        return None
    v2 = v.strip()
    return v2 if v2 else None

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "API rodando", "service": "orcamentos-cirurgiaja"})

@app.route("/orcamento", methods=["GET"])
def buscar_orcamento_por_nome():
    """
    Buscar imagem do orçamento pelo nome do procedimento:
      /orcamento?nome=Hemorroida

    Por padrão faz busca case-insensitive:
      lower(nome) = lower(%s)

    Se quiser buscar exato (case-sensitive):
      /orcamento?nome=Hemorroida&exato=1
    """
    nome = normalizar_nome(request.args.get("nome"))
    exato = request.args.get("exato") in ("1", "true", "True", "sim", "SIM")

    if not nome:
        return jsonify({"erro": "Parâmetro 'nome' é obrigatório na query string"}), 400

    try:
        conn = conectar()
        cur = conn.cursor()

        if exato:
            sql = f"""
                SELECT nome, imagem_url
                FROM {TABELA}
                WHERE nome = %s
                LIMIT 1
            """
            cur.execute(sql, (nome,))
        else:
            sql = f"""
                SELECT nome, imagem_url
                FROM {TABELA}
                WHERE lower(nome) = lower(%s)
                LIMIT 1
            """
            cur.execute(sql, (nome,))

        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            return jsonify({"erro": "Procedimento não encontrado", "nome_consultado": nome}), 404

        return jsonify({"nome": row[0], "imagem_url": row[1]})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/orcamento/existe", methods=["GET"])
def existe_orcamento():
    """
    Verifica se existe:
      /orcamento/existe?nome=...
    """
    nome = normalizar_nome(request.args.get("nome"))
    if not nome:
        return jsonify({"erro": "Parâmetro 'nome' é obrigatório na query string"}), 400

    try:
        conn = conectar()
        cur = conn.cursor()

        sql = f"""
            SELECT 1
            FROM {TABELA}
            WHERE lower(nome) = lower(%s)
            LIMIT 1
        """
        cur.execute(sql, (nome,))
        row = cur.fetchone()

        cur.close()
        conn.close()

        return jsonify({"nome": nome, "exists": bool(row)})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/orcamentos", methods=["GET"])
def listar_orcamentos():
    """
    Lista todos (útil pra teste/admin):
      /orcamentos
    """
    try:
        conn = conectar()
        cur = conn.cursor()

        sql = f"""
            SELECT nome, imagem_url
            FROM {TABELA}
            ORDER BY nome
        """
        cur.execute(sql)
        rows = cur.fetchall()

        cur.close()
        conn.close()

        resultados = [{"nome": r[0], "imagem_url": r[1]} for r in rows]
        return jsonify({"total": len(resultados), "resultados": resultados})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=int(os.getenv("PORT", "5000")))

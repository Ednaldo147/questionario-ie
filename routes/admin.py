from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from src.models.questionario import QuestionarioResposta
from datetime import datetime

admin_bp = Blueprint('admin', __name__, template_folder='../templates')

# Senha fixa por enquanto
ADMIN_PASSWORD = 'admin123'

@admin_bp.route('/admin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        senha = request.form.get('senha')
        if senha == ADMIN_PASSWORD:
            session['logado'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            return render_template('admin_login.html', erro="Senha incorreta")
    return render_template('admin_login.html')

@admin_bp.route('/admin/dashboard')
def dashboard():
    if not session.get('logado'):
        return redirect(url_for('admin.login'))
    return render_template('admin_dashboard.html')

@admin_bp.route('/admin/logout')
def logout():
    session.clear()
    return redirect(url_for('admin.login'))

@admin_bp.route('/api/resultados')
def api_resultados():
    if not session.get('logado'):
        return jsonify({"erro": "Não autorizado"}), 403

    resultados = QuestionarioResposta.query.order_by(QuestionarioResposta.data_criacao.desc()).all()
    lista = []
    for r in resultados:
        lista.append({
            "id": r.id,
            "nome": r.nome,
            "email": r.email,
            "data": r.data_criacao.strftime("%d/%m/%Y %H:%M"),
            "neurociencia": r.pontuacao_neurociencia,
            "psicologia": r.pontuacao_psicologia,
            "metafisica": r.pontuacao_metafisica,
            "total": r.pontuacao_total,
            "nivel": r.nivel_ie,
        })
    return jsonify(lista)

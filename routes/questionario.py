import os
import pdfkit
import smtplib
from io import BytesIO
from flask import Blueprint, request, jsonify, render_template, send_file
from flask_cors import cross_origin
from email.message import EmailMessage
from src.models.questionario import QuestionarioResposta, db
import traceback

questionario_bp = Blueprint('questionario', __name__)

# Perguntas
PERGUNTAS = [
    {"id": 1, "categoria": "neurociencia", "pergunta": "Eu consigo identificar as sensações físicas no meu corpo quando sinto uma emoção forte (ex: coração acelerado, tensão muscular)?"},
    {"id": 2, "categoria": "neurociencia", "pergunta": "Eu consigo controlar meus impulsos e reações imediatas quando estou sob estresse?"},
    {"id": 3, "categoria": "neurociencia", "pergunta": "Eu percebo como o estresse afeta minha saúde física e mental?"},
    {"id": 4, "categoria": "neurociencia", "pergunta": "Eu consigo reconhecer os sinais de alerta do meu corpo antes que uma emoção se torne avassaladora?"},
    {"id": 5, "categoria": "neurociencia", "pergunta": "Eu consigo gerenciar minha energia para evitar a fadiga emocional?"},
    {"id": 6, "categoria": "psicologia", "pergunta": "Eu consigo identificar e nomear com precisão as emoções que estou sentindo na maioria das situações?"},
    {"id": 7, "categoria": "psicologia", "pergunta": "Eu consigo gerenciar minhas emoções de forma eficaz, evitando explosões ou retraimentos excessivos?"},
    {"id": 8, "categoria": "psicologia", "pergunta": "Eu me sinto motivado(a) e persistente na busca dos meus objetivos, mesmo diante de obstáculos?"},
    {"id": 9, "categoria": "psicologia", "pergunta": "Eu consigo me colocar no lugar dos outros e compreender seus sentimentos e perspectivas?"},
    {"id": 10, "categoria": "psicologia", "pergunta": "Eu consigo construir e manter relacionamentos saudáveis e harmoniosos com as pessoas ao meu redor?"},
    {"id": 11, "categoria": "metafisica", "pergunta": "Eu percebo uma conexão entre minhas emoções e a energia que sinto ao meu redor?"},
    {"id": 12, "categoria": "metafisica", "pergunta": "Eu consigo transformar emoções negativas (como raiva ou medo) em algo mais positivo ou construtivo?"},
    {"id": 13, "categoria": "metafisica", "pergunta": "Eu acredito que minhas experiências emocionais têm um propósito maior para o meu crescimento?"},
    {"id": 14, "categoria": "metafisica", "pergunta": "Eu consigo alinhar minhas emoções com minhas intenções e objetivos mais elevados?"},
    {"id": 15, "categoria": "metafisica", "pergunta": "Eu sinto uma profunda conexão com algo maior que eu (universo, natureza, espiritualidade) que influencia minhas emoções?"}
]

OPCOES_RESPOSTA = [
    {"valor": 1, "texto": "Discordo totalmente / Nunca"},
    {"valor": 2, "texto": "Discordo / Raramente"},
    {"valor": 3, "texto": "Neutro / Às vezes"},
    {"valor": 4, "texto": "Concordo / Frequentemente"},
    {"valor": 5, "texto": "Concordo totalmente / Sempre"}
]

# ------------------------------------------------------------------------------

def calcular_nivel_ie(pontuacao_total):
    if pontuacao_total <= 30:
        return "Básico"
    elif pontuacao_total <= 45:
        return "Intermediário"
    elif pontuacao_total <= 60:
        return "Avançado"
    else:
        return "Expert"

def gerar_relatorio(total, neuro, psicologia, metafisica, nivel):
    return {
        "pontuacao_total": total,
        "pontuacao_maxima": 75,
        "percentual": round((total / 75) * 100, 1),
        "nivel": nivel,
        "descricao": {
            "Básico": "Você está no início da sua jornada emocional. Há muito espaço para crescer.",
            "Intermediário": "Você tem uma boa noção emocional, mas ainda pode se desenvolver bastante.",
            "Avançado": "Você tem uma inteligência emocional sólida e bem desenvolvida.",
            "Expert": "Parabéns! Você demonstra um nível elevado de consciência emocional."
        }.get(nivel, ""),
        "categorias": {
            "neurociencia": {"pontuacao": neuro, "percentual": round(neuro / 25 * 100, 1)},
            "psicologia": {"pontuacao": psicologia, "percentual": round(psicologia / 25 * 100, 1)},
            "metafisica": {"pontuacao": metafisica, "percentual": round(metafisica / 25 * 100, 1)},
        },
        "area_mais_forte": max({"Neurociência": neuro, "Psicologia": psicologia, "Metafísica": metafisica}, key=lambda k: {"Neurociência": neuro, "Psicologia": psicologia, "Metafísica": metafisica}[k]),
        "area_mais_fraca": min({"Neurociência": neuro, "Psicologia": psicologia, "Metafísica": metafisica}, key=lambda k: {"Neurociência": neuro, "Psicologia": psicologia, "Metafísica": metafisica}[k]),
        "sugestoes": [
            *(["Pratique mindfulness para consciência corporal."] if neuro < 15 else []),
            *(["Use um diário emocional para desenvolver autocontrole."] if psicologia < 15 else []),
            *(["Explore meditação para entender melhor seu propósito emocional."] if metafisica < 15 else []),
        ] or ["Continue praticando para manter seu equilíbrio emocional."]
    }

def gerar_pdf_html(relatorio, nome, email, data, grafico_base64=''):
    html = render_template("relatorio_template.html",
        nome=nome,
        email=email,
        data=data.strftime("%d/%m/%Y %H:%M"),
        nivel=relatorio["nivel"],
        percentual=relatorio["percentual"],
        descricao=relatorio["descricao"],
        neurociencia=relatorio["categorias"]["neurociencia"]["pontuacao"],
        neurociencia_pct=relatorio["categorias"]["neurociencia"]["percentual"],
        psicologia=relatorio["categorias"]["psicologia"]["pontuacao"],
        psicologia_pct=relatorio["categorias"]["psicologia"]["percentual"],
        metafisica=relatorio["categorias"]["metafisica"]["pontuacao"],
        metafisica_pct=relatorio["categorias"]["metafisica"]["percentual"],
        area_mais_forte=relatorio["area_mais_forte"],
        area_mais_fraca=relatorio["area_mais_fraca"],
        sugestoes=relatorio["sugestoes"],
        grafico_base64=grafico_base64
    )

    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    return pdfkit.from_string(html, False, configuration=config)

def enviar_email(destinatario, nome, relatorio_pdf):
    msg = EmailMessage()
    msg['Subject'] = 'Seu Relatório de Inteligência Emocional'
    msg['From'] = 'Segredodenegocio@gmail.com'
    msg['To'] = destinatario
    msg.set_content(f"Olá {nome},\n\nSegue em anexo seu relatório de IE.\n\nAtenciosamente,\nEquipe IE")
    msg.add_attachment(relatorio_pdf, maintype='application', subtype='pdf', filename="relatorio_ie.pdf")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('Segredodenegocio@gmail.com', 'fqtv xdje cwxz ljtk')
        smtp.send_message(msg)

# ------------------------------------------------------------------------------

@questionario_bp.route('/perguntas', methods=['GET'])
@cross_origin()
def obter_perguntas():
    return jsonify({"perguntas": PERGUNTAS, "opcoes_resposta": OPCOES_RESPOSTA})

@questionario_bp.route('/submeter', methods=['POST'])
@cross_origin()
def submeter_questionario():
    try:
        dados = request.get_json()
        grafico_base64 = dados.get('grafico_base64', '')
        nome = dados.get('nome')
        email = dados.get('email', '')
        respostas = dados.get('respostas', [])

        if not nome or len(respostas) != 15:
            return jsonify({"erro": "Dados incompletos"}), 400

        neuro = sum(respostas[0:5])
        psicologia = sum(respostas[5:10])
        metafisica = sum(respostas[10:15])
        total = neuro + psicologia + metafisica
        nivel = calcular_nivel_ie(total)

        nova = QuestionarioResposta(
            nome=nome, email=email,
            pergunta_1=respostas[0], pergunta_2=respostas[1], pergunta_3=respostas[2],
            pergunta_4=respostas[3], pergunta_5=respostas[4], pergunta_6=respostas[5],
            pergunta_7=respostas[6], pergunta_8=respostas[7], pergunta_9=respostas[8],
            pergunta_10=respostas[9], pergunta_11=respostas[10], pergunta_12=respostas[11],
            pergunta_13=respostas[12], pergunta_14=respostas[13], pergunta_15=respostas[14],
            pontuacao_total=total, pontuacao_neurociencia=neuro,
            pontuacao_psicologia=psicologia, pontuacao_metafisica=metafisica, nivel_ie=nivel
        )

        db.session.add(nova)
        db.session.commit()

        relatorio = gerar_relatorio(total, neuro, psicologia, metafisica, nivel)

        if email:
            pdf_data = gerar_pdf_html(relatorio, nome, email, nova.data_criacao, grafico_base64)
            enviar_email(email, nome, pdf_data)

        return jsonify({"sucesso": True, "relatorio": relatorio})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500

@questionario_bp.route('/api/resultados/<int:resultado_id>', methods=['GET'])
@cross_origin()
def obter_pdf_resultado(resultado_id):
    try:
        resultado = QuestionarioResposta.query.get_or_404(resultado_id)
        relatorio = gerar_relatorio(
            resultado.pontuacao_total,
            resultado.pontuacao_neurociencia,
            resultado.pontuacao_psicologia,
            resultado.pontuacao_metafisica,
            resultado.nivel_ie
        )

        pdf_data = gerar_pdf_html(
            relatorio,
            resultado.nome,
            resultado.email,
            resultado.data_criacao,
            grafico_base64=''  # no histórico, sem gráfico
        )

        return send_file(BytesIO(pdf_data), mimetype='application/pdf', download_name=f'relatorio_{resultado.nome}.pdf', as_attachment=False)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

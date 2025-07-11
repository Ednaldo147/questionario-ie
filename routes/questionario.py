from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.models.questionario import QuestionarioResposta, db

questionario_bp = Blueprint('questionario', __name__)

# Perguntas do questionário
PERGUNTAS = [
    # Neurociência (1-5)
    {
        "id": 1,
        "categoria": "neurociencia",
        "pergunta": "Eu consigo identificar as sensações físicas no meu corpo quando sinto uma emoção forte (ex: coração acelerado, tensão muscular)?"
    },
    {
        "id": 2,
        "categoria": "neurociencia",
        "pergunta": "Eu consigo controlar meus impulsos e reações imediatas quando estou sob estresse?"
    },
    {
        "id": 3,
        "categoria": "neurociencia",
        "pergunta": "Eu percebo como o estresse afeta minha saúde física e mental?"
    },
    {
        "id": 4,
        "categoria": "neurociencia",
        "pergunta": "Eu consigo reconhecer os sinais de alerta do meu corpo antes que uma emoção se torne avassaladora?"
    },
    {
        "id": 5,
        "categoria": "neurociencia",
        "pergunta": "Eu consigo gerenciar minha energia para evitar a fadiga emocional?"
    },
    # Psicologia (6-10)
    {
        "id": 6,
        "categoria": "psicologia",
        "pergunta": "Eu consigo identificar e nomear com precisão as emoções que estou sentindo na maioria das situações?"
    },
    {
        "id": 7,
        "categoria": "psicologia",
        "pergunta": "Eu consigo gerenciar minhas emoções de forma eficaz, evitando explosões ou retraimentos excessivos?"
    },
    {
        "id": 8,
        "categoria": "psicologia",
        "pergunta": "Eu me sinto motivado(a) e persistente na busca dos meus objetivos, mesmo diante de obstáculos?"
    },
    {
        "id": 9,
        "categoria": "psicologia",
        "pergunta": "Eu consigo me colocar no lugar dos outros e compreender seus sentimentos e perspectivas?"
    },
    {
        "id": 10,
        "categoria": "psicologia",
        "pergunta": "Eu consigo construir e manter relacionamentos saudáveis e harmoniosos com as pessoas ao meu redor?"
    },
    # Metafísica (11-15)
    {
        "id": 11,
        "categoria": "metafisica",
        "pergunta": "Eu percebo uma conexão entre minhas emoções e a energia que sinto ao meu redor?"
    },
    {
        "id": 12,
        "categoria": "metafisica",
        "pergunta": "Eu consigo transformar emoções negativas (como raiva ou medo) em algo mais positivo ou construtivo?"
    },
    {
        "id": 13,
        "categoria": "metafisica",
        "pergunta": "Eu acredito que minhas experiências emocionais têm um propósito maior para o meu crescimento?"
    },
    {
        "id": 14,
        "categoria": "metafisica",
        "pergunta": "Eu consigo alinhar minhas emoções com minhas intenções e objetivos mais elevados?"
    },
    {
        "id": 15,
        "categoria": "metafisica",
        "pergunta": "Eu sinto uma profunda conexão com algo maior que eu (universo, natureza, espiritualidade) que influencia minhas emoções?"
    }
]

OPCOES_RESPOSTA = [
    {"valor": 1, "texto": "Discordo totalmente / Nunca"},
    {"valor": 2, "texto": "Discordo / Raramente"},
    {"valor": 3, "texto": "Neutro / Às vezes"},
    {"valor": 4, "texto": "Concordo / Frequentemente"},
    {"valor": 5, "texto": "Concordo totalmente / Sempre"}
]

def calcular_nivel_ie(pontuacao_total):
    """Calcula o nível de IE baseado na pontuação total"""
    if pontuacao_total <= 30:
        return "Básico"
    elif pontuacao_total <= 45:
        return "Intermediário"
    elif pontuacao_total <= 60:
        return "Avançado"
    else:
        return "Expert"

def gerar_relatorio(pontuacao_total, pontuacao_neurociencia, pontuacao_psicologia, pontuacao_metafisica, nivel_ie):
    """Gera relatório personalizado baseado nas pontuações"""
    
    relatorio = {
        "pontuacao_total": pontuacao_total,
        "pontuacao_maxima": 75,
        "percentual": round((pontuacao_total / 75) * 100, 1),
        "nivel": nivel_ie,
        "categorias": {
            "neurociencia": {
                "pontuacao": pontuacao_neurociencia,
                "percentual": round((pontuacao_neurociencia / 25) * 100, 1)
            },
            "psicologia": {
                "pontuacao": pontuacao_psicologia,
                "percentual": round((pontuacao_psicologia / 25) * 100, 1)
            },
            "metafisica": {
                "pontuacao": pontuacao_metafisica,
                "percentual": round((pontuacao_metafisica / 25) * 100, 1)
            }
        }
    }
    
    # Descrição do nível
    descricoes = {
        "Básico": "Você está no início da sua jornada de desenvolvimento da inteligência emocional. Há muito espaço para crescimento e aprendizado.",
        "Intermediário": "Você possui alguma consciência e controle emocional, mas ainda há áreas importantes para desenvolver.",
        "Avançado": "Você demonstra boa inteligência emocional, com capacidade sólida de gerenciar emoções e se relacionar bem com outros.",
        "Expert": "Você possui alta inteligência emocional, com profundo autoconhecimento e habilidade de influenciar positivamente a si e aos outros."
    }
    
    relatorio["descricao"] = descricoes.get(nivel_ie, "")
    
    # Identificar área mais forte e mais fraca
    categorias_pontuacao = {
        "Neurociência": pontuacao_neurociencia,
        "Psicologia": pontuacao_psicologia,
        "Metafísica": pontuacao_metafisica
    }
    
    area_mais_forte = max(categorias_pontuacao, key=categorias_pontuacao.get)
    area_mais_fraca = min(categorias_pontuacao, key=categorias_pontuacao.get)
    
    relatorio["area_mais_forte"] = area_mais_forte
    relatorio["area_mais_fraca"] = area_mais_fraca
    
    # Sugestões personalizadas
    sugestoes = []
    
    if pontuacao_neurociencia < 15:
        sugestoes.append("Pratique exercícios de respiração e mindfulness para desenvolver maior consciência corporal.")
    
    if pontuacao_psicologia < 15:
        sugestoes.append("Inicie um diário emocional para melhorar seu autoconhecimento e controle emocional.")
    
    if pontuacao_metafisica < 15:
        sugestoes.append("Explore práticas de meditação e reflexão sobre o propósito das suas experiências emocionais.")
    
    if not sugestoes:
        sugestoes.append("Continue praticando as técnicas aprendidas para manter e aprimorar sua inteligência emocional.")
    
    relatorio["sugestoes"] = sugestoes
    
    return relatorio

@questionario_bp.route('/perguntas', methods=['GET'])
@cross_origin()
def obter_perguntas():
    """Retorna todas as perguntas do questionário"""
    return jsonify({
        "perguntas": PERGUNTAS,
        "opcoes_resposta": OPCOES_RESPOSTA
    })

@questionario_bp.route('/submeter', methods=['POST'])
@cross_origin()
def submeter_questionario():
    """Processa as respostas do questionário e retorna o relatório"""
    try:
        dados = request.get_json()
        
        # Validar dados obrigatórios
        if not dados.get('nome'):
            return jsonify({"erro": "Nome é obrigatório"}), 400
        
        # Validar respostas (devem ser 15 respostas com valores de 1 a 5)
        respostas = dados.get('respostas', [])
        if len(respostas) != 15:
            return jsonify({"erro": "Devem ser fornecidas exatamente 15 respostas"}), 400
        
        for resposta in respostas:
            if not isinstance(resposta, int) or resposta < 1 or resposta > 5:
                return jsonify({"erro": "Cada resposta deve ser um número entre 1 e 5"}), 400
        
        # Calcular pontuações
        pontuacao_neurociencia = sum(respostas[0:5])  # Perguntas 1-5
        pontuacao_psicologia = sum(respostas[5:10])   # Perguntas 6-10
        pontuacao_metafisica = sum(respostas[10:15])  # Perguntas 11-15
        pontuacao_total = pontuacao_neurociencia + pontuacao_psicologia + pontuacao_metafisica
        
        nivel_ie = calcular_nivel_ie(pontuacao_total)
        
        # Salvar no banco de dados
        nova_resposta = QuestionarioResposta(
            nome=dados['nome'],
            email=dados.get('email', ''),
            pergunta_1=respostas[0],
            pergunta_2=respostas[1],
            pergunta_3=respostas[2],
            pergunta_4=respostas[3],
            pergunta_5=respostas[4],
            pergunta_6=respostas[5],
            pergunta_7=respostas[6],
            pergunta_8=respostas[7],
            pergunta_9=respostas[8],
            pergunta_10=respostas[9],
            pergunta_11=respostas[10],
            pergunta_12=respostas[11],
            pergunta_13=respostas[12],
            pergunta_14=respostas[13],
            pergunta_15=respostas[14],
            pontuacao_total=pontuacao_total,
            pontuacao_neurociencia=pontuacao_neurociencia,
            pontuacao_psicologia=pontuacao_psicologia,
            pontuacao_metafisica=pontuacao_metafisica,
            nivel_ie=nivel_ie
        )
        
        db.session.add(nova_resposta)
        db.session.commit()
        
        # Gerar relatório
        relatorio = gerar_relatorio(
            pontuacao_total, 
            pontuacao_neurociencia, 
            pontuacao_psicologia, 
            pontuacao_metafisica, 
            nivel_ie
        )
        
        return jsonify({
            "sucesso": True,
            "id": nova_resposta.id,
            "relatorio": relatorio
        })
        
    except Exception as e:
        return jsonify({"erro": f"Erro interno do servidor: {str(e)}"}), 500

@questionario_bp.route('/resultados/<int:resultado_id>', methods=['GET'])
@cross_origin()
def obter_resultado(resultado_id):
    """Retorna um resultado específico pelo ID"""
    try:
        resultado = QuestionarioResposta.query.get_or_404(resultado_id)
        
        relatorio = gerar_relatorio(
            resultado.pontuacao_total,
            resultado.pontuacao_neurociencia,
            resultado.pontuacao_psicologia,
            resultado.pontuacao_metafisica,
            resultado.nivel_ie
        )
        
        return jsonify({
            "resultado": resultado.to_dict(),
            "relatorio": relatorio
        })
        
    except Exception as e:
        return jsonify({"erro": f"Erro interno do servidor: {str(e)}"}), 500


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class QuestionarioResposta(db.Model):
    __tablename__ = 'questionario_respostas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    
    # Respostas das perguntas (1-15)
    pergunta_1 = db.Column(db.Integer, nullable=False)
    pergunta_2 = db.Column(db.Integer, nullable=False)
    pergunta_3 = db.Column(db.Integer, nullable=False)
    pergunta_4 = db.Column(db.Integer, nullable=False)
    pergunta_5 = db.Column(db.Integer, nullable=False)
    pergunta_6 = db.Column(db.Integer, nullable=False)
    pergunta_7 = db.Column(db.Integer, nullable=False)
    pergunta_8 = db.Column(db.Integer, nullable=False)
    pergunta_9 = db.Column(db.Integer, nullable=False)
    pergunta_10 = db.Column(db.Integer, nullable=False)
    pergunta_11 = db.Column(db.Integer, nullable=False)
    pergunta_12 = db.Column(db.Integer, nullable=False)
    pergunta_13 = db.Column(db.Integer, nullable=False)
    pergunta_14 = db.Column(db.Integer, nullable=False)
    pergunta_15 = db.Column(db.Integer, nullable=False)
    
    # Pontuações calculadas
    pontuacao_total = db.Column(db.Integer, nullable=False)
    pontuacao_neurociencia = db.Column(db.Integer, nullable=False)
    pontuacao_psicologia = db.Column(db.Integer, nullable=False)
    pontuacao_metafisica = db.Column(db.Integer, nullable=False)
    nivel_ie = db.Column(db.String(50), nullable=False)
    
    # Timestamp
    data_criacao = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def __repr__(self):
        return f'<QuestionarioResposta {self.nome} - {self.pontuacao_total}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'pontuacao_total': self.pontuacao_total,
            'pontuacao_neurociencia': self.pontuacao_neurociencia,
            'pontuacao_psicologia': self.pontuacao_psicologia,
            'pontuacao_metafisica': self.pontuacao_metafisica,
            'nivel_ie': self.nivel_ie,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }


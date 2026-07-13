
-- REMOÇÃO DAS TABELAS
DROP TABLE IF EXISTS
    paciente_alergia,
    procedimento_realizado,
    escala,
    atendimento,
    residente,
    preceptor,
    profissional,
    paciente,
    alergia,
    procedimento,
    unidade,
    pessoa
CASCADE;


CREATE TABLE pessoa (
    id_pessoa SERIAL,
    nome VARCHAR(100) NOT NULL,
    cpf CHAR(11) NOT NULL,
    data_nascimento DATE NOT NULL,
    is_flamengo BOOLEAN NOT NULL DEFAULT FALSE,
    telefone VARCHAR(20) NOT NULL,
    endereco VARCHAR(200) NOT NULL,

    CONSTRAINT pk_pessoa
        PRIMARY KEY (id_pessoa),

    CONSTRAINT uq_pessoa_cpf
        UNIQUE (cpf),

    CONSTRAINT ck_pessoa_cpf
        CHECK (cpf ~ '^[0-9]{11}$'),

    CONSTRAINT ck_pessoa_nome
        CHECK (TRIM(nome) <> ''),

    CONSTRAINT ck_pessoa_data_nascimento
        CHECK (data_nascimento <= CURRENT_DATE)
);


CREATE TABLE paciente (
    id_pessoa INT NOT NULL,
    num_convenio VARCHAR(30) NOT NULL,
    grupo_sanguineo VARCHAR(3) NOT NULL,

    CONSTRAINT pk_paciente
        PRIMARY KEY (id_pessoa),

    CONSTRAINT fk_paciente_pessoa
        FOREIGN KEY (id_pessoa)
        REFERENCES pessoa(id_pessoa)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT uq_paciente_num_convenio
        UNIQUE (num_convenio),

    CONSTRAINT ck_paciente_grupo_sanguineo
        CHECK (
            grupo_sanguineo IN (
                'A+', 'A-', 'B+', 'B-',
                'AB+', 'AB-', 'O+', 'O-'
            )
        )
);


CREATE TABLE alergia (
    id_alergia SERIAL,
    nome VARCHAR(100) NOT NULL,

    CONSTRAINT pk_alergia
        PRIMARY KEY (id_alergia),

    CONSTRAINT uq_alergia_nome
        UNIQUE (nome),

    CONSTRAINT ck_alergia_nome
        CHECK (TRIM(nome) <> '')
);


CREATE TABLE paciente_alergia (
    id_paciente INT NOT NULL,
    id_alergia INT NOT NULL,

    CONSTRAINT pk_paciente_alergia
        PRIMARY KEY (id_paciente, id_alergia),

    CONSTRAINT fk_paciente_alergia_paciente
        FOREIGN KEY (id_paciente)
        REFERENCES paciente(id_pessoa)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_paciente_alergia_alergia
        FOREIGN KEY (id_alergia)
        REFERENCES alergia(id_alergia)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);


CREATE TABLE profissional (
    id_pessoa INT NOT NULL,
    crm VARCHAR(20) NOT NULL,
    data_admissao DATE NOT NULL,
    especialidade VARCHAR(100) NOT NULL,

    CONSTRAINT pk_profissional
        PRIMARY KEY (id_pessoa),

    CONSTRAINT fk_profissional_pessoa
        FOREIGN KEY (id_pessoa)
        REFERENCES pessoa(id_pessoa)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT uq_profissional_crm
        UNIQUE (crm),

    CONSTRAINT ck_profissional_data_admissao
        CHECK (data_admissao <= CURRENT_DATE),

    CONSTRAINT ck_profissional_especialidade
        CHECK (TRIM(especialidade) <> '')
);


CREATE TABLE residente (
    id_profissional INT NOT NULL,
    ano_residencia VARCHAR(2) NOT NULL,

    CONSTRAINT pk_residente
        PRIMARY KEY (id_profissional),

    CONSTRAINT fk_residente_profissional
        FOREIGN KEY (id_profissional)
        REFERENCES profissional(id_pessoa)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT ck_residente_ano
        CHECK (ano_residencia IN ('R1', 'R2', 'R3'))
);


CREATE TABLE preceptor (
    id_profissional INT NOT NULL,
    titulacao VARCHAR(30) NOT NULL,

    CONSTRAINT pk_preceptor
        PRIMARY KEY (id_profissional),

    CONSTRAINT fk_preceptor_profissional
        FOREIGN KEY (id_profissional)
        REFERENCES profissional(id_pessoa)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT ck_preceptor_titulacao
        CHECK (
            titulacao IN (
                'ESPECIALISTA',
                'MESTRE',
                'DOUTOR',
                'POS_DOUTOR'
            )
        )
);


CREATE TABLE unidade (
    id_unidade SERIAL,
    nome VARCHAR(100) NOT NULL,
    tipo VARCHAR(30) NOT NULL,
    capacidade_leitos INT NOT NULL,

    CONSTRAINT pk_unidade
        PRIMARY KEY (id_unidade),

    CONSTRAINT uq_unidade_nome
        UNIQUE (nome),

    CONSTRAINT ck_unidade_tipo
        CHECK (
            tipo IN (
                'ENFERMARIA',
                'UTI',
                'PRONTO_SOCORRO',
                'AMBULATORIO'
            )
        ),

    CONSTRAINT ck_unidade_capacidade
        CHECK (capacidade_leitos >= 0)
);


CREATE TABLE procedimento (
    id_procedimento SERIAL,
    codigo VARCHAR(20) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    tempo_medio_minutos INT NOT NULL,
    nivel_risco VARCHAR(10) NOT NULL,

    CONSTRAINT pk_procedimento
        PRIMARY KEY (id_procedimento),

    CONSTRAINT uq_procedimento_codigo
        UNIQUE (codigo),

    CONSTRAINT ck_procedimento_nome
        CHECK (TRIM(nome) <> ''),

    CONSTRAINT ck_procedimento_tempo
        CHECK (tempo_medio_minutos > 0),

    CONSTRAINT ck_procedimento_nivel_risco
        CHECK (
            nivel_risco IN ('BAIXO', 'MEDIO', 'ALTO')
        )
);


CREATE TABLE atendimento (
    id_atendimento SERIAL,
    data_hora TIMESTAMP NOT NULL,
    duracao_minutos INT NOT NULL,
    id_paciente INT NOT NULL,
    id_residente INT NOT NULL,
    id_preceptor INT NOT NULL,

    CONSTRAINT pk_atendimento
        PRIMARY KEY (id_atendimento),

    CONSTRAINT fk_atendimento_paciente
        FOREIGN KEY (id_paciente)
        REFERENCES paciente(id_pessoa)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_atendimento_residente
        FOREIGN KEY (id_residente)
        REFERENCES residente(id_profissional)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_atendimento_preceptor
        FOREIGN KEY (id_preceptor)
        REFERENCES preceptor(id_profissional)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT ck_atendimento_duracao
        CHECK (duracao_minutos > 0)
);


CREATE TABLE procedimento_realizado (
    id_atendimento INT NOT NULL,
    id_procedimento INT NOT NULL,
    quantidade INT NOT NULL,
    tempo_real_minutos INT NOT NULL,
    observacao TEXT,
    faturado BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT pk_procedimento_realizado
        PRIMARY KEY (id_atendimento, id_procedimento),

    CONSTRAINT fk_procedimento_realizado_atendimento
        FOREIGN KEY (id_atendimento)
        REFERENCES atendimento(id_atendimento)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_procedimento_realizado_procedimento
        FOREIGN KEY (id_procedimento)
        REFERENCES procedimento(id_procedimento)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT ck_procedimento_realizado_quantidade
        CHECK (quantidade > 0),

    CONSTRAINT ck_procedimento_realizado_tempo
        CHECK (tempo_real_minutos > 0)
);


CREATE TABLE escala (
    id_escala SERIAL,
    data_plantao DATE NOT NULL,
    turno VARCHAR(10) NOT NULL,
    id_unidade INT NOT NULL,
    id_residente INT NOT NULL,
    id_preceptor INT NOT NULL,

    CONSTRAINT pk_escala
        PRIMARY KEY (id_escala),

    CONSTRAINT fk_escala_unidade
        FOREIGN KEY (id_unidade)
        REFERENCES unidade(id_unidade)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_escala_residente
        FOREIGN KEY (id_residente)
        REFERENCES residente(id_profissional)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_escala_preceptor
        FOREIGN KEY (id_preceptor)
        REFERENCES preceptor(id_profissional)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT ck_escala_turno
        CHECK (
            turno IN ('MANHA', 'TARDE', 'NOITE')
        ),

    CONSTRAINT uq_escala_residente
        UNIQUE (
            id_unidade,
            data_plantao,
            turno,
            id_residente
        )
);
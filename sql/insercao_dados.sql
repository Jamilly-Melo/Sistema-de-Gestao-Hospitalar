INSERT INTO pessoa (
    nome,
    cpf,
    data_nascimento,
    is_flamengo,
    telefone,
    endereco
)
VALUES
    (
        'Ana Silva dos Santos',
        '11111111111',
        '1990-01-01',
        TRUE,
        '83940028922',
        'Rua Helena Freire, 100'
    ),
    (
        'Bruno Soares Ferraz',
        '22222222222',
        '1991-02-02',
        FALSE,
        '83988865421',
        'Avenida Pau Brasil, 220'
    ),
    (
        'Carla Oliveira Fernandes',
        '33333333333',
        '1992-03-03',
        TRUE,
        '83998758962',
        'Rua Haiti, 45'
    ),
    (
        'Diego Justino Soares',
        '44444444444',
        '1993-04-04',
        FALSE,
        '83965425445',
        'Rua das Acácias, 80'
    ),
    (
        'Eva Pontes Vieira Pires',
        '55555555555',
        '1994-05-05',
        TRUE,
        '81987789556',
        'Rua das Palmeiras, 90'
    ),
    (
        'Lucas Andrade Alves',
        '66666666666',
        '1995-01-01',
        TRUE,
        '83987905454',
        'Avenida Central, 60'
    ),
    (
        'Mariana Souza Menezes',
        '77777777777',
        '1995-02-02',
        FALSE,
        '83965547899',
        'Rua dos Ipês, 70'
    ),
    (
        'Maria Vitória Fernandes',
        '88888888888',
        '1995-03-03',
        TRUE,
        '81982233665',
        'Rua das Flores, 85'
    ),
    (
        'Aline Ferreira Costa',
        '99999999999',
        '1995-04-04',
        FALSE,
        '83956784599',
        'Rua das Oliveiras, 95'
    ),
    (
        'André Vieira Duarte e Silva',
        '10101010101',
        '1995-05-05',
        TRUE,
        '81986653244',
        'Avenida Esperança, 110'
    ),
    (
        'Ricardo Mendes Mariano',
        '12121212121',
        '1980-01-01',
        FALSE,
        '83920226543',
        'Rua das Mangueiras, 120'
    ),
    (
        'Juliana Martins Honorato',
        '13131313131',
        '1981-02-02',
        TRUE,
        '83954668795',
        'Avenida Principal, 130'
    ),
    (
        'Hevelin Kudiess Souza',
        '14141414141',
        '1982-03-03',
        FALSE,
        '83952226456',
        'Rua do Hospital, 140'
    ),
    (
        'Rafael Martan Pontes',
        '15151515151',
        '1983-04-04',
        TRUE,
        '83989755621',
        'Rua das Pedras, 150'
    ),
    (
        'Camila Evelin de Melo',
        '16161616161',
        '1984-05-05',
        FALSE,
        '81987506070',
        'Avenida dos Estados, 160'
    );


INSERT INTO paciente (
    id_pessoa,
    num_convenio,
    grupo_sanguineo
)
VALUES
    (1, 'C001', 'A+'),
    (2, 'C002', 'O+'),
    (3, 'C003', 'B+'),
    (4, 'C004', 'AB+'),
    (5, 'C005', 'O-');


INSERT INTO alergia (nome)
VALUES
    ('Penicilina'),
    ('Dipirona'),
    ('Amendoim'),
    ('Lactose'),
    ('Poeira');


INSERT INTO paciente_alergia (
    id_paciente,
    id_alergia
)
VALUES
    (1, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (5, 5);


INSERT INTO profissional (
    id_pessoa,
    crm,
    data_admissao,
    especialidade
)
VALUES
    (6, 'CRM001', '2024-01-01', 'Clínica Médica'),
    (7, 'CRM002', '2024-01-01', 'Pediatria'),
    (8, 'CRM003', '2024-01-01', 'Cirurgia Geral'),
    (9, 'CRM004', '2024-01-01', 'Ortopedia'),
    (10, 'CRM005', '2024-01-01', 'Cardiologia'),
    (11, 'CRM006', '2018-01-01', 'Clínica Médica'),
    (12, 'CRM007', '2017-01-01', 'Pediatria'),
    (13, 'CRM008', '2016-01-01', 'Cirurgia Geral'),
    (14, 'CRM009', '2015-01-01', 'Ortopedia'),
    (15, 'CRM010', '2014-01-01', 'Cardiologia');


INSERT INTO residente (
    id_profissional,
    ano_residencia
)
VALUES
    (6, 'R1'),
    (7, 'R1'),
    (8, 'R2'),
    (9, 'R2'),
    (10, 'R3');


INSERT INTO preceptor (
    id_profissional,
    titulacao
)
VALUES
    (11, 'MESTRE'),
    (12, 'DOUTOR'),
    (13, 'DOUTOR'),
    (14, 'MESTRE'),
    (15, 'ESPECIALISTA');


INSERT INTO unidade (
    nome,
    tipo,
    capacidade_leitos
)
VALUES
    ('Unidade de Terapia Intensiva', 'UTI', 20),
    ('Enfermaria Geral', 'ENFERMARIA', 40),
    ('Ambulatório Geral', 'AMBULATORIO', 0);


INSERT INTO procedimento (
    codigo,
    nome,
    tempo_medio_minutos,
    nivel_risco
)
VALUES
    ('PR01', 'Coleta de sangue', 10, 'BAIXO'),
    ('PR02', 'Sutura', 30, 'MEDIO'),
    ('PR03', 'Aplicação de medicação', 15, 'BAIXO'),
    ('PR04', 'Raio X', 20, 'BAIXO'),
    ('PR05', 'Cirurgia', 120, 'ALTO'),
    ('PR06', 'Curativo', 10, 'BAIXO'),
    ('PR07', 'Tomografia', 40, 'MEDIO'),
    ('PR08', 'Eletrocardiograma', 15, 'BAIXO'),
    ('PR09', 'Intubação', 25, 'ALTO'),
    ('PR10', 'Biópsia', 45, 'ALTO');


INSERT INTO atendimento (
    data_hora,
    duracao_minutos,
    id_paciente,
    id_residente,
    id_preceptor
)
VALUES
    ('2026-07-01 08:00:00', 31, 1, 6, 11),
    ('2026-07-02 09:00:00', 32, 2, 7, 11),
    ('2026-07-03 10:00:00', 33, 3, 8, 11),
    ('2026-07-04 11:00:00', 34, 4, 9, 11),
    ('2026-07-05 12:00:00', 35, 5, 10, 11),
    ('2026-07-06 13:00:00', 36, 1, 6, 11),
    ('2026-07-07 14:00:00', 37, 2, 7, 12),
    ('2026-07-08 15:00:00', 38, 3, 8, 13),
    ('2026-07-09 16:00:00', 39, 4, 9, 14),
    ('2026-07-10 17:00:00', 40, 5, 10, 15);


INSERT INTO procedimento_realizado (
    id_atendimento,
    id_procedimento,
    quantidade,
    tempo_real_minutos,
    observacao,
    faturado
)
VALUES
    (
        1,
        1,
        1,
        12,
        'Coleta realizada sem intercorrências.',
        TRUE
    ),
    (
        2,
        2,
        1,
        35,
        'Sutura realizada normalmente.',
        FALSE
    ),
    (
        3,
        3,
        1,
        18,
        'Medicação aplicada conforme prescrição.',
        TRUE
    ),
    (
        4,
        4,
        1,
        25,
        'Exame realizado sem alterações.',
        FALSE
    ),
    (
        5,
        5,
        1,
        130,
        'Cirurgia realizada com supervisão.',
        TRUE
    ),
    (
        6,
        6,
        2,
        22,
        'Foram realizados dois curativos.',
        FALSE
    ),
    (
        7,
        7,
        1,
        45,
        'Paciente permaneceu estável.',
        TRUE
    ),
    (
        8,
        8,
        1,
        15,
        'Eletrocardiograma sem alterações.',
        FALSE
    ),
    (
        9,
        9,
        1,
        28,
        'Intubação realizada sem intercorrências graves.',
        TRUE
    ),
    (
        10,
        10,
        1,
        50,
        'Material enviado para análise.',
        FALSE
    );


INSERT INTO escala (
    data_plantao,
    turno,
    id_unidade,
    id_residente,
    id_preceptor
)
VALUES
    ('2026-07-01', 'MANHA', 1, 6, 11),
    ('2026-07-01', 'TARDE', 2, 7, 12),
    ('2026-07-01', 'NOITE', 3, 8, 13),
    ('2026-07-02', 'MANHA', 1, 9, 14),
    ('2026-07-02', 'TARDE', 2, 10, 15),
    ('2026-07-05', 'NOITE', 1, 6, 11),
    ('2026-07-06', 'MANHA', 2, 7, 12),
    ('2026-07-07', 'TARDE', 3, 8, 13),
    ('2026-07-08', 'NOITE', 1, 9, 14),
    ('2026-07-09', 'MANHA', 2, 10, 15);
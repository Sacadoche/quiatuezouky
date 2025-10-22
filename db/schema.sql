-- Création de la table investigators
CREATE TABLE IF NOT EXISTS investigators (
    identite TEXT NOT NULL,
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    alias TEXT NOT NULL,
    role TEXT DEFAULT 'enqueteur'
);

-- Création de la table missions
CREATE TABLE IF NOT EXISTS missions (
    mission_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,
    expected_answer TEXT,
    success_message TEXT,
    attachment_path TEXT
);

-- Création de la table investigator_missions
CREATE TABLE IF NOT EXISTS investigator_missions (
    investigator_username TEXT NOT NULL,
    mission_id INTEGER NOT NULL,
    completed BOOLEAN NOT NULL,
    response TEXT,
    PRIMARY KEY (investigator_username, mission_id),
    FOREIGN KEY (investigator_username) REFERENCES investigators (username),
    FOREIGN KEY (mission_id) REFERENCES missions (mission_id)
);

-- Insertion des données initiales si elles n'existent pas
INSERT OR IGNORE INTO investigators (identite, username, password, alias, role)
VALUES
    ('Cindy BRAEM', '340765080', 'B7429', 'L’Encre Noire', 'enqueteur'),
    ('Anne BUREL', '101560170', 'M0384', 'La Main Fantôme', 'enqueteur'),
    ('Christelle DOUAY', '164007970', 'T5601', 'La Rose de Fer', 'enqueteur'),
    ('Noémie BRASSET', '684015202', 'R1947', 'L’Architecte', 'enqueteur'),
    ('Elisabeth DANTU', '350001479', 'H0052', 'La Louve Silencieuse', 'enqueteur'),
    ('Tiphaine IVON', '301506961', 'Z8316', 'La Veilleuse', 'enqueteur'),
    ('Juliette FROUIN', '150046314', 'K4090', 'L’Ombre du Bureau', 'enqueteur'),
    ('Amandine COUÉ', '807346951', 'P2673', 'La Sentinelle', 'enqueteur'),
    ('Edouard CHOISNET', '104383930', 'S9104', 'Le Fantôme du Dock', 'enqueteur'),
    ('Germain MOREAU', '421198366', 'V3268', 'Le Dernier Mot', 'enqueteur'),
    ('Anas ZAHRAWI', '733623419', 'C4507', 'Le Gardien', 'enqueteur'),
    ('Eric SZWAICER', '640680605', 'L7720', 'Le Sablier', 'enqueteur'),
    ('Mehdi BARBIN', '679809258', 'Y1189', 'Le Corbeau', 'enqueteur'),
    ('Frédéric LHUMEAU', '398867831', 'D6043', 'Le Chiffreur', 'enqueteur'),
    ('Gweltaz ROBERT', '612820234', 'F2506', 'Le Silencieux', 'enqueteur'),
    ('Hugues VAN WEYDEVELT', '414552832', 'N8875', 'Le Marcheur', 'enqueteur'),
    ('Maxime LESTRELIN', '534127684', 'X0391', 'L’Horloger', 'enqueteur'),
    ('Sébastien LACOUR', '420567302', 'E5562', 'Le Dossier Rouge', 'enqueteur'),
    ('Mathilde HUBERT', 'macolas', 'macolas', 'Inspecteur Hubert', 'admin');

-- Insertion des missions si elles n'existent pas
INSERT OR IGNORE INTO missions (mission_id, name, description, status)
VALUES
    (1, 'Mission 1', '', 'locked'),
    (2, 'Mission 2', '', 'locked'),
    (3, 'Mission 3', '', 'locked'),
    (4, 'Mission 4', '', 'locked'),
    (5, 'Mission 5', '', 'locked'),
    (6, 'Mission 6', '', 'locked'),
    (7, 'Mission 7', '', 'locked'),
    (8, 'Mission 8', '', 'locked'),
    (9, 'Mission 9', '', 'locked'),
    (10, 'Mission 10', '', 'locked'),
    (11, 'Mission 11', '', 'locked'),
    (12, 'Mission 12', '', 'locked'),
    (13, 'Mission 13', '', 'locked'),
    (14, 'Mission 14', '', 'locked'),
    (15, 'Mission 15', '', 'locked'),
    (16, 'Mission 16', '', 'locked'),
    (17, 'Mission 17', '', 'locked'),
    (18, 'Mission 18', '', 'locked'),
    (19, 'Mission 19', '', 'locked'),
    (20, 'Mission 20', '', 'locked'),
    (21, 'Mission 21', '', 'locked'),
    (22, 'Mission 22', '', 'locked'),
    (23, 'Mission 23', '', 'locked'),
    (24, 'Mission 24', '', 'locked'),
    (25, 'Mission 25', '', 'locked'),
    (26, 'Mission 26', '', 'locked'),
    (27, 'Mission 27', '', 'locked'),
    (28, 'Mission 28', '', 'locked'),
    (29, 'Mission 29', '', 'locked'),
    (30, 'Mission 30', '', 'locked');
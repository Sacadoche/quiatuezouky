from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'  # Remplacez par une clé secrète

# Initialisation de la base de données
def init_db():
    db = sqlite3.connect('enqueteur.db')
    cursor = db.cursor()

    # Création des tables si elles n'existent pas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS investigators (
            identite TEXT NOT NULL,
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            alias TEXT NOT NULL,
            role TEXT DEFAULT 'enqueteur'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS missions (
            mission_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS investigator_missions (
            investigator_username TEXT NOT NULL,
            mission_id INTEGER NOT NULL,
            completed BOOLEAN NOT NULL,
            PRIMARY KEY (investigator_username, mission_id),
            FOREIGN KEY (investigator_username) REFERENCES investigators (username),
            FOREIGN KEY (mission_id) REFERENCES missions (mission_id)
        )
    ''')

    # Insertion des données initiales si elles n'existent pas
    cursor.execute('SELECT COUNT(*) FROM investigators')
    if cursor.fetchone()[0] == 0:
        # Insertion des enquêteurs
        cursor.executemany('INSERT INTO investigators (identite, username, password, alias, role) VALUES (?, ?, ?, ?, ?)',
                           [('Cindy BRAEM', '340765080', 'B7429', 'L’Encre Noire', 'enqueteur'),
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

                            ('Mathilde HUBERT', 'macolas', 'macolas', 'Inspecteur Hubert', 'admin')])

        # Insertion des missions
        missions = [(i, f'Mission {i}', '', 'locked') for i in range(1, 41)]
        cursor.executemany('INSERT INTO missions (mission_id, name, description, status) VALUES (?, ?, ?, ?)', missions)

    db.commit()
    db.close()

# Appel de l'initialisation de la base de données
init_db()

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    alias = session['alias']
    role = session['role']
    db = sqlite3.connect('enqueteur.db')
    cursor = db.cursor()

    if role == 'admin':
        cursor.execute('SELECT * FROM investigators')
        investigators = cursor.fetchall()

        cursor.execute('SELECT * FROM missions')
        missions = cursor.fetchall()

        # Récupérer les missions complétées pour chaque enquêteur
        completed_missions = defaultdict(list)
        cursor.execute('SELECT investigator_username, mission_id FROM investigator_missions WHERE completed = 1')
        for row in cursor.fetchall():
            completed_missions[row[0]].append(row[1])

        db.close()
        return render_template('admin.html', investigators=investigators, missions=missions, completed_missions=completed_missions)

    # Récupérer les missions complétées par l'enquêteur
    cursor.execute('''
        SELECT mission_id FROM investigator_missions
        WHERE investigator_username = ? AND completed = 1
    ''', (username,))
    completed_missions = [row[0] for row in cursor.fetchall()]


    # Récupérer toutes les missions
    cursor.execute('SELECT * FROM missions')
    missions_db = cursor.fetchall()
    missions = {row[0]: {'name': row[1], 'description': row[2], 'status': row[3]} for row in missions_db}

    db.close()
    return render_template('index.html', missions=missions, completed_missions=completed_missions)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = sqlite3.connect('enqueteur.db')
        cursor = db.cursor()

        cursor.execute('SELECT password, alias, role FROM investigators WHERE username = ?', (username,))
        user = cursor.fetchone()
        db.close()

        if user and user[0] == password:
            session['username'] = username
            session['alias'] = user[1]
            session['role'] = user[2]
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Nom d\'utilisateur ou mot de passe incorrect')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/update_mission_status', methods=['POST'])
def update_mission_status():
    if 'username' not in session or session['username'] != 'macolas':
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403

    mission_id = int(request.form['mission_id'])
    new_status = request.form['new_status']

    db = sqlite3.connect('enqueteur.db')
    cursor = db.cursor()

    cursor.execute('UPDATE missions SET status = ? WHERE mission_id = ?', (new_status, mission_id))
    db.commit()
    db.close()

    return jsonify({'success': True})

@app.route('/update_investigator_mission', methods=['POST'])
def update_investigator_mission():
    if 'username' not in session or session['username'] != 'macolas':
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403

    investigator = request.form['investigator']
    mission_id = int(request.form['mission_id'])
    action = request.form['action']  # 'add' ou 'remove'

    db = sqlite3.connect('enqueteur.db')
    cursor = db.cursor()

    if action == 'add':
        cursor.execute('''
            INSERT OR REPLACE INTO investigator_missions (investigator_username, mission_id, completed)
            VALUES (?, ?, 1)
        ''', (investigator, mission_id))
    elif action == 'remove':
        cursor.execute('''
            DELETE FROM investigator_missions
            WHERE investigator_username = ? AND mission_id = ?
        ''', (investigator, mission_id))

    db.commit()
    db.close()

    return jsonify({'success': True})

@app.route('/update_mission_info', methods=['POST'])
def update_mission_info():
    if 'username' not in session or session['username'] != 'macolas':
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403

    mission_id = int(request.form['mission_id'])
    name = request.form['name']
    description = request.form['description']

    db = sqlite3.connect('enqueteur.db')
    cursor = db.cursor()

    cursor.execute('UPDATE missions SET name = ?, description = ? WHERE mission_id = ?', (name, description, mission_id))
    db.commit()
    db.close()

    return jsonify({'success': True})

@app.route('/get_mission_info/<int:mission_id>', methods=['GET'])
def get_mission_info(mission_id):
    db = sqlite3.connect('enqueteur.db')
    cursor = db.cursor()

    cursor.execute('SELECT name, description, status FROM missions WHERE mission_id = ?', (mission_id,))
    mission = cursor.fetchone()
    db.close()

    if mission:
        return jsonify({
            'success': True,
            'mission': {
                'name': mission[0],
                'description': mission[1],
                'status': mission[2]
            }
        })
    else:
        return jsonify({'success': False, 'error': 'Mission non trouvée'}), 404


if __name__ == '__main__':
    app.run(debug=True)

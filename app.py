from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'  # Remplacez par une clé secrète

def apply_schema():
    db = sqlite3.connect('enqueteur.db')
    cursor = db.cursor()

    # Lire et exécuter le fichier SQL pour créer les tables si elles n'existent pas
    with open('db/schema.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()
        cursor.executescript(sql_script)

    # Vérifier et ajouter les colonnes manquantes
    cursor.execute("PRAGMA table_info(investigator_missions)")
    existing_columns = [col[1] for col in cursor.fetchall()]

    if 'response_time' not in existing_columns:
        cursor.execute("ALTER TABLE investigator_missions ADD COLUMN response_time TEXT")
    if 'attempts' not in existing_columns:
        cursor.execute("ALTER TABLE investigator_missions ADD COLUMN attempts INTEGER DEFAULT 0")
    if 'validated' not in existing_columns:
        cursor.execute("ALTER TABLE investigator_missions ADD COLUMN validated BOOLEAN DEFAULT 0")

    # Assurer la présence de missions.expected_answer
    cursor.execute("PRAGMA table_info(missions)")
    missions_columns = [col[1] for col in cursor.fetchall()]
    if 'expected_answer' not in missions_columns:
        cursor.execute("ALTER TABLE missions ADD COLUMN expected_answer TEXT")
    # Nouveau: message de succès personnalisé
    cursor.execute("PRAGMA table_info(missions)")
    missions_columns = [col[1] for col in cursor.fetchall()]
    if 'success_message' not in missions_columns:
        cursor.execute("ALTER TABLE missions ADD COLUMN success_message TEXT")

    # Renseigner les réponses attendues pour les missions 1–3 si absentes
    cursor.execute("""
        UPDATE missions SET expected_answer = ?
        WHERE mission_id = ? AND (expected_answer IS NULL OR TRIM(expected_answer) = '')
    """, ('CANARD', 1))
    cursor.execute("""
        UPDATE missions SET expected_answer = ?
        WHERE mission_id = ? AND (expected_answer IS NULL OR TRIM(expected_answer) = '')
    """, ('Zouky aime beaucoup trop twerker', 2))
    cursor.execute("""
        UPDATE missions SET expected_answer = ?
        WHERE mission_id = ? AND (expected_answer IS NULL OR TRIM(expected_answer) = '')
    """, ('Enkhuizen', 3))

    db.commit()
    db.close()

# Appel de la fonction pour appliquer le schéma au démarrage
apply_schema()

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

        # Récupérer les missions validées pour chaque enquêteur (validated=1)
        completed_missions = defaultdict(list)
        cursor.execute('SELECT investigator_username, mission_id FROM investigator_missions WHERE validated = 1')
        for row in cursor.fetchall():
            completed_missions[row[0]].append(row[1])

        db.close()
        return render_template('admin.html', investigators=investigators, missions=missions, completed_missions=completed_missions)

    # Récupérer les missions complétées par l'enquêteur
    cursor.execute('''
        SELECT mission_id FROM investigator_missions
        WHERE investigator_username = ? AND validated = 1
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
    if 'username' not in session or session['role'] != 'admin':
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403

    mission_id = int(request.form['mission_id'])
    name = request.form['name']
    description = request.form['description']
    status = request.form['status']
    # Nouveau: champs admin
    expected_answer = (request.form.get('expected_answer') or '').strip()
    success_message = (request.form.get('success_message') or '').strip()

    db = sqlite3.connect('enqueteur.db')
    cursor = db.cursor()

    cursor.execute('''
        UPDATE missions
        SET name = ?, description = ?, status = ?, expected_answer = ?, success_message = ?
        WHERE mission_id = ?
    ''', (name, description, status, expected_answer or None, success_message or None, mission_id))

    db.commit()
    db.close()

    return jsonify({'success': True, 'message': 'Mission mise à jour avec succès.'})

@app.route('/get_mission_info/<int:mission_id>', methods=['GET'])
def get_mission_info(mission_id):
    db = sqlite3.connect('enqueteur.db')
    cursor = db.cursor()

    # Inclure expected_answer pour calculer requires_answer, ne pas le renvoyer
    cursor.execute('SELECT name, description, status, expected_answer FROM missions WHERE mission_id = ?', (mission_id,))
    mission = cursor.fetchone()
    db.close()

    if mission:
        name, description, status, expected_answer = mission
        requires_answer = bool((expected_answer or '').strip())
        return jsonify({
            'success': True,
            'mission': {
                'name': name,
                'description': description,
                'status': status,
                'requires_answer': requires_answer
            }
        })
    else:
        return jsonify({'success': False, 'error': 'Mission non trouvée'}), 404

@app.route('/submit_attempt', methods=['POST'])
def submit_attempt():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403

    try:
        mission_id = int(request.form['mission_id'])
    except (ValueError, KeyError):
        return jsonify({'success': False, 'error': 'ID de mission invalide.'}), 400

    response = request.form.get('response', '').strip()
    if not response:
        return jsonify({'success': False, 'error': 'La réponse est vide.'}), 400

    username = session['username']
    response_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    db = sqlite3.connect('enqueteur.db')
    cursor = db.cursor()

    try:
        # Tente de récupérer expected_answer + success_message (peut échouer si colonne manquante)
        try:
            cursor.execute('SELECT expected_answer, success_message FROM missions WHERE mission_id = ?', (mission_id,))
            row = cursor.fetchone()
        except sqlite3.OperationalError:
            # Fallback pour anciennes bases sans success_message
            cursor.execute('SELECT expected_answer FROM missions WHERE mission_id = ?', (mission_id,))
            r = cursor.fetchone()
            row = (r[0] if r else None, None)

        if not row:
            db.close()
            return jsonify({'success': False, 'error': 'Mission inconnue.'}), 404

        expected_response = (row[0] or '').strip()
        mission_success_message = (row[1] or '').strip() if len(row) > 1 else ''
        if not mission_success_message:
            mission_success_message = 'Mission validée avec succès !'

        if not expected_response:
            db.close()
            return jsonify({'success': False, 'error': 'Réponse attendue non définie pour cette mission.'}), 400

        def normalize(s: str) -> str:
            return " ".join(s.strip().lower().split())

        cursor.execute('''
            SELECT attempts, validated FROM investigator_missions
            WHERE investigator_username = ? AND mission_id = ?
        ''', (username, mission_id))
        result = cursor.fetchone()

        if result:
            attempts, validated = result
            if validated:
                db.close()
                return jsonify({'success': False, 'error': 'Mission déjà validée.'}), 400

            attempts += 1
            is_valid = normalize(response) == normalize(expected_response)

            cursor.execute('''
                UPDATE investigator_missions
                SET attempts = ?, response = ?, response_time = ?, validated = ?, completed = CASE WHEN ? THEN 1 ELSE completed END
                WHERE investigator_username = ? AND mission_id = ?
            ''', (attempts, response, response_time, 1 if is_valid else 0, is_valid, username, mission_id))
        else:
            attempts = 1
            is_valid = normalize(response) == normalize(expected_response)

            cursor.execute('''
                INSERT INTO investigator_missions (investigator_username, mission_id, completed, response, response_time, attempts, validated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, mission_id, 1 if is_valid else 0, response, response_time, attempts, 1 if is_valid else 0))

        db.commit()
        db.close()

        if is_valid:
            return jsonify({'success': True, 'message': mission_success_message, 'attempts': attempts, 'response_time': response_time})
        else:
            return jsonify({'success': False, 'error': 'Réponse incorrecte.', 'attempts': attempts, 'response_time': response_time})
    except Exception as e:
        # Log et réponse JSON propre
        try:
            db.close()
        except Exception:
            pass
        app.logger.exception("Erreur lors de submit_attempt")
        return jsonify({'success': False, 'error': 'Erreur serveur lors de la soumission.'}), 500

@app.route('/admin_validate_mission', methods=['POST'])
def admin_validate_mission():
    if 'username' not in session or session['role'] != 'admin':
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403

    investigator = request.form['investigator']
    mission_id = int(request.form['mission_id'])
    desired = request.form.get('validated') or request.form.get('checked') or '1'
    desired_state = 1 if str(desired).lower() in ('1', 'true', 'on', 'yes') else 0

    db = sqlite3.connect('enqueteur.db')
    cursor = db.cursor()

    if desired_state == 1:
        # Valider
        response_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO investigator_missions (investigator_username, mission_id, completed, response, response_time, attempts, validated)
            VALUES (?, ?, 1, 'Validé par admin', ?, 1, 1)
            ON CONFLICT(investigator_username, mission_id)
            DO UPDATE SET
                completed = 1,
                response = 'Validé par admin',
                response_time = excluded.response_time,
                attempts = CASE WHEN investigator_missions.attempts IS NULL OR investigator_missions.attempts = 0 THEN 1 ELSE investigator_missions.attempts END,
                validated = 1
        ''', (investigator, mission_id, response_time))
        msg = f'Mission {mission_id} validée pour {investigator}.'
    else:
        # Invalider
        cursor.execute('''
            INSERT INTO investigator_missions (investigator_username, mission_id, completed, response, response_time, attempts, validated)
            VALUES (?, ?, 0, NULL, NULL, 0, 0)
            ON CONFLICT(investigator_username, mission_id)
            DO UPDATE SET
                completed = 0,
                response = NULL,
                response_time = NULL,
                validated = 0
        ''', (investigator, mission_id))
        msg = f'Validation retirée pour {investigator} - mission {mission_id}.'

    db.commit()
    db.close()

    return jsonify({'success': True, 'message': msg})

@app.route('/mission_status', methods=['GET'])
def mission_status():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403

    mission_id = request.args.get('mission_id', type=int)
    username = session['username']

    db = sqlite3.connect('enqueteur.db')
    cursor = db.cursor()

    cursor.execute('''
        SELECT attempts, validated FROM investigator_missions
        WHERE investigator_username = ? AND mission_id = ?
    ''', (username, mission_id))
    result = cursor.fetchone()
    db.close()

    if result:
        attempts, validated = result
        return jsonify({'success': True, 'attempts': attempts, 'validated': validated})
    else:
        return jsonify({'success': True, 'attempts': 0, 'validated': False})

if __name__ == '__main__':
    app.run(debug=True)
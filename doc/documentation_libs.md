# ok recherche sur le web et fais moi un manuel d'utilisation des librairies don l'agent de code va avoir besoin. il n'as pas accès au web.

Voici le manuel d'utilisation complet des bibliothèques pour ton agent de code :

***

# Manuel d'utilisation des bibliothèques - Workpad

Ce document contient toutes les informations nécessaires pour implémenter Workpad sans accès au web.

***

## 1. Flask (Web Framework)

### Installation

```bash
pip install flask>=3.0.0
```


### Création d'une application minimale

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# Pour lancer : flask --app nom_fichier run
# Ou : python -m flask --app nom_fichier run
```


### Routes avec paramètres

```python
from flask import Flask
from markupsafe import escape

app = Flask(__name__)

# Route simple
@app.route('/hello')
def hello():
    return 'Hello, World'

# Route avec paramètre string
@app.route('/user/<username>')
def show_user_profile(username):
    return f'User {escape(username)}'

# Route avec paramètre int
@app.route('/post/<int:post_id>')
def show_post(post_id):
    return f'Post {post_id}'

# Route avec paramètre float
@app.route('/price/<float:price>')
def show_price(price):
    return f'Price {price}'
```


### Méthodes HTTP

```python
from flask import request

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return do_the_login()
    else:
        return show_the_login_form()

# Ou avec des décorateurs séparés
@app.get('/login')
def login_get():
    return show_the_login_form()

@app.post('/login')
def login_post():
    return do_the_login()
```


### Accéder aux données de requête

```python
from flask import request

@app.route('/login', methods=['POST'])
def login():
    # Accéder aux données de formulaire
    username = request.form['username']
    password = request.form['password']
    
    # Accéder aux paramètres d'URL (?key=value)
    search = request.args.get('q', '')
    
    # Accéder aux fichiers uploadés
    file = request.files['file']
    
    # Accéder au body JSON
    data = request.get_json()
    
    return 'OK'
```


### Retourner du JSON

```python
from flask import jsonify

@app.route("/api/users")
def users_api():
    users = get_all_users()
    # Retourner un dict ou une list = JSON automatique
    return {"users": users}

# Ou explicitement avec jsonify
@app.route("/api/user/<int:id>")
def user_api(id):
    user = get_user(id)
    return jsonify(user)
```


### Codes de statut HTTP

```python
from flask import jsonify

@app.route("/create", methods=['POST'])
def create():
    # Retourner code 201 Created
    return jsonify({"id": "123"}), 201

@app.route("/item/<id>")
def get_item(id):
    item = find_item(id)
    if not item:
        # Retourner 404 Not Found
        return jsonify({"error": "Not found"}), 404
    return jsonify(item)

# Avec tuple (response, status, headers)
@app.route("/data")
def data():
    return {"data": "value"}, 200, {"X-Custom": "header"}
```


### Gestion d'erreurs

```python
from flask import jsonify

@app.errorhandler(404)
def page_not_found(error):
    return jsonify({"error": "Not found", "code": 404}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error", "code": 500}), 500

# Erreurs personnalisées
class ValidationError(Exception):
    pass

@app.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify({"error": str(error), "code": 400}), 400
```


### Lancer l'application

```python
if __name__ == '__main__':
    # Mode debug (auto-reload)
    app.run(debug=True)
    
    # Production
    app.run(host='0.0.0.0', port=5001, debug=False)
```


### Configuration

```python
app = Flask(__name__)

# Secret key pour sessions
app.secret_key = 'votre-secret-key'

# Configuration
app.config['DEBUG'] = True
app.config['TESTING'] = False

# Depuis dict
app.config.from_mapping(
    DEBUG=True,
    SECRET_KEY='dev'
)

# Depuis environnement
import os
app.config['DATABASE'] = os.environ.get('DATABASE_URL')
```


***

## 2. Pydantic (Validation)

### Installation

```bash
pip install pydantic>=2.0.0
```


### Modèle de base

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str = 'Jane Doe'  # Avec valeur par défaut
    age: int  # Requis

# Créer une instance
user = User(id='123', name='John')  # '123' sera converti en int 123
print(user.id)  # 123
print(user.name)  # 'John'
print(user.age)  # Erreur : champ requis manquant
```


### Validation automatique

```python
from pydantic import BaseModel, ValidationError

class User(BaseModel):
    id: int
    name: str
    age: int

# Données valides
user = User(id=1, name='John', age=30)

# Données invalides
try:
    user = User(id='abc', name='John', age=30)
except ValidationError as e:
    print(e)
    # Affiche : 1 validation error for User
    # id: Input should be a valid integer...
```


### Types optionnels

```python
from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: Optional[str] = None  # Peut être None
    age: int

user = User(id=1, name='John', age=30)
print(user.email)  # None
```


### Listes et dicts

```python
from typing import List, Dict
from pydantic import BaseModel

class Model(BaseModel):
    items: List[int]
    metadata: Dict[str, str]

m = Model(items=[1, 2, 3], metadata={"key": "value"})
print(m.items)  # [1, 2, 3]
```


### Modèles imbriqués

```python
from typing import List
from pydantic import BaseModel

class Pet(BaseModel):
    name: str
    species: str

class Person(BaseModel):
    name: str
    age: int
    pets: List[Pet]

person = Person(
    name='Anna',
    age=20,
    pets=[
        {'name': 'Bones', 'species': 'dog'},
        {'name': 'Orion', 'species': 'cat'}
    ]
)
print(person.pets[^0].name)  # 'Bones'
```


### Sérialisation

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str

user = User(id=123, name='John')

# Vers dict
print(user.model_dump())
# {'id': 123, 'name': 'John'}

# Vers JSON string
print(user.model_dump_json())
# '{"id":123,"name":"John"}'
```


### Désérialisation

```python
from pydantic import BaseModel, ValidationError

class User(BaseModel):
    id: int
    name: str

# Depuis dict
user = User.model_validate({'id': 123, 'name': 'John'})

# Depuis JSON string
user = User.model_validate_json('{"id": 123, "name": "John"}')

# Erreur si invalide
try:
    user = User.model_validate(['not', 'a', 'dict'])
except ValidationError as e:
    print(e)
```


### Field avec validation

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., ge=0, le=120)  # >= 0 et <= 120
    email: str = Field(default='', description='Email address')

user = User(id=1, name='John', age=25)
```


### Enums

```python
from enum import Enum
from pydantic import BaseModel

class Color(str, Enum):
    red = 'red'
    green = 'green'
    blue = 'blue'

class Item(BaseModel):
    name: str
    color: Color

item = Item(name='Ball', color='red')
print(item.color)  # Color.red
print(item.color.value)  # 'red'
```


### Alias

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    id: int
    user_name: str = Field(alias='userName')

# Input avec alias
user = User(id=1, userName='john')
print(user.user_name)  # 'john'

# Dump avec alias
print(user.model_dump(by_alias=True))
# {'id': 1, 'userName': 'john'}
```


### Configuration de modèle

```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(
        frozen=True,  # Immutable
        extra='forbid',  # Interdire champs extra
        str_strip_whitespace=True  # Strip whitespace des strings
    )
    
    id: int
    name: str

user = User(id=1, name='  John  ')
print(user.name)  # 'John' (stripped)

try:
    user.id = 2  # Erreur : frozen
except:
    pass

try:
    User(id=1, name='John', extra='field')  # Erreur : extra='forbid'
except:
    pass
```


### Création sans validation

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str

# DANGER : pas de validation !
user = User.model_construct(id='not-an-int', name='John')
print(user.id)  # 'not-an-int' (invalide mais accepté)

# Utiliser seulement avec données déjà validées
```


***

## 3. pytest (Testing)

### Installation

```bash
pip install pytest>=7.0.0
pip install pytest-cov  # Pour coverage
```


### Premier test

```python
# Fichier: test_sample.py

def func(x):
    return x + 1

def test_answer():
    assert func(3) == 4

def test_another():
    assert func(0) == 1
```


### Lancer les tests

```bash
# Tous les tests
pytest

# Un fichier spécifique
pytest test_sample.py

# Un test spécifique
pytest test_sample.py::test_answer

# Verbose
pytest -v

# Avec coverage
pytest --cov=workpad tests/
```


### Tests avec classes

```python
class TestCalculator:
    def test_addition(self):
        assert 1 + 1 == 2
    
    def test_subtraction(self):
        assert 5 - 3 == 2
```


### Assertions

```python
def test_assertions():
    # Égalité
    assert 1 == 1
    
    # Comparaison
    assert 5 > 3
    assert 2 <= 2
    
    # Membership
    assert 'a' in 'abc'
    assert 'x' not in 'abc'
    
    # Types
    assert isinstance(5, int)
    
    # Exceptions
    import pytest
    with pytest.raises(ValueError):
        int('abc')
    
    # Exception avec message
    with pytest.raises(ValueError, match='invalid literal'):
        int('abc')
```


### Fixtures

```python
import pytest

@pytest.fixture
def sample_data():
    """Fixture qui retourne des données"""
    return {'id': 1, 'name': 'test'}

def test_with_fixture(sample_data):
    """Utilise la fixture comme argument"""
    assert sample_data['id'] == 1
    assert sample_data['name'] == 'test'

# Fixture avec setup/teardown
@pytest.fixture
def database():
    # Setup
    db = create_database()
    db.connect()
    
    yield db  # Fournit la fixture
    
    # Teardown
    db.disconnect()
    db.delete()

def test_database(database):
    database.insert({'name': 'test'})
    assert database.count() == 1
```


### Fixtures avec scope

```python
import pytest

@pytest.fixture(scope='function')  # Défaut : chaque test
def func_fixture():
    return setup()

@pytest.fixture(scope='module')  # Une fois par module
def module_fixture():
    return setup()

@pytest.fixture(scope='session')  # Une fois pour toute la session
def session_fixture():
    return setup()
```


### Fixtures imbriquées

```python
import pytest

@pytest.fixture
def base_data():
    return {'id': 1}

@pytest.fixture
def extended_data(base_data):
    base_data['name'] = 'test'
    return base_data

def test_extended(extended_data):
    assert extended_data == {'id': 1, 'name': 'test'}
```


### Parametrize

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 3),
    (5, 6),
])
def test_increment(input, expected):
    assert input + 1 == expected

# Avec IDs personnalisés
@pytest.mark.parametrize("x,y,result", [
    (1, 2, 3),
    (5, 10, 15),
], ids=["simple", "larger"])
def test_addition(x, y, result):
    assert x + y == result
```


### Temporary files

```python
def test_with_tmp_path(tmp_path):
    """tmp_path est une fixture pytest intégrée"""
    # tmp_path est un objet Path vers un dossier temporaire
    file = tmp_path / "test.txt"
    file.write_text("content")
    assert file.read_text() == "content"
    # Nettoyé automatiquement après le test
```


### Marks

```python
import pytest

@pytest.mark.skip(reason="Not implemented yet")
def test_skip():
    pass

@pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires Python 3.10+")
def test_conditional_skip():
    pass

@pytest.mark.xfail(reason="Known bug")
def test_expected_to_fail():
    assert False  # Test marqué xfail même s'il échoue
```


### Fixtures pour Flask

```python
import pytest
from workpad.api.routes import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_entries(client):
    response = client.get('/entries')
    assert response.status_code == 200
    assert response.json['entries'] == []

def test_post_entry(client):
    response = client.post('/entries', json={
        'type': 'note',
        'content': 'Test note'
    })
    assert response.status_code == 201
    assert 'id' in response.json
```


***

## 4. Python logging

### Basic usage

```python
import logging

# Configuration basique
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Log messages
logging.debug('Debug message')
logging.info('Info message')
logging.warning('Warning message')
logging.error('Error message')
logging.critical('Critical message')
```


### Logger personnalisé

```python
import logging

# Créer un logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Handler console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Handler fichier
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.ERROR)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Ajouter handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Utiliser
logger.debug('Debug message')
logger.info('Info message')
logger.error('Error message')
```


### Niveaux de log

```python
import logging

# NOTSET = 0
# DEBUG = 10
# INFO = 20
# WARNING = 30
# ERROR = 40
# CRITICAL = 50

logger.setLevel(logging.DEBUG)  # Tout passe
logger.setLevel(logging.WARNING)  # Seulement WARNING et au-dessus
```


### Log avec variables

```python
logger.info('User %s logged in', username)
logger.error('Failed to connect to %s:%d', host, port)

# f-strings (Python 3.6+)
logger.info(f'User {username} logged in')
```


### Log exceptions

```python
try:
    1 / 0
except Exception as e:
    logger.exception('An error occurred')  # Inclut le traceback
    # Ou
    logger.error('An error occurred', exc_info=True)
```


***

## 5. SQLite (Python)

### Installation

Inclus dans Python standard library, pas besoin d'installer.

### Créer une connexion

```python
import sqlite3

# Créer/ouvrir une base de données
conn = sqlite3.connect('database.db')

# En mémoire (pour tests)
conn = sqlite3.connect(':memory:')

# Cursor pour exécuter des requêtes
cursor = conn.cursor()
```


### Créer une table

```python
import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        age INTEGER
    )
''')

conn.commit()
```


### Insérer des données

```python
# Une seule ligne
cursor.execute('''
    INSERT INTO users (name, email, age)
    VALUES (?, ?, ?)
''', ('John', 'john@example.com', 30))

# Plusieurs lignes
users = [
    ('Alice', 'alice@example.com', 25),
    ('Bob', 'bob@example.com', 35)
]
cursor.executemany('''
    INSERT INTO users (name, email, age)
    VALUES (?, ?, ?)
''', users)

conn.commit()
```


### Sélectionner des données

```python
# Toutes les lignes
cursor.execute('SELECT * FROM users')
rows = cursor.fetchall()
for row in rows:
    print(row)  # (1, 'John', 'john@example.com', 30)

# Une seule ligne
cursor.execute('SELECT * FROM users WHERE id = ?', (1,))
row = cursor.fetchone()
print(row)

# Avec WHERE
cursor.execute('SELECT name, age FROM users WHERE age > ?', (25,))
rows = cursor.fetchall()
```


### Row factory (accès par nom)

```python
import sqlite3

conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute('SELECT * FROM users')
rows = cursor.fetchall()

for row in rows:
    print(row['name'])  # Accès par nom de colonne
    print(row['email'])
```


### Mettre à jour

```python
cursor.execute('''
    UPDATE users
    SET age = ?
    WHERE name = ?
''', (31, 'John'))

conn.commit()
print(cursor.rowcount, 'rows updated')
```


### Supprimer

```python
cursor.execute('DELETE FROM users WHERE age < ?', (25,))
conn.commit()
print(cursor.rowcount, 'rows deleted')
```


### Transactions

```python
try:
    cursor.execute('INSERT INTO users VALUES (?, ?, ?)', (1, 'John', 30))
    cursor.execute('INSERT INTO users VALUES (?, ?, ?)', (2, 'Alice', 25))
    conn.commit()
except sqlite3.Error as e:
    conn.rollback()
    print(f'Error: {e}')
```


### Context manager (auto close)

```python
import sqlite3

with sqlite3.connect('database.db') as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()
# Connexion fermée automatiquement
```


### Index

```python
cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_users_email
    ON users(email)
''')
```


***

## 6. python-dotenv (Variables d'environnement)

### Installation

```bash
pip install python-dotenv
```


### Fichier .env

```
# .env
WORKPAD_HOST=0.0.0.0
WORKPAD_PORT=5001
WORKPAD_DEBUG=true
DATABASE_PATH=./data/database.db
SECRET_KEY=your-secret-key-here
```


### Charger les variables

```python
import os
from dotenv import load_dotenv

# Charger depuis .env
load_dotenv()

# Accéder aux variables
host = os.getenv('WORKPAD_HOST', '127.0.0.1')  # Défaut: 127.0.0.1
port = int(os.getenv('WORKPAD_PORT', 5001))
debug = os.getenv('WORKPAD_DEBUG', 'false').lower() == 'true'

print(f'Host: {host}, Port: {port}, Debug: {debug}')
```


***

## 7. Bonnes pratiques générales

### Structure de test

```python
# tests/test_service.py
import pytest
from workpad.service import WorkpadService
from workpad.storage.json_storage import JSONStorage

@pytest.fixture
def storage(tmp_path):
    return JSONStorage(tmp_path)

@pytest.fixture
def service(storage):
    return WorkpadService(storage)

def test_create_entry(service):
    entry = service.create_entry({
        'type': 'note',
        'content': 'Test'
    })
    assert entry.id is not None
    assert entry.content == 'Test'

def test_get_entry_not_found(service):
    with pytest.raises(NotFoundError):
        service.get_entry('invalid-id')
```


### Flask + Pydantic

```python
from flask import Flask, jsonify, request
from pydantic import BaseModel, ValidationError

app = Flask(__name__)

class CreateEntryRequest(BaseModel):
    type: str
    content: str

@app.post('/entries')
def create_entry():
    try:
        data = CreateEntryRequest(**request.get_json())
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    
    entry = service.create_entry(data.model_dump())
    return jsonify(entry.model_dump()), 201
```


***

**Ce manuel couvre tout ce dont l'agent aura besoin pour implémenter Workpad ! 🚀**
<span style="display:none">[^1][^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^2][^20][^3][^4][^5][^6][^7][^8][^9]</span>

<div align="center">⁂</div>

[^1]: https://flask.palletsprojects.com

[^2]: https://devdocs.io/flask~3.0/

[^3]: https://flask.palletsprojects.com/en/stable/tutorial/

[^4]: https://flask.palletsprojects.com/en/stable/quickstart/

[^5]: https://flask-doc-pdf-gen.readthedocs.io/_/downloads/en/latest/pdf/

[^6]: https://www.youtube.com/watch?v=ok8bF8M7gjk

[^7]: https://docs.pytest.org/en/stable/explanation/fixtures.html

[^8]: https://www.youtube.com/watch?v=VRoXgHyJGx8

[^9]: https://docs.pydantic.dev/2.0/usage/models/

[^10]: https://pythontest.com/framework/pytest/pytest-fixtures-easy-example/

[^11]: https://docs.pytest.org/en/stable/getting-started.html

[^12]: https://realpython.com/pytest-python-testing/

[^13]: https://www.tutorialspoint.com/pytest/index.htm

[^14]: https://testdriven.io/blog/pytest-for-beginners/

[^15]: https://blog.teclado.com/pytest-for-beginners/

[^16]: https://www.loggly.com/ultimate-guide/python-logging-basics/

[^17]: https://www.tutorialspoint.com/sqlite/sqlite_python.htm

[^18]: https://www.geeksforgeeks.org/python/getting-started-with-pytest/

[^19]: https://www.dash0.com/guides/logging-in-python

[^20]: https://www.sqlitetutorial.net/sqlite-python/


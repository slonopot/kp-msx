import sqlite3
import json
import config
from util import sqlite_migrations

connection = sqlite3.connect(config.SQLITE_URL, autocommit=True)

connection.execute(
    '''
    CREATE TABLE IF NOT EXISTS migrations (id INT PRIMARY KEY, name TEXT)
    '''
)
current_version = connection.execute('SELECT MAX(id) FROM migrations').fetchone()[0] or 0

migrations = sqlite_migrations.get_migrations()
latest_version = len(migrations)
for i in range(current_version, latest_version):
    connection.executescript(migrations[i])
    print(f'SQLite DB schema is updated to v{i + 1}')

def get_device_by_id(device_id):
    cursor = connection.execute(
        '''
        SELECT id, code, refresh, token, settings, user_agent
        FROM devices
        WHERE id = ?1
        ''', [device_id])
    return to_device_dict(cursor.fetchone())


def create_device(entry):
    settings = entry.get('settings')
    settingsJson = None if settings is None else json.dumps(settings)
    cursor = connection.execute(
        '''
        INSERT INTO devices (id, code, refresh, token, settings, user_agent)
        VALUES (?1, ?2, ?3, ?4, ?5, ?6)
        RETURNING id, code, refresh, token, settings, user_agent
        ''',
        [
            entry.get('id'),
            entry.get('code'),
            entry.get('refresh'),
            entry.get('token'),
            settingsJson,
            entry.get('user_agent'),
        ]
    )
    return to_device_dict(cursor.fetchone())


def update_device_code(id, code):
    cursor = connection.execute(
        '''
        UPDATE devices SET code = ?2
        WHERE id = ?1
        RETURNING id, code, refresh, token, settings, user_agent
        ''',
        [ id, code ]
    )
    return to_device_dict(cursor.fetchone())


def update_device_tokens(id, token, refresh):
    cursor = connection.execute(
        '''
        UPDATE devices SET token = ?2, refresh = ?3
        WHERE id = ?1
        RETURNING id, code, refresh, token, settings, user_agent
        ''',
        [
            id, token, refresh
        ]
    )
    return to_device_dict(cursor.fetchone())


def update_tokens(token, newToken, refresh):
    cursor = connection.execute(
        '''
        UPDATE devices SET token = ?2, refresh = ?3
        WHERE token = ?1
        RETURNING id, code, refresh, token, settings, user_agent
        ''',
        [token, newToken, refresh]
    )
    return to_device_dict(cursor.fetchone())


def delete_device(id):
    cursor = connection.execute(
        '''
        DELETE FROM devices
        WHERE id = ?1
        RETURNING id, code, refresh, token, settings, user_agent
        ''', [id]
    )
    return to_device_dict(cursor.fetchone())


def update_device_user_agent(id, user_agent):
    cursor = connection.execute(
        '''
        UPDATE devices SET user_agent = ?2
        WHERE id = ?1
        RETURNING id, code, refresh, token, settings, user_agent
        ''',
        [id, user_agent]
    )
    return to_device_dict(cursor.fetchone())


def update_device_settings(id, param):
    cursor = connection.execute(
        '''
        UPDATE devices SET settings = ?2
        WHERE id = ?1
        RETURNING id, code, refresh, token, settings, user_agent
        ''',
        [id, json.dumps(param)]
    )
    return to_device_dict(cursor.fetchone())


def get_domain(domain):
    cursor = connection.execute(
        '''
        SELECT domain FROM domains
        WHERE domain = ?1
        ''', [domain])
    domain = cursor.fetchone()
    return None if domain is None else domain[0]


def add_domain(domain):
    cursor = connection.execute(
        '''
        INSERT INTO domains (domain)
        VALUES (?1)
        RETURNING domain
        ''', [domain])
    domain = cursor.fetchone()
    return None if domain is None else domain[0]


def to_device_dict(row):
    return None if row is None else {
        'id': row[0],
        'code': row[1],
        'refresh': row[2],
        'token': row[3],
        'settings': None if row[4] is None else json.loads(row[4]),
        'user_agent': row[5]
    }

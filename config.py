from krc.env import EnvVar

DATABASE_NAME = 'TEST'
DATABASE_HOST = '10.10.81.19'
DATABASE_PORT = '50000'
DATABASE_USER = EnvVar('DBUser').value
DATABASE_PASSWORD = EnvVar('DBPassword').value

# kismet-bitmotion
## INITIAL SETUP/PYTHON
#### Clone Repo
```
git clone https://github.com/DirtyOptics/kismet-bitmotion.git
```
#### Nav to repo
```
cd kismet-bitmotion
```
#### Create python virtual environment (environment called vws)
```
sudo python3 -m venv vws
```
#### Activate 'kismet' virtual environment
```
source vws/bin/activate
```
#### You may need to change permissions of the pulled folder:
```
sudo chown -R $(whoami) /home/user/kismet-bitmotion
sudo chmod -R u+rwX /home/user/kismet-bitmotion
```
#### Install the items from inside requirements.txt
```
pip install -r requirements.txt
```

## DATABASE CREATION

PostgreSQL 14 - Installed locally to Grafana. Config.yaml has the url to db.
Create db, username/pw etc. Modify the PostgreSQL server config to allow traffic in and out. Don't forget to allow port 5432 in firewall.

#### log in to PostgreSQL as super user
```
sudo -i -u postgres
```
#### Start Postgres
```
psql
```
##### verify users
```
\du
```
##### create user 'db'
```
CREATE USER db WITH PASSWORD 'your_password';
```
##### Create databases
```
CREATE DATABASE kismet_db_aps OWNER db;
```
```
CREATE DATABASE kismet_db_client OWNER db;
```
##### permissions
```
GRANT ALL PRIVILEGES ON DATABASE kismet_db_aps TO db;
```
```
GRANT ALL PRIVILEGES ON DATABASE kismet_db_clients TO db;
```
##### exit PostgreSQL CLI
```
\q
```
##### exit postgres
```
exit
```

#### Edit postgresql.conf
```
sudo nano /etc/postgresql/14/main/postgresql.conf
```
```
listen_addresses = '*'
```
#### Edit pg_hba.conf
```
sudo nano /etc/postgresql/14/main/pg_hba.conf
```
```
# Allow all IPv4 addresses
host    all             all             0.0.0.0/0            md5

# Alternatively, allow connections from a specific IP range
host    all             all             <your-ip-range>/24   md5
```
#### Retsart Postgresql
```
sudo systemctl restart postgresql
```


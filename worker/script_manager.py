import requests
import sqlite3
import os
import urlparse
import logging
import shutil
import time

from common import config
from requests.auth import HTTPBasicAuth

log = logging.getLogger(__name__)


class ScriptFileDB(object):
    def __init__(self):
        self.db_file = config.get("script.db_file", "scriptsdb.sqlite3")
        self.connection = sqlite3.connect(self.db_file)
        self.initialize()

    def initialize(self):
        self.execute('''CREATE TABLE IF NOT EXISTS scripts (id text PRIMARY
                            KEY, file text, cache integer, ttd integer)''')

    def add_script_file(self, script_id, script_file, cache=False, ttd=0):
        self.execute("INSERT INTO scripts VALUES (?, ?, ?, ?)",
                script_id, script_file, cache, ttd)

    def get_script_file(self, script_id):
        res = self.execute("SELECT * FROM scripts WHERE id=? AND (ttd=0 OR ttd>?)", script_id, time.time())
        if res:
            _, file_name, _, _ = res[0]
            return file_name
        else:
            return None

    def get_scripts(self, **kwargs):

        values = []
        query = []
        for key, value in kwargs.iteritems():
            query.append("%s=?" % key)
            values.append(value)

        query = " AND ".join(query)
        where_clause = ""
        if query:
            where_clause = "WHERE %s" % query

        return self.execute(" ".join(["SELECT * FROM scripts", where_clause]), *values)

    def execute(self, query, *args):
        c = self.connection.cursor()
        c.execute(query, args)
        results = c.fetchall()
        self.connection.commit()
        return results


class ScriptManager(object):
    """
    Handles script load and storage
    """
    def __init__(self):
        self.script_ttl = config.getint("script.ttl", 60) # minutes
        self.scripts_folder = config.get("script.folder", "scripts")
        self.master_host = config.get("script.master_host")

        self.api_user = config.get("script.api_user")
        self.api_password = config.get("script.api_password")

        self.file_db = ScriptFileDB()

    def clean(self):
        files_to_remove = self.file_db.get_scripts(cache=True)
        files_to_remove.append(self.file_db.db_file)
        for f in files_to_remove:
            if os.path.exists(f):
                shutil.rmtree(f) if os.path.isdir(f) else os.remove(f) 

    def get(self, task): 
        path = self.file_db.get_script_file(task.scenario_id)
        if not path or not os.path.exists(path):
            path = os.path.join(self.scripts_folder, task.scenario_id)
            if not os.path.exists(path):
                if not self.download_script(task, path):
                    if os.path.exists(path):
                        os.unlink(path)
                    return None

        return path

    def download_script(self, task, path):
        if os.path.exists(path):
            self.file_db.add_script_file(task.scenario_id, path)
            return True

        host = task.source_host or self.master_host
        if not host:
            return False

        url = "http://%s/v1/scenarios/%s/content" % (host, task.scenario_id)
        log.info("Going to download script in cache from %s", url)

        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(path, 'wb') as handle:
            try:
                kwargs = dict(stream=True, params={"format": "txt"})
                if self.api_user and self.api_password:
                    kwargs["auth"] = HTTPBasicAuth(self.api_user, self.api_password)
                response = requests.get(url, **kwargs)
            except:
                log.exception("Failed to request script from master host")
                return False

            if not response.ok:
                logging.error("Failed to get %s", url)
                return False

            for block in response.iter_content(1024):
                if not block:
                    break

                handle.write(block)

            self.file_db.add_script_file(task.scenario_id, path, cache=True,
                    ttd=time.time() + self.script_ttl * 60)
            return True


import redis as r

import logging, os, json, sys, signal, time, random

db = {}
log = None
log_level = os.environ.get("LOG_LEVEL", "DEBUG")
wait_enabled = os.environ.get("WAIT_ENABLED", "false").upper() == "TRUE"
min_wait = float(os.environ.get("MIN_WAIT_MS", "25")) / 1000
max_wait = float(os.environ.get("MAX_WAIT_MS", "250")) / 1000

class GracefulKiller:
    terminating = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        global terminating
        terminating = True
        log.warning("closing api (%s)" % (signum))
        sys.exit(0)

ctx = GracefulKiller()

def init_logger(name):
    global log
    logging.basicConfig(
        format="%(asctime)s %(name)s " + name + " %(levelname)-8s %(message)s",
        level=log_level,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    log = logging.getLogger(name)
    log.warning("log level is %s" % log_level)
    return log


def init_db(db_name, host, port):
    global db
    if db:
        return
    db[db_name] = r.StrictRedis(
        host=host,
        port=port,
        decode_responses=True,
    )


def add(db_name, topic, uid, data):
    
    # 33% chance to sleep for a bit
    if wait_enabled and random.randrange(0, 100) <= 33:
        time.sleep(random.uniform(min_wait, max_wait))

    if type(data) is not str:
        raise Exception("'data' should be string")
    
    if db_name not in db:
        raise Exception("db %s does not exist" % db_name)

    key = "%s.%s" % (topic, uid)

    if db[db_name].get(key):
        raise Exception("key already exists")
    
    log.debug("%s %s" % (uid, topic))
    db[db_name].set(key, data)
    db[db_name].sadd(topic, uid)


def get(db_name, topic, uid):
        
    if wait_enabled:
        # sleep for a bit
        time.sleep(random.uniform(min_wait, max_wait))

    if db_name not in db:
        raise Exception("db %s does not exist" % db_name)
    
    data = ""
    key = "%s.%s" % (topic, uid)

    if uid:
        try:
            data = json.loads(db[db_name].get(key))
        except:
            raise Exception("key %s does not exist" % key)

    if not uid:
        try:
            data = []
            uids = db[db_name].smembers(topic)
            for uid in uids:
                key = "%s.%s" % (topic, uid)
                row = db[db_name].get(key)
                data.append(json.loads(row))

        except:
            raise Exception("error returning all keys")
    
    return data


def rm(db_name, topic, uid=None):
        
    if wait_enabled:
        # sleep for a bit
        time.sleep(random.uniform(min_wait, max_wait))

    if db_name not in db:
        raise Exception("db %s does not exist" % db_name)
    
    key = "%s.%s" % (topic, uid)

    try:
        db[db_name].get(key)
        db[db_name].srem(topic, uid)
    except:
        raise Exception("key %s does not exist" % key)
    
    db[db_name].delete(key)


def add_to_list(db_name, key, uid):
        
    if wait_enabled:
        # sleep for a bit
        time.sleep(random.uniform(min_wait, max_wait))

    if db_name not in db:
        raise Exception("db %s does not exist" % db_name)

    db[db_name].sadd(key, uid)


def rm_from_list(db_name, key, uid):
        
    if wait_enabled:
        # sleep for a bit
        time.sleep(random.uniform(min_wait, max_wait))

    if db_name not in db:
        raise Exception("db %s does not exist" % db_name)
    
    db[db_name].srem(key, uid)


def get_list(db_name, key):
        
    if wait_enabled:
        # sleep for a bit
        time.sleep(random.uniform(min_wait, max_wait))

    if db_name not in db:
        raise Exception("db %s does not exist" % db_name)
    
    return db[db_name].smembers(key)
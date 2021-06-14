from os import getenv, path
from telethon.sessions import StringSession

TELEGRAM_DAEMON_SESSION_PATH = getenv("TELEGRAM_DAEMON_SESSION_PATH")
sessionName = "DownloadDaemon"
stringSessionFilename = "{0}.session".format(sessionName)


def _getStringSessionIfExists():
    sessionPath = path.join(TELEGRAM_DAEMON_SESSION_PATH,
                            stringSessionFilename)
    if path.isfile(sessionPath):
        with open(sessionPath, 'r') as file:
            session = file.read()
            print("Session loaded from {0}".format(sessionPath))
            return session
    return None


def getSession():
    if TELEGRAM_DAEMON_SESSION_PATH == None:
        return sessionName

    return StringSession(_getStringSessionIfExists())


def saveSession(session):
    if TELEGRAM_DAEMON_SESSION_PATH != None:
        sessionPath = path.join(TELEGRAM_DAEMON_SESSION_PATH,
                                stringSessionFilename)
        with open(sessionPath, 'w') as file:
            file.write(StringSession.save(session))
        print("Session saved in {0}".format(sessionPath))

from sparts.vservice import VService
from sparts.tasks.poller import PollerTask
from subprocess import Popen, PIPE
import re

CONFIG = {
    'TapButton1': 0,
    #'HorizHysteresis': 39,
    #'VertHysteresis': 27,
    'HorizHysteresis': 8,
    'VertHysteresis': 7,
}


def get_synclient_settings():
    p = Popen(['/usr/bin/synclient', '-l'], shell=False, stdout=PIPE,
              stdin=open('/dev/null', mode='r'),
              close_fds=True)
    stdout, stderr = p.communicate()
    result = {}
    for l in stdout.split("\n"):
        m = re.match('\s*([^=]+?)\s*=\s*(.*?)\s*$', l)
        if not m:
            continue
        k, v = m.groups()
        result[k.strip()] = float(v.strip())
    return result

def synclient_set(key, value):
    p = Popen(['/usr/bin/synclient', '%s=%s' % (key, value)])
    p.communicate()


class SettingsWatcher(PollerTask):
    INTERVAL = 5
    def fetch(self):
        return get_synclient_settings()

    def onValueChanged(self, old_value, new_value):
        old_value = old_value or {}
        for k in new_value:
            old_item = old_value.get(k, '')
            new_item = new_value[k]
            if old_item != new_item:
                self.logger.debug("%s changed from '%s' to '%s'", k, old_item, new_item)
                if k in CONFIG:
                    if new_item != CONFIG[k]:
                        self.logger.info("Fixing %s", k)
                        synclient_set(k, CONFIG[k])

class MyService(VService):
    TASKS = [SettingsWatcher]

if __name__ == '__main__':
    MyService.initFromCLI()

from sparts.vservice import VService
from sparts.tasks.poller import PollerTask
from subprocess import Popen, PIPE
import re

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

def fix_tapbutton():
    p = Popen(['/usr/bin/synclient', 'TapButton1=0'])
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
                if k == 'TapButton1' and new_item != 0:
                    self.logger.info("Fixing TapButton1")
                    fix_tapbutton()

class MyService(VService):
    TASKS = [SettingsWatcher]

if __name__ == '__main__':
    MyService.initFromCLI()


import random
from collections import OrderedDict

from huepy import bold, green, orange


class file(object):
    def __init__(self, fname, verbose=True):
        self.fname = fname
        self.verbose = verbose
        open(self.fname, 'a').close()

    @property
    def list(self):
        with open(self.fname, 'r') as f:
            lines = [x.strip('\n') for x in f.readlines()]
            return [x for x in lines if x]

    @property
    def set(self):
        return set(self.list)

    def __iter__(self):
        for i in self.list:
            yield next(iter(i))

    def __len__(self):
        return len(self.list)

    def append(self, item, allow_duplicates=False):
        from instabot.bot import bot_support
        if self.verbose:
            msg = "Adding '{}' to `{}`.".format(item, self.fname)
            bot_support.console_print(bot_support,msg,color='green',bold_text=True)

        if not allow_duplicates and str(item) in self.list:
            msg = "'{}' already in `{}`.".format(item, self.fname)
            bot_support.console_print(bot_support,msg,color='orange',bold_text=True)
            return

        with open(self.fname, 'a') as f:
            f.write('{item}\n'.format(item=item))

    def remove(self, x):
        from instabot.bot import bot_support
        x = str(x)
        items = self.list
        if x in items:
            items.remove(x)
            msg = "Removing '{}' from `{}`.".format(x, self.fname)
            bot_support.console_print(bot_support,msg,color='green',bold_text=True)
            self.save_list(items)

    def random(self):
        return random.choice(self.list)

    def remove_duplicates(self):
        return list(OrderedDict.fromkeys(self.list))

    def save_list(self, items):
        with open(self.fname, 'w') as f:
            for item in items:
                f.write('{item}\n'.format(item=item))

import time

from tqdm import tqdm
from app.models.igaccounts import igaccounts as igaccounts_model
from app.models.igtotal import igtotal as igtotal_model
from core.functions import functions


def follow(self, user_id,force=False,hashtag='',progress=None):
    user_id = self.convert_to_user_id(user_id)
    user_info = self.get_user_info(user_id)
    username = user_info["username"]
    self.console_print('===> Going to Follow `user_id`: {} with username: {}'.format(user_id, username),progress=progress)
    error_check=False
    if not self.check_user(user_id):
        if not force: 
            return False
        else:
            error_check=True
    if force or not self.reached_limit('follows'):
        self.delay('follow')
        response=self.api.follow(user_id)
        if isinstance(response,bool) and response:
            self.total['follows'] += 1
            igtotal_model.set_total('follows',functions.current_time('%Y-%m-%d'),1)
            self.followed_file.append(user_id)
            msg = '===> FOLLOWED <==== `user_id`: {}. Total: {}/{}'.format(user_id,self.total['follows'],self.max_per_day['follows'])
            self.console_print(msg, 'green')
            
            if user_id not in self.following:
                self.following.append(user_id)
            
            if not error_check:
                data={'id':user_info[0],'following':True}
            else:
                data={'id':user_info[0],'following':False}
            if hashtag!='':
                data['hashtag']=hashtag
            igaccounts_model.update(data,False)
            
            return True
        else:
            return False
    else:
        self.console_print("Out of follows for today.")
    return False


def follow_users(self, user_ids,base=0,proporcion=1,hashtag=''):
    broken_items = []
    if self.reached_limit('follows'):
        self.console_print("Out of follows for today.")
        return
    skipped = self.skipped_file
    followed = self.followed_file
    unfollowed = self.unfollowed_file

    # Remove skipped and already followed and unfollowed list from user_ids
    #following=igaccounts_model.getAll(select='pk')
    #following=(f['pk'] for f in following)
    #user_ids = list(set(user_ids) - skipped.set - followed.set - unfollowed.set - set(following))
    user_ids = list(set(user_ids) - skipped.set - followed.set - unfollowed.set)


    msg = 'After filtering followed, unfollowed and `{}`, {} user_ids left to follow.'
    msg = msg.format(skipped.fname, len(user_ids))
    self.console_print(msg, 'green')
    count=0
    #for user_id in tqdm(user_ids, desc='Processed users'):
    for user_id in user_ids:
        count+=1
        if self.reached_limit('follows'):
            self.console_print("Out of follows for today.")
            break
        #self.console_print(user_id,progress=base+(count/len(user_ids))*proporcion)
        if not self.follow(user_id,hashtag=hashtag,progress=base+(count/len(user_ids))*proporcion):
            if self.api.fatal_error:
                i = user_ids.index(user_id)
                broken_items += user_ids[i-1:]
                break

            if self.api.last_response.status_code == 404:
                self.console_print("404 error user {user_id} doesn't exist.", 'red')
                broken_items.append(user_id)

            elif self.api.last_response.status_code == 200:
                broken_items.append(user_id)

            elif self.api.last_response.status_code not in (400, 429):
                # 400 (block to follow) and 429 (many request error)
                # which is like the 500 error.
                try_number = 3
                error_pass = False
                for _ in range(try_number):
                    time.sleep(60)
                    error_pass = self.follow(user_id)
                    if error_pass:
                        break
                if not error_pass:
                    self.error_delay()
                    i = user_ids.index(user_id)
                    broken_items += user_ids[i:]
                    break

    self.console_print("DONE: Now following {} users in total.".format(self.total['follows']))
    return broken_items


def follow_followers(self, user_id, nfollows=None):
    self.console_print("Follow followers of: {}".format(user_id))
    if self.reached_limit('follows'):
        self.console_print("Out of follows for today.")
        return
    if not user_id:
        self.console_print("User not found.")
        return
    followers = self.get_user_followers(user_id, nfollows)
    followers = list(set(followers) - set(self.blacklist))
    if not followers:
        self.console_print("{} not found / closed / has no followers.".format(user_id))
    else:
        self.follow_users(followers[:nfollows])


def follow_following(self, user_id, nfollows=None):
    self.console_print("Follow following of: {}".format(user_id))
    if self.reached_limit('follows'):
        self.console_print("Out of follows for today.")
        return
    if not user_id:
        self.console_print("User not found.")
        return
    followings = self.get_user_following(user_id)
    if not followings:
        self.console_print("{} not found / closed / has no following.".format(user_id))
    else:
        self.follow_users(followings[:nfollows])

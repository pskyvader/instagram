from tqdm import tqdm
from app.models.igaccounts import igaccounts as igaccounts_model
from app.models.igtotal import igtotal as igtotal_model
from core.functions import functions


def unfollow(self, user_id,progress=None):
    user_id = self.convert_to_user_id(user_id)
    user_info = self.get_user_info(user_id)
    username = user_info["username"]
    #msg='===> Going to unfollow `user_id`: {} with username: {}'.format(user_id, username)
    #self.console_print(msg,progress=progress)
    if self.check_user(user_id, unfollowing=True):
        data={'id':user_info[0],'following':True}
        igaccounts_model.update(data,False)
        return True  # whitelisted user
    if not self.reached_limit('unfollows'):
        self.delay('unfollow')
        response=self.api.unfollow(user_id)
        if isinstance(response,bool) and response:
            self.unfollowed_file.append(user_id,show_message=False)
            self.total['unfollows'] += 1
            igtotal_model.set_total('unfollows',functions.current_time('%Y-%m-%d'),1)
            msg = '===> Unfollowed, `user_id`: {}, user_name: {}. Total: {}/{}'.format(user_id, username,self.total['unfollows'],self.max_per_day['unfollows'])
            self.console_print(msg, 'green')

            if user_id in self.following:
                self.following.remove(user_id)
            data={'id':user_info[0],'following':False}
            igaccounts_model.update(data,False)
            
            if not self.reset['unfollow']:
                self.reset_turn('unfollow')
                self.reset['unfollow']=True
                
            return True
        else:
            return False
    else:
        self.console_print("Out of unfollows for today.")
    return False


def unfollow_users(self, user_ids):
    broken_items = []
    self.logger.info("Going to unfollow {} users.".format(len(user_ids)))
    user_ids = set(map(str, user_ids))
    filtered_user_ids = list(set(user_ids) - set(self.whitelist))
    if len(filtered_user_ids) != len(user_ids):
        self.logger.info(
            "After filtration by whitelist {} users left.".format(
                len(filtered_user_ids)
            )
        )
    for user_id in tqdm(filtered_user_ids, desc="Processed users"):
        if not self.unfollow(user_id):
            self.error_delay()
            i = filtered_user_ids.index(user_id)
            broken_items = filtered_user_ids[i:]
            break
    self.logger.info("DONE: Total unfollowed {} users.".format(self.total["unfollows"]))
    return broken_items


def unfollow_non_followers(self, n_to_unfollows=None):
    self.logger.info("Unfollowing non-followers.")
    self.console_print(" ===> Start unfollowing non-followers <===", "red")
    non_followers = set(self.following) - set(self.followers) - self.friends_file.set
    non_followers = list(non_followers)
    for user_id in tqdm(non_followers[:n_to_unfollows]):
        if self.reached_limit("unfollows"):
            self.logger.info("Out of unfollows for today.")
            break
        self.unfollow(user_id)
    self.console_print(" ===> Unfollow non-followers done! <===", "red")


def unfollow_everyone(self):
    self.unfollow_users(self.following)
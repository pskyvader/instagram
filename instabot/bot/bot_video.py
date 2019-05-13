
def upload_video(self, video, caption=''):
    self.small_delay()
    self.console_print("Started uploading '{video}'".format(video=video))
    if not self.api.upload_video(video, caption):
        self.console_print("Video '%s' is not %s ." % (video, 'uploaded'))
        return False
    self.console_print("Video '{video}' uploaded".format(video=video))
    return True

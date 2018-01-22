from machine.singletons import Slack, Scheduler


class MessagingClient:
    @property
    def users(self):
        return Slack.get_instance().server.users

    @property
    def channels(self):
        return Slack.get_instance().server.channels

    def retrieve_bot_info(self):
        return Slack.get_instance().server.login_data['self']

    def fmt_mention(self, user):
        u = self.users.find(user)
        return "<@{}>".format(u.id)

    def send(self, channel, text, thread_ts=None):
        Slack.get_instance().rtm_send_message(channel, text, thread_ts)

    def send_scheduled(self, when, channel, text):
        args = [self, channel, text]
        kwargs = {'thread_ts': None}

        Scheduler.get_instance().add_job(MessagingClient.send, trigger='date', args=args,
                                         kwargs=kwargs, run_date=when)

    def send_webapi(self, channel, text, attachments=None, thread_ts=None, ephemeral_user=None):
        method = 'chat.postMessage'

        # This is the only way to conditionally add thread_ts
        kwargs = {
            'channel': channel,
            'text': text,
            'attachments': attachments,
            'as_user': True
        }

        if ephemeral_user:
            method = 'chat.postEphemeral'
            kwargs['user'] = ephemeral_user
        else:
            if thread_ts:
                kwargs['thread_ts'] = thread_ts

        return Slack.get_instance().api_call(
            method,
            **kwargs
        )

    def send_webapi_scheduled(self, when, channel, text, attachments=None, ephemeral_user=None):
        args = [self, channel, text]
        kwargs = {
            'attachments': attachments,
            'thread_ts': None,
            'ephemeral_user': ephemeral_user
        }

        Scheduler.get_instance().add_job(MessagingClient.send_webapi, trigger='date', args=args,
                                         kwargs=kwargs, run_date=when)

    def react(self, channel, ts, emoji):
        return Slack.get_instance().api_call(
            'reactions.add',
            name=emoji,
            channel=channel,
            timestamp=ts
        )

    def open_im(self, user):
        response = Slack.get_instance().api_call(
            'im.open',
            user=user
        )

        return response['channel']['id']

    def send_dm(self, user, text):
        u = self.users.find(user)
        dm_channel = self.open_im(u.id)

        self.send(dm_channel, text)

    def send_dm_scheduled(self, when, user, text):
        args = [self, user, text]
        Scheduler.get_instance().add_job(MessagingClient.send_dm, trigger='date', args=args,
                                         run_date=when)

    def send_dm_webapi(self, user, text, attachments=None):
        u = self.users.find(user)
        dm_channel = self.open_im(u.id)

        return Slack.get_instance().api_call(
            'chat.postMessage',
            channel=dm_channel,
            text=text,
            attachments=attachments,
            as_user=True
        )

    def send_dm_webapi_scheduled(self, when, user, text, attachments=None):
        args = [self, user, text]
        kwargs = {'attachments': attachments}

        Scheduler.get_instance().add_job(MessagingClient.send_dm_webapi, trigger='data', args=args,
                                         kwargs=kwargs)

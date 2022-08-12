# Async mode

As of v0.26.0 Slack Machine supports AsyncIO using the
[Slack Events API](https://api.slack.com/apis/connections/events-api) and
[Socket Mode](https://api.slack.com/apis/connections/socket). This is still experimental and should be thoroughly
tested. The goal is to eventually stop supporting the old version that uses the Slack RTM API, as the Events API is
recommended by Slack for must use cases and asyncio has the potential to be much more performant.

All the asyncio code is in the `machine.asyncio` package.

## How to start using it

With the advent of asyncio in Slack Machine, we're also moving towards using **Slack Apps** instead of legacy bot
tokens. This means that you'll need to create a new app in Slack and get an app token and a bot token for it:

1. Create a new app in Slack: <https://api.slack.com/apps>
2. Choose to create an app from an _App manifest_
3. Copy/paste the following manifest:

    ``` title="manifest.yaml"
    --8<-- "docs/extra/manifest.yaml"
    ```

4. Add the Slack API token to your `local_settings.py` like this:

    ``` title="local_settings.py"
    SLACK_APP_TOKEN = "xapp-my-app-token"
    SLACK_BOT_TOKEN = "xoxb-my-bot-token"
    ```

5. Start the bot with `slack-machine-async`
6. ...
7. Profit!

## Choosing storage

Async mode uses different storage backend then the old sync mode. The following 2 backends are available:

- `machine.asyncio.storage.backends.memory.MemoryStorage`
- `machine.asyncio.storage.backends.memory.RedisStorage`

## Plugin API and usage

To support asyncio, the plugin API is slightly different. All user-defined plugin methods (the methods that are
marked with the plugin [decorators][decorators]) should now be defined as `async def`. And all
[builtin plugin][machine.asyncio.plugins.base.MachineBasePlugin] methods are async as well.

This also means that the builtin plugins have async versions:

- `machine.asyncio.plugins.builtin.general.HelloPlugin`,
- `machine.asyncio.plugins.builtin.general.PingPongPlugin`,
- `machine.asyncio.plugins.builtin.help.HelpPlugin`,
- `machine.asyncio.plugins.builtin.fun.images.ImageSearchPlugin`,
- `machine.asyncio.plugins.builtin.fun.memes.MemePlugin`,
- `machine.asyncio.plugins.builtin.admin.RBACPlugin`

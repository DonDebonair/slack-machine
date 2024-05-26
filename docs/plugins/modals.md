# Modals

In Slack, [modals](https://api.slack.com/surfaces/modals) are a way to ask users for input or display information in a
dialog/popup-like form. Modals are a great way to collect information from users, display information, or confirm an
action.

Modals can only be triggered by [actions the user takes](https://api.slack.com/interactivity#user). The most
common types of user actions that can trigger a modal are:

- Shortcuts
- [Slash Commands][slash-commands]
- [Block Kit interative components][block-kit-actions]

For each of these actions, Slack provides a `trigger_id` which can be used to open a modal. **This needs to be done
within 3 seconds of receiving the `trigger_id`**. Slack Machine abstracts most of this away for you and lets you
open modals from Slash Commands and Block Kit actions without having to worry about the `trigger_id`.

## Defining and opening modals

When you want to open a modal, you first need to define the
[_view_](https://api.slack.com/surfaces/modals#composing_views) with the content you want to show. This view has
some additional properties that define how the modal should behave. One important property is the `callback_id` which
is used to identify the modal when it is submitted or closed.

You can define a modal view in 2 ways:

- As a [dict][] that conforms to the [View schema](https://api.slack.com/reference/surfaces/views#modal)
- By constructing a [View](https://tools.slack.dev/python-slack-sdk/api-docs/slack_sdk/models/views/index.html#slack_sdk.models.views.View)
  object from the Slack SDK for Python

When you have defined the view, you can open the modal by calling the `open_modal` method on the
[`Command`][machine.plugins.command.Command] object that is passed to your Slash Command handler or on the
[`BlockAction`][machine.plugins.block_action.BlockAction] object that is passed to your Block Kit action handler.

## Listening for modal interactions

Once a modal is opened, the user can interact with the block kit elements within the modal, such as buttons, input
fields, datepickers etc. When the user interacts with these elements, a [block kit action](block-kit-actions.md) can be
triggered which lets you deal with input.

Additionally, when the user _submits_ the modal, this triggers a `view_submission` event that you can listen to with
the [`@modal`][machine.plugins.decorators.modal] decorator. This decorator takes a `callback_id` as
an argument, which is used to identify the modal that was submitted. The `callback_id` can be a [`str`][str] or a
[`re.Pattern`][re.Pattern]. When a string is provided, the handler only fires upon an exact match, whereas with a regex
pattern, you can have the handler fired for multiple matching `callback_id`s. This is convenient when you want one
handler to process multiple modals, for example.

Unless you want to listen for changes to specific input fields - for example to update the modal in-place - it's
probably easiest to use the `@modal` decorator and process the entire input upon modal submission.

### The modal handler function

The handler function will be called with a
[`ModalSubmission`][machine.plugins.modals.ModalSubmission] object that contains useful information about the
modal that was submitted and the user that submitted it. The `ModalSubmission` object has a property
[`view`][machine.plugins.modals.ModalSubmission.view] that contains the complete view that was submitted, including the
state of the input fields of the modal. The object also has a [`user`][machine.plugins.modals.ModalSubmission.user]
property that corresponds to the user that submitted the modal.

You can optionally add the `logger` argument to your handler get a
[logger that was enriched by Slack Machine](misc.md#using-loggers-provided-by-slack-machine-in-your-handler-functions)

The `ModalSubmission` contains methods for
[updating the current modal view][machine.plugins.modals.ModalSubmission.update_modal],
[pushing a new view on top of the current one][machine.plugins.modals.ModalSubmission.push_modal] or even
[opening a completely new modal][machine.plugins.modals.ModalSubmission.open_modal].

You can also send a message to the user that submitted the modal with the
[`send_dm`][machine.plugins.modals.ModalSubmission.send_dm] method.

The modal handler function can be defined as a regular `async` function or a generator. When you define it as a
generator, you can use the `yield` statement to:

- [Update the modal view in-place](https://api.slack.com/surfaces/modals#updating_response)
- [Push a new view on top of the current one](https://api.slack.com/surfaces/modals#add_response)
- [Close the current view](https://api.slack.com/surfaces/modals#close_current_view) (which is the default behavior when
  nothing is yielded)
- [Close all the views on the stack](https://api.slack.com/surfaces/modals#close_all_views)
- [Display errors in the modal](https://api.slack.com/surfaces/modals#displaying_errors), which is useful when you want
  to show validation errors to the user.

!!! warning

    You must yield a response to Slack within 3 seconds of receiving the `view_submission` event. If you don't, Slack
    will show an error to the user.


## Listening for modal closures

Sometimes you want to know when a user closes a modal without submitting it. This can be useful to clean up
resources or store the state of the modal for later continuation. You can listen for modal closures with the
[`@modal_closed`][machine.plugins.decorators.modal_closed] decorator. This decorator takes a `callback_id` as parameter
and works the same way as the `@modal` decorator.

The handler function will be called with a
[`ModalClosure`][machine.plugins.modals.ModalClosure] object that contains information about the modal that was
closed. Just like the `ModalSubmission` object, the `ModalClosure` object has a
[`view`][machine.plugins.modals.ModalSubmission.view] property that contains the complete view of the modal that was
closed, including the state of the input fields. The object also has a
[`user`][machine.plugins.modals.ModalClosure.user] property that corresponds to the user that submitted the
modal.

You can send a message to the user that submitted the modal with the
[`send_dm`][machine.plugins.modals.ModalClosure.send_dm] method.

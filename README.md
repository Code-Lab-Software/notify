Notify allows you to register the Django build-in signals with the custom e-mail message template.
Once the template is registered, the signal event will trigger the message to be send.


Post-save
------
To register `post-save` message, create the `notify.models.PostSaveMessageType`
subclass, provide the `RECEIVERS` list (i.e. a list of names of the groups, that
will be configured to receive an e-mail) and the `SENDERS` list (only listed models postsaves will
trigger notifications).

The simplest message config is:

```python
from notify.models import PostSaveMessageType
class SomeMessageConfig(PostSaveMessageType):
    RECEIVERS = {'receiver_a': 'create', 'receiver_b': 'update', 'receiver_c': 'any'}
    SENDERS = ('app.ModelA', 'app.ModelB')
    SUBJECT_TPL = "Email subject - use {{ instance }}"
    BODY_TPL = "Email body - you can also use {{ instance }} here"
				
    class Receivers:
         def get_receiver_a_emails(self, instance):
             # Some logic here...
             return ['some_email@example.org']

        def get_receiver_b_emails(self, instance)
            # Some logic here...
            return ['another_email@other.domain.com', 'a_second_email@other.com']
``` 

'notify' lets you handle dynamic subjects and body templates as well as
language specific messages. More details soon.


Other signals
------
The handlers for other build-in signals will be available some day. This is very
simple to implement, though -- so if you want to contribute... just fork this repo,
create the other signal handler and submit merge request!
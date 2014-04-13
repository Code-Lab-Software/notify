Notify allows you to register the Django build-in signals with the custom e-mail message template. Once the template is registered, it will be sent to a receivers groups.


Post-save
------
To register `post-save` message, create the `notify.PostSaveMessageType`
class, provide the `RECEIVERS` list (i.e. a list of names of the groups, that
can be configured to receive an e-mail during the `post-save` processing) and 
the `MODELS` list (only these models will be handled by this message template).

**When you're ready with the signal handler registration, `sync_db`, navigate to 
admin `notify` and configure the message template.**

```python
from notify.registry import PostSaveMessageType
class SomeMessageHandler(PostSaveMessageType):
    RECEIVERS = (('receiver_a', 'Receiver A verbose name'), ('receiver_b', 'Receiver B verbose name'))
    MODELS = (ModelA, ModelB)
				
    class Receivers:
         def get_receiver_a_emails(self, instance):
             # Some logic here...
             return ['some_email@example.org']

        def get_receiver_b_emails(self, instance)
            # Some logic here...
            return ['another_email@other.domain.com', 'a_second_email@other.com']
``` 

Other signals
------
The handlers for other build-in signals will be available some day. This is very
simple to implement, though -- so if you want to contribute... just fork this repo,
create the other signal handler and submit merge request!
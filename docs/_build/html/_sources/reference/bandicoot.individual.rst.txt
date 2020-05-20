individual
==========

This module  contains indicators from mobile phone usage and interactions with contacts.

.. currentmodule:: bandicoot.individual

.. autosummary::
   :toctree: generated/

   active_days
   number_of_contacts
   number_of_interactions
   call_duration
   percent_nocturnal
   percent_initiated_conversations
   percent_initiated_interactions
   response_delay_text
   response_rate_text
   entropy_of_contacts
   balance_of_contacts
   interactions_per_contact
   interevent_time
   percent_pareto_interactions
   percent_pareto_durations


.. _conversations-label:

Conversations
^^^^^^^^^^^^^

Some bandicoot indicators rely on texts being grouped into conversations. We define conversations as a series of text messages between the user and one contact. A conversation starts with either of the parties sending a text to the other. A conversation will stop if no text was exchanged by the parties for an hour or if one of the parties call the other. The next conversation will start as soon as a new text is send by either of the parties.

Example
-------

- At 10:00, Alice sends a message to Bob “*Where are you? I'm waiting at the train station. I have your ice cream.*”
- At 10:01, Bob responds with a text “*I'm running late, I should be there soon.*”
- At 10:05, Bob sends another message “*I missed my bus :(*”
- At 10:10, Alice calls Bob to tell him she eated the ice cream and took the train.

The first three text messages define a conversation between Alice and Bob, which is ended by the last call. The call is not included in the conversation.

The distribution of delays is *[60 seconds, 240 seconds]*. Bob's response rate is *1* as he responded to Alice's first message.


.. note::

   A conversation can be defined by just one text message. In this case, the response delay is ``None``.


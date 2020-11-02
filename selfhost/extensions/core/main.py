from extensions.core.events import CoreEvents
import logging


def extension_setup(client):
    client.add_cog(CoreEvents(client, logging.getLogger("Core Events")))

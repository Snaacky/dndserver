from dndserver.protos.Common import SC2S_META_LOCATION_REQ, SS2C_META_LOCATION_RES
from dndserver.persistent import sessions
from dndserver.handlers.party import send_party_location_notification


def process_location(ctx, msg):
    # get the location from the message.
    req = SC2S_META_LOCATION_REQ()
    req.ParseFromString(msg)

    # update the location
    sessions[ctx.transport].state.location = req.location

    # send the party the new location the user is in
    send_party_location_notification(sessions[ctx.transport].party, sessions[ctx.transport])

    # respond to the location request
    return SS2C_META_LOCATION_RES(location=req.location)

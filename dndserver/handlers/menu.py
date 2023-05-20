from dndserver.protos.Common import SC2S_META_LOCATION_REQ, SS2C_META_LOCATION_RES
from dndserver.persistent import sessions
from dndserver.handlers.party import get_party, send_party_location_notification


def process_location(ctx, msg) -> SS2C_META_LOCATION_RES:
    # get the location from the message.
    req = SC2S_META_LOCATION_REQ()
    req.ParseFromString(msg)

    # update the location
    sessions[ctx.transport].state.location = req.location

    # send the party the new location the user is in
    party = get_party(account_id=sessions[ctx.transport].account.id)
    send_party_location_notification(party, sessions[ctx.transport])

    # respond to the location request
    return SS2C_META_LOCATION_RES(location=req.location)

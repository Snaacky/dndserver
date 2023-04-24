
from dndserver.protos.Defines import Define_Common as common
from dndserver.protos.Common import SC2S_META_LOCATION_REQ, SS2C_META_LOCATION_RES

def process_location(ctx, msg):
    # get the location from the message.
    req = SC2S_META_LOCATION_REQ()

    # TODO: get a better way to get the actual size of the proto as it also has the 
    # size of the other packet. Currently hardcoded to 2 bytes
    req.ParseFromString(msg[:2])

    # check if we have more data than expected for the proto
    if (len(msg) > 2):
        # process the other data as well
        ctx.dataReceived(msg[2:])

    # respond to the location request
    return SS2C_META_LOCATION_RES(location=req.location)
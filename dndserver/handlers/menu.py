
from dndserver.protos.Defines import Define_Common as common
from dndserver.protos.Common import SC2S_META_LOCATION_REQ, SS2C_META_LOCATION_RES

def process_location(ctx, msg):
    # get the location from the message.
    req = SC2S_META_LOCATION_REQ()

    # get the location from the string
    req.ParseFromString(msg)

    # respond to the location request
    return SS2C_META_LOCATION_RES(location=req.location)
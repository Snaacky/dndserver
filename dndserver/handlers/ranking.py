import random

from dndserver.protos.Character import SACCOUNT_NICKNAME
from dndserver.protos.Ranking import SRankRecord, SC2S_RANKING_RANGE_REQ, SS2C_RANKING_RANGE_RES


def get_ranking(ctx, msg):
    # message SC2S_RANKING_RANGE_REQ {
    #   uint32 rankType = 1;
    #   uint32 startIndex = 2;
    #   uint32 endIndex = 3;
    #   string characterClass = 4;
    # }

    req = SC2S_RANKING_RANGE_REQ()
    req.ParseFromString(msg)

    # message SS2C_RANKING_RANGE_RES {
    #   uint32 result = 1;
    #   repeated .DC.Packet.SRankRecord records = 2;
    #   uint32 rankType = 3;
    #   uint32 allRowCount = 4;
    #   uint32 startIndex = 5;
    #   uint32 endIndex = 6;
    #   string characterClass = 7;
    # }
    res = SS2C_RANKING_RANGE_RES(result=1, rankType=1, allRowCount=1, startIndex=1, endIndex=1, characterClass="")

    # message SRankRecord {
    #   uint32 pageIndex = 1;
    #   uint32 rank = 2;
    #   uint32 score = 3;
    #   float percentage = 4;
    #   string accountId = 5;
    #   .DC.Packet.SACCOUNT_NICKNAME nickName = 6;
    #   string characterClass = 7;
    # }

    record = SRankRecord(
        pageIndex=1,
        rank=1,
        score=1,
        percentage=1.0,
        accountId=1,
        nickName=SACCOUNT_NICKNAME(
            originalNickName="Test",
            streamingModeNickName=f"Fighter#{random.randrange(1000000, 1700000)}"
        )
    )
    res.records.CopyFrom(record)

    return res

import random

from loguru import logger

from dndserver.protos import _Character_pb2 as char, Ranking_pb2 as rank


def get_ranking(ctx, req):
    # message SC2S_RANKING_RANGE_REQ {
    #   uint32 rankType = 1;
    #   uint32 startIndex = 2;
    #   uint32 endIndex = 3;
    #   string characterClass = 4;
    # }

    # message SS2C_RANKING_RANGE_RES {
    #   uint32 result = 1;
    #   repeated .DC.Packet.SRankRecord records = 2;
    #   uint32 rankType = 3;
    #   uint32 allRowCount = 4;
    #   uint32 startIndex = 5;
    #   uint32 endIndex = 6;
    #   string characterClass = 7;
    # }

    logger.debug(req)
    res = rank.SS2C_RANKING_RANGE_RES()
    res.result = 1
    res.rankType = 1
    res.allRowCount = 1
    res.startIndex = 1
    res.endIndex = 1
    res.characterClass = ""
    
    record = rank.SRankRecord()
    # message SRankRecord {
    #   uint32 pageIndex = 1;
    #   uint32 rank = 2;
    #   uint32 score = 3;
    #   float percentage = 4;
    #   string accountId = 5;
    #   .DC.Packet.SACCOUNT_NICKNAME nickName = 6;
    #   string characterClass = 7;
    # }
    record.pageIndex = 1
    record.rank = 1
    record.score = 1
    record.percentage = 1.0
    record.accountId = 1

    nickname = char.SACCOUNT_NICKNAME()
    nickname.originalNickName = "Test"
    nickname.streamingModeNickName = f"Fighter#{random.randrange(1000000, 1700000)}"

    record.nickName.CopyFrom(nickname)
    res.records.CopyFrom(record)

    return res

import random

from dndserver.database import db
from dndserver.models import Character
from dndserver.protos.Character import SACCOUNT_NICKNAME
from dndserver.protos.Ranking import SRankRecord, SC2S_RANKING_RANGE_REQ, SS2C_RANKING_RANGE_RES, RANKING_TYPE
from dndserver.protos import PacketCommand as pc


def get_ranking(ctx, msg):
    """Occurs when the user opens the leaderboards."""
    req = SC2S_RANKING_RANGE_REQ()
    req.ParseFromString(msg)

    # TODO: implement some caching so the database is not hit every time a user requests the rankings
    if req.rankType == RANKING_TYPE.COIN:
        query = db.query(Character).order_by(Character.ranking_coin.desc())
    elif req.rankType == RANKING_TYPE.KILL:
        query = db.query(Character).order_by(Character.ranking_kill.desc())
    elif req.rankType == RANKING_TYPE.ESCAPE:
        query = db.query(Character).order_by(Character.ranking_escape.desc())
    elif req.rankType == RANKING_TYPE.ADVENTURE:
        query = db.query(Character).order_by(Character.ranking_adventure.desc())
    elif req.rankType == RANKING_TYPE.BOSSKILL_LICH:
        query = db.query(Character).order_by(Character.ranking_lich.desc())
    elif req.rankType == RANKING_TYPE.BOSSKILL_GHOSTKING:
        query = db.query(Character).order_by(Character.ranking_ghostking.desc())
    else:
        # we dont know this type. Give a error
        return SS2C_RANKING_RANGE_RES(result=pc.FAIL_NO_VALUE)

    res = SS2C_RANKING_RANGE_RES()
    res.result = pc.SUCCESS
    res.rankType = req.rankType
    res.startIndex = req.startIndex
    res.endIndex = req.endIndex
    res.characterClass = ""
    res.allRowCount = query.count()

    for index, (character, _) in enumerate(zip(query, range(min(query.count(), req.endIndex)))):
        if req.rankType == RANKING_TYPE.COIN:
            score = character.ranking_coin
        elif req.rankType == RANKING_TYPE.KILL:
            score = character.ranking_kill
        elif req.rankType == RANKING_TYPE.ESCAPE:
            score = character.ranking_escape
        elif req.rankType == RANKING_TYPE.ADVENTURE:
            score = character.ranking_adventure
        elif req.rankType == RANKING_TYPE.BOSSKILL_LICH:
            score = character.ranking_lich
        elif req.rankType == RANKING_TYPE.BOSSKILL_GHOSTKING:
            score = character.ranking_ghostking

        if score == 0:
            # if the score is 0 we do not show it. As the query is sorted on decending order
            # the next items are also zero and we can exit
            return res

        record = SRankRecord()
        record.score = score

        record.percentage = 1.0
        record.accountId = str(character.user_id)
        record.pageIndex = index
        record.rank = index + 1

        nickname = SACCOUNT_NICKNAME(
            originalNickName=character.nickname, streamingModeNickName=f"Fighter#{random.randrange(1000000, 1700000)}"
        )

        record.nickName.CopyFrom(nickname)

        res.records.extend([record])

    return res

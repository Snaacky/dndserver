from dndserver.database import db
from dndserver.models import Character
from dndserver.protos.Character import SACCOUNT_NICKNAME
from dndserver.protos.Ranking import (
    SRankRecord,
    SC2S_RANKING_RANGE_REQ,
    SS2C_RANKING_RANGE_RES,
    RANKING_TYPE,
    SC2S_RANKING_CHARACTER_REQ,
    SS2C_RANKING_CHARACTER_RES,
)
from dndserver.protos import PacketCommand as pc
from dndserver.enums import CharacterClass
from dndserver.sessions import sessions


def get_character_ranking(ctx, msg):
    """Occurs when the user opens the leaderboards to view the rank in the leaderboard."""
    req = SC2S_RANKING_CHARACTER_REQ()
    req.ParseFromString(msg)

    res = SS2C_RANKING_CHARACTER_RES()
    res.result = pc.SUCCESS
    res.rankType = req.rankType
    res.allRowCount = 1
    res.characterClass = req.characterClass

    character = sessions[ctx.transport].character

    # TODO: get the acctual ranking of the character (for now set everything
    # to 0 to hide the user)
    record = SRankRecord()
    record.score = 0
    record.percentage = 0
    record.accountId = str(character.account_id)
    record.pageIndex = 0
    record.rank = 0
    record.characterClass = req.characterClass
    nickname = SACCOUNT_NICKNAME(
        originalNickName=character.nickname, streamingModeNickName=character.streaming_nickname
    )
    record.nickName.CopyFrom(nickname)

    res.rankRecord.CopyFrom(record)
    return res


def get_ranking(ctx, msg):
    """Occurs when the user opens the leaderboards."""
    req = SC2S_RANKING_RANGE_REQ()
    req.ParseFromString(msg)

    query = db.query(Character)

    # check if we need to update the query
    if CharacterClass(req.characterClass) != CharacterClass.NONE:
        query = query.filter_by(character_class=CharacterClass(req.characterClass))

    # TODO: implement some caching so the database is not hit every time a user requests the rankings
    if req.rankType == RANKING_TYPE.COIN:
        query = query.order_by(Character.ranking_coin.desc())
    elif req.rankType == RANKING_TYPE.KILL:
        query = query.order_by(Character.ranking_kill.desc())
    elif req.rankType == RANKING_TYPE.ESCAPE:
        query = query.order_by(Character.ranking_escape.desc())
    elif req.rankType == RANKING_TYPE.ADVENTURE:
        query = query.order_by(Character.ranking_adventure.desc())
    elif req.rankType == RANKING_TYPE.BOSSKILL_LICH:
        query = query.order_by(Character.ranking_lich.desc())
    elif req.rankType == RANKING_TYPE.BOSSKILL_GHOSTKING:
        query = query.order_by(Character.ranking_ghostking.desc())
    else:
        # we dont know this type. Give a error
        return SS2C_RANKING_RANGE_RES(result=pc.FAIL_NO_VALUE)

    res = SS2C_RANKING_RANGE_RES()
    res.result = pc.SUCCESS if query.count() else pc.FAIL_NO_VALUE
    res.rankType = req.rankType
    res.startIndex = req.startIndex
    res.endIndex = min(query.count(), req.endIndex)
    res.characterClass = req.characterClass
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
        record.accountId = str(character.account_id)
        record.pageIndex = index
        record.rank = index + 1
        record.characterClass = CharacterClass(character.character_class).value

        nickname = SACCOUNT_NICKNAME(
            originalNickName=character.nickname,
            streamingModeNickName=character.streaming_nickname,
        )

        record.nickName.CopyFrom(nickname)

        res.records.extend([record])

    return res

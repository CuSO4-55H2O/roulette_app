from peewee import *
from playhouse.pool import PooledMySQLDatabase
import datetime
import os

MYSQL_HOST = os.getenv("MYSQL_HOST",'db')
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "roulette_db")

db = PooledMySQLDatabase(
    MYSQL_DATABASE,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    max_connections=20,
    stale_timeout=300,
)


class BaseModel(Model):
    class Meta:
        database = db


#表1：对局表(Match)
class Match(BaseModel):
    group_id = BigIntegerField()
    start_time = DateTimeField(default=datetime.datetime.now)  # 开局时间
    end_time = DateTimeField(null=True)  #结束时间
    mode_flags = TextField()
    winner_id = BigIntegerField(null=True)  #最终赢家的QQ号


#表2：玩家信息表(MatchPlayer)
class MatchPlayer(BaseModel):
    match = ForeignKeyField(Match, backref='players')  #关联到对局
    user_id = BigIntegerField()  #玩家QQ号
    seat_index = IntegerField()  #0=先手(P0),1=后手(P1)
    coin_change = IntegerField(default=0)


#表3：对局流水表(MatchEvent)
class MatchEvent(BaseModel):
    match = ForeignKeyField(Match, backref='events')
    turn_num = IntegerField()
    content = TextField()


def init_db():
    """初始化数据库表结构"""
    db.connect()
    db.create_tables([Match, MatchPlayer, MatchEvent], safe=True)
    db.close()
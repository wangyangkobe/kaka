from kaka import db
from sqlalchemy.sql import text

if __name__ == '__main__':   
    db.drop_all() 
    db.create_all()
    db.session.commit()
    db.engine.execute(text('ALTER table user CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci'))
    db.engine.execute(text('ALTER table user_machine CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci'))
    db.engine.execute(text('ALTER table shen_qing CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci'))
    db.engine.execute(text('ALTER table machine_usage CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci'))
    db.engine.execute(text('ALTER table machine CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci'))
    db.engine.execute(text('ALTER table address CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci'))
    db.engine.execute(text('ALTER table share CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci'))
    db.engine.execute(text('ALTER table comment CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci'))
    db.engine.execute(text('ALTER table hotpoint CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci'))
    print('create table finish!')

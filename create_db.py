from kaka import db
if __name__ == '__main__':   
    db.drop_all() 
    db.create_all()
    db.session.commit()
    print('create table finish!')
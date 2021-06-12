from stud_corner import create_app, db

app = create_app()

if __name__=="__main__":
    with app.app_context():
        db.create_all()
        db.session.commit()
    app.run()
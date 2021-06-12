from stud_corner import create_app, db

app = create_app()

if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run()


"""" To create a database we have to do all of these above except the if __name__=="__main__": """
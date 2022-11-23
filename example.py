# from crypt import methods
# from flask import Flask, render_template, request, redirect, url_for,flash
# from flask_sqlalchemy import SQLAlchemy

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.sqlite3'

# db = SQLAlchemy(app)
# class library(db.Model):
#    id = db.Column('library_id', db.Integer, primary_key = True)
#    name = db.Column(db.String(100))
#    city = db.Column(db.String(50))  

# def __init__(self, name, city):
#    self.name = name
#    self.city = city


# @app.route('/')
# def show_all():
#     return render_template('showAll.html', libraries = library.query.all())

# @app.route('/new', methods = ['GET', 'POST'])
# def new():
#    if request.method == 'POST':
#       if not request.form['name'] or not request.form['city'] :
#          flash('Please enter all the fields', 'error')
#       else:
#          student = library(name=request.form['name'], city=request.form['city'])
         
#          db.session.add(student)
#          db.session.commit()
         
#          flash('Record was successfully added')
#          return redirect(url_for('show_all'))
#    return render_template('add.html')
    
    
# if __name__ == '__main__':
#     db.create_all()
#     app.run(debug=True)
#     app.run(host='127.0.0.1', port=3000)





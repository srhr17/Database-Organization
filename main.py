from time import sleep
from flask import Flask, render_template, request, redirect, url_for,flash,session
import mysql.connector
from datetime import date
import datetime

mydb=mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="Qwertyuiop@123",
    database="library",
    auth_plugin='mysql_native_password'
)
mycursor=mydb.cursor()

app = Flask(__name__)
app.secret_key = 'SRIHARI'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

@app.route('/',methods=['GET','POST'])
def index():
    # mycursor.execute("SHOW DATABASES")
    # for x in mycursor:
    #     print(x)
    # mycursor.close()
    if request.method == 'POST':
        details = request.form
        username = details['username']
        password = details['password']
        #verify the user against mysql database
        mycursor.execute("SELECT * FROM USERS WHERE email = %s AND password = %s", (username, password))
        account = mycursor.fetchone()
        if account==None:
            flash('Invalid username/password!')
            return redirect(url_for('index'))
        if account[-1]=="librarian":
            session['username'] = username
            session['role'] = "librarian"
            session['name'] = account[1]
            session['id'] = account[0]
            return redirect(url_for('librarian_home'))
        elif account[-1]=="member":
            session['username'] = username
            session['role'] = "member"
            session['name'] = account[1]
            session['id'] = account[0]
            return redirect(url_for('member_home'))
        else:
            flash('Invalid username/password!')
            return redirect(url_for('index'))
    else:
        return render_template('index.html')

@app.route('/add',methods=['GET','POST'])
def add():
    #sign up members
    if request.method == 'POST':
        details = request.form
        fname = details['firstname']
        lname = details['lastname']
        dob = details['dob']
        email = details['username']
        password = details['password']
        mycursor.execute("INSERT INTO USERS(firstName,lastName,email,memberSince,password,dob,typeOfUser) VALUES (%s,%s,%s,%s,%s,%s,'member')", (fname,lname, email,date.today(), password,dob))
        mydb.commit()
        session['username'] = email
        session['role'] = "member"
        session['name'] = fname
        mycursor.execute("SELECT * FROM USERS WHERE email = %s", (email,))
        account = mycursor.fetchone()
        session['id'] = account[0]
        return redirect(url_for('member_home'))
    else:
        return render_template('add.html')

@app.route('/librarian_home',methods=['GET'])
def librarian_home():
    #librarian home page
    if session['role']!="librarian":
        session.pop('username', None)
        session.pop('role', None)
        return redirect(url_for('index'))
    
    return render_template('librarian_home.html',username=session['name'])
    
@app.route('/member_home',methods=['GET'])
def member_home():
    #member home page
    if session['role']!="member":
        session.pop('username', None)
        session.pop('role', None)
        return redirect(url_for('index'))
    # mycursor.execute("SELECT * FROM BOOKS")
    # books=mycursor.fetchall()
    mycursor.execute("SELECT documentID,title,typeOfDocument,borrowDate FROM BORROW NATURAL JOIN DOCUMENTS NATURAL JOIN BOOKS WHERE userId = %s and status='1'", (session['id'],))
    books=mycursor.fetchall()
    mycursor.execute("SELECT documentID,title,typeOfDocument,borrowDate FROM BORROW NATURAL JOIN DOCUMENTS NATURAL JOIN ARTICLES WHERE userId = %s and status='1'", (session['id'],))
    articles=mycursor.fetchall()
    mycursor.execute("SELECT documentID,title,typeOfDocument,borrowDate FROM BORROW NATURAL JOIN DOCUMENTS NATURAL JOIN ISSUES WHERE userId = %s and status='1'", (session['id'],))
    issues=mycursor.fetchall()
    mycursor.execute("SELECT DISTINCT(documentID),title,typeOfDocument FROM BORROW NATURAL JOIN DOCUMENTS NATURAL JOIN BOOKS WHERE userID=%s and status='0' and availability='1'", (session['id'],))
    previousbooks=mycursor.fetchall()
    mycursor.execute("SELECT DISTINCT(documentID),title,typeOfDocument FROM BORROW NATURAL JOIN DOCUMENTS NATURAL JOIN ARTICLES WHERE userID=%s and status='0' and availability='1'", (session['id'],))
    previousarticles=mycursor.fetchall()
    mycursor.execute("SELECT DISTINCT(documentID),title,typeOfDocument FROM BORROW NATURAL JOIN DOCUMENTS NATURAL JOIN ISSUES WHERE userID=%s and status='0' and availability='1'", (session['id'],))
    previousissues=mycursor.fetchall()
    return render_template('member_home.html',username=session['name'],books=books,articles=articles,issues=issues,previousbooks=previousbooks,previousarticles=previousarticles,previousissues=previousissues)

@app.route('/logout',methods=['GET'])
def logout():
    #logout
    session.pop('username', None)
    session.pop('role', None)
    # mycursor.close()
    return redirect(url_for('index'))

@app.route('/add_book',methods=['GET','POST'])
def add_book():
    #add books
    if request.method == 'POST':
        details = request.form
        name = details['title']
        edition = details['edition']
        published_year = details['year']
        published_by = details['published_by']
        author = details['author']
        mycursor.execute("INSERT INTO DOCUMENTS(availability,typeOfDocument) VALUES (%s,%s)", (1,"book"))
        mydb.commit()
        mycursor.execute("SELECT documentID FROM DOCUMENTS ORDER BY documentID DESC LIMIT 1")
        document_id = mycursor.fetchone()[0]
        mycursor.execute("INSERT INTO BOOKS VALUES (%s,%s,%s,%s,%s)", (document_id, name, edition, published_year, published_by))
        # mycursor.execute("INSERT INTO AUTHORS VALUES (%s,%s)", (document_id, author))
        authors = author.split(",")
        for a in authors:
            mycursor.execute("INSERT INTO BOOKAUTHORS VALUES (%s,%s)", (document_id, a))
        mycursor.execute("INSERT INTO DOCUMENTADDMODIFY VALUES (%s,%s,%s)", ( session['id'],document_id, "add"))
        mydb.commit()
        return redirect(url_for('librarian_home'))
    else:
        mycursor.execute("SELECT TITLE FROM BOOKS")
        books=mycursor.fetchall()
        return render_template('add_book.html',books=books)

@app.route('/add_article',methods=['GET','POST'])
def add_article():
    #add articles
    if request.method == 'POST':
        details = request.form
        name = details['title']
        edition = details['edition']
        published_year = details['year']
        published_by = details['published_by']
        author = details['author']
        mycursor.execute("INSERT INTO DOCUMENTS(availability,typeOfDocument) VALUES (%s,%s)", (1,"article"))
        mydb.commit()
        mycursor.execute("SELECT documentID FROM DOCUMENTS ORDER BY documentID DESC LIMIT 1")
        document_id = mycursor.fetchone()[0]
        mycursor.execute("INSERT INTO ARTICLES(documentID,title,journalName,journalPublishedOn,journalPublishedBy) VALUES (%s,%s,%s,%s,%s)", (document_id, name, edition, published_year, published_by))
        # mycursor.execute("INSERT INTO AUTHORS VALUES (%s,%s)", (document_id, author))
        authors = author.split(",")
        for a in authors:
            mycursor.execute("INSERT INTO ARTICLEAUTHORS VALUES (%s,%s)", (document_id, a))
        mycursor.execute("INSERT INTO DOCUMENTADDMODIFY VALUES (%s,%s,%s)", ( session['id'],document_id, "add"))
        mydb.commit()
        return redirect(url_for('librarian_home'))
    else:
        mycursor.execute("SELECT TITLE FROM ARTICLES")
        articles=mycursor.fetchall()
        return render_template('add_article.html',articles=articles)

@app.route('/add_issue',methods=['GET','POST'])
def add_issue():
    #add journals
    if request.method == 'POST':
        details = request.form
        name = details['title']
        contributors = details['author']
        # edition = details['edition']
        published_year = details['year']
        published_by = details['published_by']
        mycursor.execute("INSERT INTO DOCUMENTS(availability,typeOfDocument) VALUES (%s,%s)", (1,"issue"))
        mydb.commit()
        mycursor.execute("SELECT documentID FROM DOCUMENTS ORDER BY documentID DESC LIMIT 1")
        document_id = mycursor.fetchone()[0]
        mycursor.execute("INSERT INTO ISSUES VALUES (%s,%s,%s,%s)", (document_id, name,  published_year, published_by))
        mycursor.execute("INSERT INTO DOCUMENTADDMODIFY VALUES (%s,%s,%s)", ( session['id'],document_id, "add"))
        for i in contributors.split(","):
            mycursor.execute("INSERT INTO ISSUECONTRIBUTOREDITOR VALUES (%s,%s)", (document_id, i))
        mydb.commit()
        return redirect(url_for('librarian_home'))
    else:
        mycursor.execute("SELECT title FROM ISSUES")
        issues=mycursor.fetchall()
        return render_template('add_issue.html',issues=issues)


#librarian will be able to view and modify the details of members
@app.route('/modify_member',methods=['GET','POST'])
def modify_member():
    if request.method == 'POST':
        details = request.form
        fname = details['fname']
        lname = details['lname']
        dob = details['dob']
        password = details['password']
        mycursor.execute("UPDATE USERS SET firstName=%s,lastName=%s,dob=%s,password=%s WHERE userID=%s", (fname,lname,dob,password,session['id']))
        mydb.commit()
        return redirect(url_for('librarian_home'))
    else:
        mycursor.execute("SELECT * FROM USERS WHERE userID=%s",(session['id'],))
        member=mycursor.fetchone()

        return render_template('modify_member.html',id=member[0],fname=member[1],lname=member[2],dob=member[6],password=member[5],memberSince=member[4])

#librarian will be able to delete the details of members
@app.route('/delete_member',methods=['GET','POST']) 
def delete_member():
    if session['role'] == 'librarian':
        if request.method == 'POST':
            details = request.form
            id = details['member_id']
            try:
                mycursor.execute("DELETE FROM USERS WHERE userID=%s and typeOfUser='member'",(id,))
                mydb.commit()
            except mysql.connector.Error as err:
                print("Something went wrong: {}".format(err))
                mycursor.execute("SELECT * FROM USERS WHERE typeOfUser='member'")
                members=mycursor.fetchall()
                return render_template('delete_member.html',error=str(err),members=members)
            return redirect(url_for('librarian_home'))
        else:
            mycursor.execute("SELECT * FROM USERS WHERE typeOfUser='member'")
            members=mycursor.fetchall()
            return render_template('delete_member.html',members=members)

#librarian will be able to view and modify the details of documents
# @app.route('/modify_document',methods=['GET','POST'])
# def modify_document():
    if request.method == 'POST':
        details = request.form
        typeOfDocument = details['typeOfDocument']
        if typeOfDocument=='Book':
            title = details['title']
            edition = details['edition']
            year = details['year']
            published_by = details['published_by']
            author = details['author']
            document_id = details['document_id']
            mycursor.execute("UPDATE BOOKS SET title=%s,edition=%s,year=%s,publishedBy=%s WHERE documentID=%s", (title,edition,year,published_by,document_id))
            mycursor.execute("DELETE FROM BOOKAUTHORS WHERE documentID=%s",(document_id,))
            authors = author.split(",")
            for a in authors:
                mycursor.execute("INSERT INTO BOOKAUTHORS VALUES (%s,%s)", (document_id, a))
            mycursor.execute("INSERT INTO DOCUMENTADDMODIFY VALUES (%s,%s,%s)", ( session['id'],document_id, "modify"))
            mydb.commit()
            return redirect(url_for('librarian_home'))
        elif typeOfDocument=='Article':
            title = details['title']
            edition = details['edition']
            year = details['year']
            published_by = details['published_by']
            author = details['author']
            document_id = details['document_id']
            mycursor.execute("UPDATE ARTICLES SET title=%s,journalName=%s,journalPublishedOn=%s,journalPublishedBy=%s WHERE documentID=%s", (title,edition,year,published_by,document_id))
            mycursor.execute("DELETE FROM ARTICLEAUTHORS WHERE documentID=%s",(document_id,))
            authors = author.split(",")
            for a in authors:
                mycursor.execute("INSERT INTO ARTICLEAUTHORS VALUES (%s,%s)", (document_id, a))
            mycursor.execute("INSERT INTO DOCUMENTADDMODIFY VALUES (%s,%s,%s)", ( session['id'],document_id, "modify"))
            mydb.commit()
            return redirect(url_for('librarian_home'))
        elif typeOfDocument=='Issue':
            title = details['title']
            year = details['year']
            published_by = details['published_by']
            document_id = details['document_id']
            mycursor.execute("UPDATE ISSUES SET title=%s,year=%s,publishedBy=%s WHERE documentID=%s", (title,year,published_by,document_id))
            mycursor.execute("INSERT INTO DOCUMENTADDMODIFY VALUES (%s,%s,%s)", ( session['id'],document_id, "modify"))
            mydb.commit()
            return redirect(url_for('librarian_home'))
        
    else:
        mycursor.execute("SELECT * FROM BOOKS WHERE documentID IN (SELECT documentID FROM DOCUMENTS WHERE typeOfDocument='book')")
        books=mycursor.fetchall()
        mycursor.execute("SELECT * FROM ARTICLES WHERE documentID IN (SELECT documentID FROM DOCUMENTS WHERE typeOfDocument='article')")
        articles=mycursor.fetchall()
        mycursor.execute("SELECT * FROM ISSUES WHERE documentID IN (SELECT documentID FROM DOCUMENTS WHERE typeOfDocument='issue')")
        issues=mycursor.fetchall()
        return render_template('modify_document.html',books=books,articles=articles,issues=issues)


#fix bugs
#users will be able to search for documents based on title, author, year, publisher and type of document, They should also view the details of the document.
@app.route('/search_document',methods=['GET','POST'])
def search_document():
    if session['role'] == 'member':
        if request.method == 'POST':
            details = request.form
            documenttype = details['documenttype']
            if documenttype=="0":
                title = details['booktitle']
                author = details['bookauthor']
                publisher = details['bookpublisher']
                edition = details['edition']
                if title!='':
                    title+="%"
                if author!='':
                    author+="%"
                if publisher!='':
                    publisher+="%"
                if title=='' and author=='' and publisher=='' and edition=='':
                    mycursor.execute("SELECT documentID,title,edition,publishedOn,publishedBy,authorName,IF(availability='1',1,0) as availability FROM BOOKS NATURAL JOIN BOOKAUTHORS NATURAL JOIN DOCUMENTS")
                else:
                    mycursor.execute("SELECT documentID,title,edition,publishedOn,publishedBy,authorName,IF(availability='1',1,0) as availability FROM BOOKS NATURAL JOIN BOOKAUTHORS NATURAL JOIN DOCUMENTS WHERE title LIKE %s or edition=%s or publishedBy LIKE %s or authorName LIKE %s",(title,edition,publisher,author))
                documents=mycursor.fetchall()
                return render_template('search_document.html',books=documents,a="selected")
            elif documenttype=="1":
                title = details['articletitle']
                author = details['articleauthor']
                journal = details['journal']
                publisher = details['journalpublisher']
                if title!='':
                    title+="%"
                if author!='':
                    author+="%"
                if journal!='':
                    journal+="%"
                if publisher!='':
                    publisher+="%"
                if title=='' and author=='' and journal=='' and publisher=='':
                    mycursor.execute("SELECT documentID,title,journalName,journalPublishedOn,journalPublishedBy,authorName,IF(availability='1',1,0) as availability FROM ARTICLES NATURAL JOIN ARTICLEAUTHORS NATURAL JOIN DOCUMENTS")
                else:
                    mycursor.execute("SELECT documentID,title,authorName,journalName,journalPublishedBy,IF(availability='1',1,0) as availability FROM ARTICLES NATURAL JOIN ARTICLEAUTHORS NATURAL JOIN DOCUMENTS WHERE title LIKE %s or journalName LIKE %s or journalPublishedBy LIKE %s or authorName LIKE %s",(title,journal,publisher,author))
                documents=mycursor.fetchall()
                return render_template('search_document.html',articles=documents,b="selected")
            elif documenttype=="2":
                title = details['issuetitle']
                contributor = details['issueauthor']
                magazine = details['magazine']
                issuefrom = details['issuefrom']
                issuetill = details['issuetill']
                if title!='':
                    title+="%"
                if contributor!='':
                    contributor+="%"
                if magazine!='':
                    magazine+="%"
                if title=='' and contributor=='' and magazine=='' and issuefrom=='' and issuetill=='':
                    mycursor.execute("SELECT documentID,title,contributorEditorName,magazineName,dateOfIssue,IF(availability='1',1,0) as availability FROM ISSUES NATURAL JOIN ISSUECONTRIBUTOREDITOR NATURAL JOIN DOCUMENTS")
                else:
                    mycursor.execute("SELECT documentID,title,contributorEditorName,magazineName,dateOfIssue,IF(availability='1',1,0) as availability FROM ISSUES NATURAL JOIN ISSUECONTRIBUTOREDITOR NATURAL JOIN DOCUMENTS WHERE title LIKE %s or contributorEditorName LIKE %s or magazineName LIKE %s or dateOfIssue BETWEEN %s and %s",(title,contributor,magazine,issuefrom,issuetill))
                documents=mycursor.fetchall()
                return render_template('search_document.html',issues=documents,c="selected")
        else:
            return render_template('search_document.html',a="selected")
    else:
        if request.method == 'POST':
            details = request.form
            documenttype = details['documenttype']
            if documenttype=="0":
                title = details['booktitle']
                author = details['bookauthor']
                publisher = details['bookpublisher']
                edition = details['edition']
                if title!='':
                    title+="%"
                if author!='':
                    author+="%"
                if publisher!='':
                    publisher+="%"
                if title=='' and author=='' and publisher=='' and edition=='':
                    mycursor.execute("SELECT documentID,title,edition,publishedOn,publishedBy,authorName,IF(availability='1',1,0) as availability FROM BOOKS NATURAL JOIN BOOKAUTHORS NATURAL JOIN DOCUMENTS")
                else:
                    mycursor.execute("SELECT documentID,title,edition,publishedOn,publishedBy,authorName,IF(availability='1',1,0) as availability FROM BOOKS NATURAL JOIN BOOKAUTHORS NATURAL JOIN DOCUMENTS WHERE title LIKE %s or edition=%s or publishedBy LIKE %s or authorName LIKE %s",(title,edition,publisher,author))
                documents=mycursor.fetchall()
                return render_template('search_document_lib.html',books=documents,a="selected")
            elif documenttype=="1":
                title = details['articletitle']
                author = details['articleauthor']
                journal = details['journal']
                publisher = details['journalpublisher']
                if title!='':
                    title+="%"
                if author!='':
                    author+="%"
                if journal!='':
                    journal+="%"
                if publisher!='':
                    publisher+="%"
                if title=='' and author=='' and journal=='' and publisher=='':
                    mycursor.execute("SELECT documentID,title,journalName,journalPublishedOn,journalPublishedBy,authorName,IF(availability='1',1,0) as availability FROM ARTICLES NATURAL JOIN ARTICLEAUTHORS NATURAL JOIN DOCUMENTS")
                else:
                    mycursor.execute("SELECT documentID,title,authorName,journalName,journalPublishedBy,IF(availability='1',1,0) as availability FROM ARTICLES NATURAL JOIN ARTICLEAUTHORS NATURAL JOIN DOCUMENTS WHERE title LIKE %s or journalName LIKE %s or journalPublishedBy LIKE %s or authorName LIKE %s",(title,journal,publisher,author))
                documents=mycursor.fetchall()
                return render_template('search_document_lib.html',articles=documents,b="selected")
            elif documenttype=="2":
                title = details['issuetitle']
                contributor = details['issueauthor']
                magazine = details['magazine']
                issuefrom = details['issuefrom']
                issuetill = details['issuetill']
                if title!='':
                    title+="%"
                if contributor!='':
                    contributor+="%"
                if magazine!='':
                    magazine+="%"
                if title=='' and contributor=='' and magazine=='' and issuefrom=='' and issuetill=='':
                    mycursor.execute("SELECT documentID,title,contributorEditorName,magazineName,dateOfIssue,IF(availability='1',1,0) as availability FROM ISSUES NATURAL JOIN ISSUECONTRIBUTOREDITOR NATURAL JOIN DOCUMENTS")
                else:
                    mycursor.execute("SELECT documentID,title,contributorEditorName,magazineName,dateOfIssue,IF(availability='1',1,0) as availability FROM ISSUES NATURAL JOIN ISSUECONTRIBUTOREDITOR NATURAL JOIN DOCUMENTS WHERE title LIKE %s or contributorEditorName LIKE %s or magazineName LIKE %s or dateOfIssue BETWEEN %s and %s",(title,contributor,magazine,issuefrom,issuetill))
                documents=mycursor.fetchall()
                return render_template('search_document_lib.html',issues=documents,c="selected")
        else:
            return render_template('search_document_lib.html',a="selected")


@app.route('/borrow_document',methods=['GET','POST'])
def borrow_document():
    if request.method == 'POST':
        details = request.form
        document_id = details['document_id']
        user_id = session['id']
        mycursor.execute("INSERT INTO BORROW(userID,documentID,borrowDate,status) VALUES (%s,%s,%s,%s)", (user_id,document_id,datetime.datetime.now(),1))
        mycursor.execute("UPDATE DOCUMENTS SET availability='0' WHERE documentID=%s",(document_id,))
        mydb.commit()
        return redirect(url_for('member_home'))
        
    else:
        mycursor.execute("SELECT * FROM BOOKS WHERE documentID IN (SELECT documentID FROM DOCUMENTS WHERE typeOfDocument='book' and availability='1')")
        books=mycursor.fetchall()
        mycursor.execute("SELECT * FROM ARTICLES WHERE documentID IN (SELECT documentID FROM DOCUMENTS WHERE typeOfDocument='article' and availability='1')")
        articles=mycursor.fetchall()
        mycursor.execute("SELECT * FROM ISSUES WHERE documentID IN (SELECT documentID FROM DOCUMENTS WHERE typeOfDocument='issue' and availability='1')")
        issues=mycursor.fetchall()
        return render_template('borrow_document.html',books=books,articles=articles,issues=issues)


@app.route('/return_document',methods=['GET','POST'])
def return_document():
    if request.method == 'POST':
        details = request.form
        document_id = details['document_id']
        user_id = session['id']
        mycursor.execute("UPDATE BORROW SET status='0' WHERE userID=%s AND documentID=%s",(user_id,document_id))
        mycursor.execute("UPDATE DOCUMENTS SET availability='1' WHERE documentID=%s",(document_id,))
        mydb.commit()
        return redirect(url_for('member_home'))

if __name__ == '__main__':
    app.run(debug=True)
    app.run(host='127.0.0.1', port=3000)
import os, sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB=os.path.join(BASE_DIR,"maslahatchi.db")
UPLOAD_DIR=os.path.join(BASE_DIR,"uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app=Flask(__name__)
app.secret_key=os.environ.get("SECRET_KEY","change-this-secret-key")
app.config["MAX_CONTENT_LENGTH"]=10*1024*1024
ALLOWED={"png","jpg","jpeg","webp","pdf"}

def db():
    con=sqlite3.connect(DB)
    con.row_factory=sqlite3.Row
    return con

def init_db():
    con=db()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS users(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS students(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      full_name TEXT NOT NULL,
      birth_date TEXT,
      class_name TEXT,
      address TEXT,
      pinfl TEXT,
      passport TEXT,
      father_name TEXT,
      father_phone TEXT,
      father_passport TEXT,
      mother_name TEXT,
      mother_phone TEXT,
      mother_passport TEXT,
      career_interest TEXT,
      notes TEXT,
      certificate_file TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    if not con.execute("SELECT 1 FROM users LIMIT 1").fetchone():
        con.execute("INSERT INTO users(username,password_hash) VALUES(?,?)",
                    ("admin",generate_password_hash("admin123")))
    con.commit(); con.close()

def login_required(f):
    @wraps(f)
    def wrapper(*a,**kw):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*a,**kw)
    return wrapper

def allowed_file(name):
    return "." in name and name.rsplit(".",1)[1].lower() in ALLOWED

init_db()

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form.get("username","").strip()
        password=request.form.get("password","")
        con=db(); user=con.execute("SELECT * FROM users WHERE username=?",(username,)).fetchone(); con.close()
        if user and check_password_hash(user["password_hash"],password):
            session.clear(); session["user_id"]=user["id"]; session["username"]=user["username"]
            return redirect(url_for("dashboard"))
        flash("Login yoki parol noto‘g‘ri.","danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def dashboard():
    con=db()
    total=con.execute("SELECT COUNT(*) c FROM students").fetchone()["c"]
    classes=con.execute("SELECT class_name,COUNT(*) c FROM students WHERE class_name<>'' GROUP BY class_name ORDER BY class_name").fetchall()
    recent=con.execute("SELECT * FROM students ORDER BY id DESC LIMIT 8").fetchall()
    con.close()
    return render_template("dashboard.html",total=total,classes=classes,recent=recent)

@app.route("/students")
@login_required
def students():
    q=request.args.get("q","").strip()
    con=db()
    if q:
        rows=con.execute("""SELECT * FROM students WHERE full_name LIKE ? OR class_name LIKE ? OR pinfl LIKE ? OR career_interest LIKE ? ORDER BY id DESC""",
                         (f"%{q}%",f"%{q}%",f"%{q}%",f"%{q}%")).fetchall()
    else:
        rows=con.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    con.close()
    return render_template("students.html",students=rows,q=q)

@app.route("/student/new",methods=["GET","POST"])
@login_required
def new_student():
    if request.method=="POST":
        data={k:request.form.get(k,"").strip() for k in [
            "full_name","birth_date","class_name","address","pinfl","passport",
            "father_name","father_phone","father_passport","mother_name","mother_phone",
            "mother_passport","career_interest","notes"]}
        if not data["full_name"]:
            flash("O‘quvchi F.I.Sh. majburiy.","danger")
            return render_template("student_form.html",student=data,title="O‘quvchi qo‘shish")
        filename=None
        f=request.files.get("certificate_file")
        if f and f.filename and allowed_file(f.filename):
            filename=secure_filename(f.filename)
            stem,ext=os.path.splitext(filename)
            i=1
            while os.path.exists(os.path.join(UPLOAD_DIR,filename)):
                filename=f"{stem}_{i}{ext}"; i+=1
            f.save(os.path.join(UPLOAD_DIR,filename))
        con=db()
        con.execute("""INSERT INTO students
        (full_name,birth_date,class_name,address,pinfl,passport,father_name,father_phone,father_passport,
         mother_name,mother_phone,mother_passport,career_interest,notes,certificate_file)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (*[data[k] for k in ["full_name","birth_date","class_name","address","pinfl","passport",
          "father_name","father_phone","father_passport","mother_name","mother_phone","mother_passport",
          "career_interest","notes"]],filename))
        con.commit(); con.close()
        flash("O‘quvchi muvaffaqiyatli saqlandi.","success")
        return redirect(url_for("students"))
    return render_template("student_form.html",student={},title="O‘quvchi qo‘shish")

@app.route("/student/<int:sid>/edit",methods=["GET","POST"])
@login_required
def edit_student(sid):
    con=db(); student=con.execute("SELECT * FROM students WHERE id=?",(sid,)).fetchone()
    if not student: con.close(); return "Topilmadi",404
    if request.method=="POST":
        keys=["full_name","birth_date","class_name","address","pinfl","passport","father_name","father_phone",
              "father_passport","mother_name","mother_phone","mother_passport","career_interest","notes"]
        vals=[request.form.get(k,"").strip() for k in keys]
        filename=student["certificate_file"]
        f=request.files.get("certificate_file")
        if f and f.filename and allowed_file(f.filename):
            filename=secure_filename(f.filename)
            stem,ext=os.path.splitext(filename); i=1
            while os.path.exists(os.path.join(UPLOAD_DIR,filename)):
                filename=f"{stem}_{i}{ext}"; i+=1
            f.save(os.path.join(UPLOAD_DIR,filename))
        con.execute("""UPDATE students SET full_name=?,birth_date=?,class_name=?,address=?,pinfl=?,passport=?,
        father_name=?,father_phone=?,father_passport=?,mother_name=?,mother_phone=?,mother_passport=?,
        career_interest=?,notes=?,certificate_file=?,updated_at=CURRENT_TIMESTAMP WHERE id=?""",(*vals,filename,sid))
        con.commit(); con.close()
        flash("Ma’lumotlar yangilandi.","success")
        return redirect(url_for("students"))
    con.close()
    return render_template("student_form.html",student=student,title="O‘quvchini tahrirlash")

@app.post("/student/<int:sid>/delete")
@login_required
def delete_student(sid):
    con=db(); row=con.execute("SELECT certificate_file FROM students WHERE id=?",(sid,)).fetchone()
    con.execute("DELETE FROM students WHERE id=?",(sid,)); con.commit(); con.close()
    if row and row["certificate_file"]:
        try: os.remove(os.path.join(UPLOAD_DIR,row["certificate_file"]))
        except OSError: pass
    flash("O‘quvchi o‘chirildi.","success")
    return redirect(url_for("students"))

@app.route("/uploads/<path:name>")
@login_required
def uploaded(name):
    return send_from_directory(UPLOAD_DIR,name)

if __name__=="__main__":
    app.run(debug=True)

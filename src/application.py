from tempfile import mkdtemp

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.exceptions import HTTPException, InternalServerError, default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///social_network.db")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # route via 'post' user clicked on the registration button
    if request.method == "POST":
        # render apology if username input field is blank
        if not request.form.get("username"):
            return apology("username field can't be blank", 400)
        # render apology if either password or confirmation field is blank
        if not request.form.get("password") or not request.form.get("confirmation"):
            return apology("password field can't be blank", 400)
        # query database for username
        username_db_query = db.execute(
            "SELECT username FROM users WHERE username = ?",
            request.form.get("username"),
        )
        # registrate user
        if len(username_db_query) == 0:
            # insert new user into db, storing username and hash of the user's password
            if request.form.get("password") == request.form.get("confirmation"):
                db.execute(
                    "INSERT INTO users (username, hash) VALUES (?,?)",
                    request.form.get("username"),
                    generate_password_hash(request.form.get("password")),
                )
            # render apology if password confirmation dosen't match
            else:
                return apology("passwords don't match", 400)
        # render apology if username is aready exists
        else:
            return apology("username is already exists", 400)
        # redirect users so they can login themselves
        return redirect("/")
    # route via 'get', by clicking on link or redirect
    else:
        return render_template("auth/register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 400)
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        # Redirect user to home page
        return redirect("/")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("auth/login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route("/")
@login_required
def index():
    """Show all users"""
    # list of all stocks that user currently possess
    users_db = db.execute("SELECT id, username FROM users ORDER BY id")
    return render_template("index.html", users=users_db)


@app.route("/message", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # route via 'post' after clicking the button
    if request.method == "POST":
        username = request.form.get("username")
        text = request.form.get("text")
        # ensure field not empty
        if not (username or text):
            return apology("missing username or message")
        else:
            if not (
                to_user_id := db.execute(
                    "SELECT id FROM users WHERE username = ?", username
                )
            ):
                return apology("invalid username")
            db.execute(
                "INSERT INTO messages (from_user, to_user, message) VALUES (?,?,?)",
                session["user_id"],
                to_user_id[0]["id"],
                text,
            )
            return redirect("/")
    else:
        return render_template("message.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # get user id
    user_id = session["user_id"]
    # get transaction history for a user
    user_history_db = db.execute(
        """SELECT username, message, message_time 
        FROM users, messages 
        WHERE users.id = messages.from_user and to_user= ? 
        ORDER BY message_time DESC""",
        user_id,
    )
    return render_template("history.html", user_history=user_history_db)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


if __name__ == "__main__":
    app.run(debug=False, threaded=True, port=8080)

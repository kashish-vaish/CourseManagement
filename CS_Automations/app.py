from flask import Flask, render_template, request
from canvaslogsproctoring import get_blur_events
from attendance import get_attendance_status

app = Flask(__name__)
attendance_cache = {} 

@app.route("/")
def home():
    return render_template("home.html", active_page="home")

@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    date_filter = request.values.get("date", "")
    selected_uid = request.values.get("uid", "").strip()
    current_page = int(request.args.get("page", 1))
    page_size = 20
    table = []

    if date_filter:
        if date_filter in attendance_cache:
            table = attendance_cache[date_filter]
        else:
            try:
                df = get_attendance_status(date_filter)
                table = df.to_dict(orient="records")
                attendance_cache[date_filter] = table
            except Exception as e:
                return f"<h3>Error loading attendance data: {e}</h3>"

        #  Filter by UID if provided
        if selected_uid:
            table = [row for row in table if row.get("uid", "").lower() == selected_uid.lower()]

    total_pages = (len(table) + page_size - 1) // page_size
    start = (current_page - 1) * page_size
    end = start + page_size

    return render_template(
        "attendance.html",
        table=table,
        selected_date=date_filter,
        selected_uid=selected_uid,
        current_page=current_page,
        total_pages=total_pages,
        start=start,
        end=end
    )
        

@app.route("/quiz-monitor", methods=["GET", "POST"])
def quiz_monitor():
    data = []
    quiz_id = ""

    if request.method == "POST":
        quiz_id = request.form.get("quiz_id")
        if quiz_id:
            try:
                data = get_blur_events(quiz_id=quiz_id, course_id=330127)
            except Exception as e:
                data = [{"error": f"Failed to fetch data: {e}"}]

    return render_template("quiz_monitor.html", data=data, quiz_id=quiz_id, active_page="quiz")

if __name__ == "__main__":
    app.run(debug=True)

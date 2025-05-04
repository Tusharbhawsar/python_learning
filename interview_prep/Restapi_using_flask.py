from flask import Flask ,jsonify
app =Flask(__name__)

@app.route("/armstrong/<int:n>")
def check_armstrong(n):
    df = list(str(n))

    check = 0
    for i in df:
        if len(str(n)) == 3:
            ds = int(i) * int(i) * int(i)
        else:
            ds = int(i) * int(i) * int(i) *int(i)
        check += ds

    if check == n:
        result = {

            "number" :n,
            "armstrong":True,
            "server ip":"127.0.0.1:5000"
        }
    else:
        result = {
            "number" :n,
            "armstrong":False,
            "server ip" : "127.0.0.1:5000"
        }

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug = True)
from flask import Flask, render_template

app = Flask(__name__)


def test():
    print("test")


@app.route('/')
def hello():
    test()
    return render_template('index.html')


app.run()
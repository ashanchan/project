from flask import Flask, render_template
app = Flask(__name__)
 
@app.route('/<string:page_name>/')

def render_static(page_name):
    return render_template('%s.html' % page_name)
 
if __name__ == '__main__':
    app.run()



    #html = '<iframe allow="microphone;" width="350" height="430" src="https://console.dialogflow.com/api-client/demo/embedded/b71d1505-6bbc-4467-8ed8-7009bbb13434"></iframe>'
    #return html

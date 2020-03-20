from flask import Flask
from crawler.pluginframe.main import run_plugin
from crawler.tools.chengji.process_manage import MyProcess
app = Flask(__name__)
mp = MyProcess()


@app.route('/run/<plugin_name>')
def run(plugin_name):
    print(plugin_name)
    start_status = mp.add(run_plugin,plugin_name,plugin_name)
    if start_status==1:
        return {'msg':'ok'}
    return {'msg':'failure'}
@app.route('/stop/<plugin_name>')
def stop(plugin_name):
    start_status = mp.terminate_by_name(plugin_name)
    if start_status==1:
        return {'msg':'ok'}
    return {'msg':'failure'}



if __name__ == '__main__':
    app.run()

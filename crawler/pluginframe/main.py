
import importlib,os
from crawler.tools.chengji.utils import ProxyTool
chengji_module_path = 'E:\ZF\crawler\plugin\chengji'
chengji_module_name_suffix_list = os.listdir(chengji_module_path)
chengji_module_name_pre = 'crawler.plugin.chengji.'
module_name_dic =  {module_name_suffix[:-3]:chengji_module_name_pre+ module_name_suffix[:-3]\
                    for module_name_suffix in chengji_module_name_suffix_list \
                    if '.py' in module_name_suffix and not('__init__' in module_name_suffix)}


def run_plugin(modulename):
    ProxyTool().add_to_white_list()
    module_name = module_name_dic.get(modulename)
    module = importlib.import_module(module_name)
    module.run()



if __name__ == '__main__':
    ProxyTool().add_to_white_list()
    run_plugin('chengjizf_detail_page')
    # importlib.import_module('plugin.chengji.chengjizf_list_page')



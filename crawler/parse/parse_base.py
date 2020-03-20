



class ParseBase(object):

    def __init__(self):

        pass


    def check_keys_exists(self,key_list, total_map):

        added_key = set(key_list) - set(total_map.keys())
        if added_key == set():
            return True
        else:
            raise BaseException('新增Key{0}'.format(added_key))

    def is_all_chinese(self,strs):
        for _char in strs:
            if not '\u4e00' <= _char <= '\u9fa5':
                return False
        return True

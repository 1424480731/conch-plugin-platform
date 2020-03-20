from pymongo import MongoClient
from gridfs import GridFS


class GFS(object):
    def __init__(self, dbname, setname):
        self.dbname = dbname
        self.setname = setname

    def createDB(self):  # 连接数据库，并创建文件数据库与数据表
        client = MongoClient('localhost', 27017)
        db = client[self.dbname]
        setname = db[self.setname]
        return (db, setname)

    def insertFile(self, db, filePath, query):  # 将文件存入数据表
        fs = GridFS(db, self.setname)
        if fs.exists(query):
            print('已经存在该文件')
        else:
            with open(filePath, 'rb') as fileObj:
                data = fileObj.read()
                ObjectId = fs.put(data, filename=filePath.split('\\')[-1])
                fileObj.close()
            return ObjectId

    def getID(self, db, query):  # 通过文件属性获取文件ID，ID为文件删除、文件读取做准备
        fs = GridFS(db, self.setname)

        ObjectId = fs.find_one(query)._id
        return ObjectId

    def getFile(self, db, id):  # 获取文件属性，并读出二进制数据至内存
        fs = GridFS(db, self.setname)
        gf = fs.get(id)
        bdata = gf.read()  # 二进制数据
        attri = {}  # 文件属性信息
        attri['chunk_size'] = gf.chunk_size
        attri['length'] = gf.length
        attri["upload_date"] = gf.upload_date
        attri["filename"] = gf.filename
        attri['md5'] = gf.md5
        return (bdata, attri)

    def listFile(self,db): #列出所有文件名
        fs = GridFS(db, self.setname)
        gf = fs.list()
        file_dic = {}
        for g in gf:
            file_dic.update({'filename':g})
        return file_dic

    def findFile(self,db): #列出所有文件二进制数据
        fs = GridFS(db,self.setname)
        for file in fs.find():
            bdata=file.read()
        print(bdata)

    def write_2_disk(self, bdata, attri):  # 将二进制数据存入磁盘
        name = "get_" + attri['filename']
        if name:
            output = open(name, 'wb')
        output.write(bdata)
        output.close()

    def remove(self, db, id):  # 文件数据库中数据的删除
        fs = GridFS(db, self.setname)
        fs.delete(id)
        print('该图片已经删除')


if __name__ == '__main__':
    gfs = GFS('zf', 'cjzf')
    (dbname, setname) = gfs.createDB()
    filePath = r'C:\Users\Public\Pictures\Sample Pictures\c.jpg'
    query = {'filename': 'c.jpg'}
    id = gfs.insertFile(dbname, filePath, query)  # 插入文件
    # querys = gfs.listFile(dbname)
    id = gfs.getID(dbname, query)
    # gfs.findFile(dbname)
    # gfs.remove(dbname,id)
    # print(id)
    # (bdata, attri) = gfs.getFile(dbname, id)  # 查询并获取文件信息至内存
    # gfs.write_2_disk(bdata, attri)  # 写入磁盘

from qiniu import Auth, put_data

access_key = '8T7-8-mzIXE_VQoVpsijWUNLeISLBjE3NPeIF9yg'
secret_key = 'cu75J0_Mcul2LCgGWajiJvMGpTvpxZra6MPHHPmO'

def storage(data):
    # 构建鉴权对象 ,网络请求
    q = Auth(access_key, secret_key)

    # 要上传的空间
    bucket_name = 'demo'

    # 生成上传 Token，指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)

    ret, info = put_data(token, None, data)
    if info.status_code != 200:
        raise Exception('上传失败')
    print(info)
    print(ret)
    # KEY就是文件名
    return ret['key']

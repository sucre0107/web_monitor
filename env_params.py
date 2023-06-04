import os

class EnvParams():
    def __init__(self):
        self.env_file = '.env'
        self.env_vars = {}

    def load_env(self):
        # 如果存在本地的 .env 文件，则从文件中加载环境变量
        if os.path.exists(self.env_file):
            with open(self.env_file) as f:
                for line in f:
                    key, value = line.strip().split('=', 1)
                    self.env_vars[key] = value

        # 如果没有 .env 文件，则读取系统环境变量
        else:
            self.env_vars = os.environ


    def get_var(self, key):
        return self.env_vars.get(key)

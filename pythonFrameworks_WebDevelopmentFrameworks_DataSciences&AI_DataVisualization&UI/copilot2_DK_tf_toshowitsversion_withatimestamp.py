from datetime import datetime

import tensorflow as tf

def show_tensorflow_version():
    now = datetime.now()
    print("TensorFlow version:",tf.__version__, " at ", now)

if __name__=="__main__":
    show_tensorflow_version()

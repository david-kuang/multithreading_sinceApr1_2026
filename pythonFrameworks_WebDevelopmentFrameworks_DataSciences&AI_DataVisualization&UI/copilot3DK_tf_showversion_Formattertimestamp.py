from datetime import datetime

import tensorflow as tf

def show_tensorflow_version3():
    dt_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("TensorFlow version:", tf.__version__, "at", dt_string, " !")

if __name__=="__main__":
    show_tensorflow_version3()

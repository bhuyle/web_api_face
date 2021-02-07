### Build Opencv in Ubuntu
```Shell
Follow in link: https://learnopencv.com/install-opencv-4-on-ubuntu-18-04/
```

### Building PCN

Build the library
```Shell
sudo apt-get install libgoogle-glog-dev libopencv-dev libboost-system-dev
```
For python interface (only supported in Ubuntu 18.04):
```Shell
sudo apt install libcaffe-cpu-dev
make
sudo make install
```
```Shell
python3 app.py
```


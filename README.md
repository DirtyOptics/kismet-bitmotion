# kismet-bitmotion

#### Clone Repo
```
git clone https://github.com/DirtyOptics/kismet-bitmotion.git
```

#### Nav to repo
```
cd kismet-bitmotion
```

#### Create python virtual environment (environment called vws)
```
sudo python3 -m venv vws
```

#### Activate 'kismet' virtual environment
```
source vws/bin/activate
```

#### You may need to change permissions of the pulled folder:
```
sudo chown -R $(whoami) /home/user/kismet-bitmotion
sudo chmod -R u+rwX /home/user/kismet-bitmotion
```

#### Install the items from inside requirements.txt
```
pip install -r requirements.txt
```

# Raspberry Pi Controlled Borg

## Installation Steps
### Hardware
Assemble and build the DiddyBorg following instructions [here](https://www.piborg.org/blog/diddyborg-build-instructions "PiBorg|DiddiBorg")
### Test
```bash
bash <(curl https://www.piborg.org/installer/install-picoborgrev.txt)
./picoborgrev/pbrSequence.py 

```
### Software
Connect to your raspberrypi, clone this repo and run the install scripts
```bash
git clone https://github.com/zuvam/piborg.git
cd piborg
sudo ./install_motion.sh -i
sudo ./install_wiimotes.sh -i
systemctl status motion
systemctl status wiimote
```




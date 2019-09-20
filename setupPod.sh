yum install procps
yum install python36
yum install zip
yum install vim

curl http://blzdistsc2-a.akamaihd.net/Linux/SC2.4.10.zip --output /root/StarCraftII.zip
unzip /root/StarCraftII.zip

cd /root/
git clone https://github.com/AdamSchunk/sc2reader.git
git clone https://github.com/AdamSchunk/pysc2.git

cp /root/pysc2/pysc2/maps/minigames /root/StarCraftII/Maps/

pip3 install --upgrade /root/sc2reader/
pip3 install --upgrade /root/pysc2/
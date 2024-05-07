source ~/.bash_profile
cd /data/django/xjny/lims
python efficiencymonitor.py  > /tmp/efficiencymonitor.log  2>&1
python efficiencymonitor_yanfa.py  >> /tmp/efficiencymonitor.log  2>&1
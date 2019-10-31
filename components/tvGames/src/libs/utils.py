import subprocess
try:
    from termcolor import cprint
    def printerr(str):
        cprint(str, color="red")
except:
    def printerr(str):
        print(str)

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
    print("Initiating Touch device")
    hdmi_devides, result = get_HDMI_devices_id()
    if result and len(hdmi_devides)>0:
        hdmi_device = hdmi_devides[0]
        touch_devices, result = get_touchscreen_devide_id()
        if result and len(touch_devices):
            touch_device = touch_devices[0]
            print("Located HDMI: %s and TouchDevice %d" % (hdmi_device, touch_device))
            command = "xinput --map-to-output %d %s" % (touch_device, hdmi_device)
            try:
                command_output = subprocess.Popen(command,
                                                  stdout=subprocess.PIPE,
                                                  stderr=subprocess.STDOUT, shell=True)
                stdout, stderr = command_output.communicate()
            except:
                printerr("Problem found while executing command %s"%(command) )
                return False
            else:
                if stderr == None and "not found" not in stdout:
                    return True
                else:
                    printerr("Problem found while executing command %s" % (command))
                    return False
        else:
            printerr("No touch device found. Can't initialice it")
            return False
    else:
        printerr("No HDMI device found. Can't initialice touch screen to any device")
        return False




if __name__ == '__main__':
    print (init_touchscreen_device())
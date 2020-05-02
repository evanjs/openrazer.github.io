#!/usr/bin/env python3
#
# Enumerates the daemon's classes and uses those URLs
#

import os
import sys
import inspect
import re
lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "openrazer", "daemon", "openrazer_daemon", "hardware"))
sys.path.append(lib_path)

# "openrazer" directory expected in parent folder.
import keyboards
import mouse
import mouse_mat
import core
import headsets
import accessory

razer_devices = []
html_keyboards = ""
html_mice = ""
html_other = ""

# Gather list of devices by looking in Razer* classes
for module in [keyboards, mouse, mouse_mat, core, headsets, accessory]:
    for inspection in inspect.getmembers(module):
        if inspection[0].startswith("Razer"):
            razer_devices.append(inspection[1])

for device in razer_devices:
    device_type = inspect.getmodule(device).__name__
    device_name = device.__name__
    lsusb = str(hex(device.USB_VID))[-4:] + ":" + str(hex(device.USB_PID))[-4:]
    lsusb = lsusb.replace("x", "0").upper()

    # Prevent duplicates (wired/wireless sets)
    if device_name.endswith("Wired"):
        continue
    elif device_name.endswith("Wireless"):
        device_name = device_name.replace("Wireless", "")

    # Get and validate URLs
    device_img_url = device.DEVICE_IMAGE

    if not device_img_url:
        print("Missing image URL for " + device_name)
        device_img_url = "img/placeholder.png"

    # Strip Razer name
    device_name = device_name.replace("Razer", "")

    # Clean up name from class
    device_name_ui = re.sub(r"(\w)([A-Z])", r"\1 \2", device_name)
    device_name_ui = device_name_ui \
                        .replace("Black Widow", "BlackWidow") \
                        .replace("Death Adder", "DeathAdder") \
                        .replace("Death Stalker", "DeathStalker") \
                        .replace("TE", "Tournament Edition") \
                        .replace("20", " 20") \
                        .replace("3500", " 3500") \
                        .replace("QH D", "QHD") \
                        .replace(" X", " X ") \
                        .replace("Abyssus1800", "Abyssus 1800") \
                        .replace("Kraken71", "Kraken 7.1") \
                        .replace("Adder3_5 G", "Adder 3.5G") \
                        .replace("Adv", "Advanced")

    def get_device_html(img_url, name):
        print("Adding " + name + "...")
        element_id = name.lower().replace(" ", "-")
        return """
            <div id="{2}" class="col-md-3 col-sm-4 device-icon">
                <div class="inner" data-image="{0}"></div>
                <h5>{1}</h5>
                <h5><code>{3}</code></h5>
            </div>
            """.format(img_url, name, element_id, lsusb).strip()

    html_buffer = "            " + get_device_html(device_img_url, device_name_ui) + "\n"

    if device_type == "keyboards":
        html_keyboards += html_buffer

    elif device_type in ["mouse", "mouse_mat"]:
        html_mice += html_buffer

    else:
        html_other += html_buffer

# Replace sections
with open("index.html") as f:
    raw_html = f.readlines()
index_html = "".join(raw_html)

def update_placeholders(html_data, placeholder_name):
    global index_html
    before_comment = "                <!-- START {0} -->".format(placeholder_name)
    after_comment = "                <!-- END {0} -->".format(placeholder_name)
    before = index_html.split(before_comment)
    after = index_html.split(after_comment)
    index_html = before[0] + before_comment + "\n" + html_data + "\n" + after_comment + after[1]

update_placeholders(html_keyboards, "KEYBOARD")
update_placeholders(html_mice, "MICE")
update_placeholders(html_other, "OTHER")

with open("index.html", "w") as f:
    f.writelines(index_html)

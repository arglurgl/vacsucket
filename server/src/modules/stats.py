import libs.modules as m
import json
from os import getenv


def parse_proc_wifi(line_list: list):
    wireless_extension_version = line_list[1].split("|")[-1].strip()
    if not wireless_extension_version == "22":
        m.log.warning(
            "The parser was tested against version 22 of the wireless extension, your version is: "
            + wireless_extension_version
        )

    map_dict = {}
    for line in line_list[2:]:  # skip the first two lines
        split = line.split()

        map_dict[split[0]] = {
            "status": split[1],
            "Quality": {
                "link": float(split[2]),
                "level": float(split[3]),
                "noise": int(split[4]),
            },
            "Discarded_packets": {
                "nwid": int(split[5]),
                "crypt": int(split[6]),
                "frag": int(split[7]),
                "retry": int(split[8]),
                "misc": int(split[9]),
            },
            "Missed_beacon": int(split[10]),
        }
    return map_dict, wireless_extension_version


def stats(parameter):
    m.log.info("stats where requested")

    match parameter.split()[0]:
        case "wifi":
            m.log.info("processing wifi stats ...")
            try:
                proc_wireless = getenv("PROC_WIRELESS")
            except Exception:
                proc_wireless = "/proc/net/wireless"
            with open(proc_wireless, "r") as file_d:
                return json.dumps(parse_proc_wifi(file_d.readlines()))

    m.log.warning("no parameter matched: " + str(parameter))
    return "Nothing matched, try again"

m.register("stats", stats)

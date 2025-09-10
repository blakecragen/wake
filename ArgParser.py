import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import argparse
import json
from pathlib import Path

TYPE_MAP = {
    "int": int,
    "str": str,
    "float": float,
    "bool": bool
}

class ArgParser:
    def __init__(self, json_path: str = "args.json"):
        self.json_path = Path(json_path)

    def load_specs(self):
        with open(self.json_path) as f:
            data = json.load(f)

        for arg in data:
            kwargs = arg["kwargs"]
            # convert string "int" → Python int, etc.
            if "type" in kwargs and isinstance(kwargs["type"], str):
                if kwargs["type"] in TYPE_MAP:
                    kwargs["type"] = TYPE_MAP[kwargs["type"]]
        return data

    def build(self, prog="wake", description="Send Wake-on-LAN packets"):
        p = argparse.ArgumentParser(
            prog=prog,
            description=description
        )

        # special group for port/no-port exclusivity
        port_group = p.add_mutually_exclusive_group()

        for arg in self.load_specs():
            flags = arg["flags"]
            kwargs = arg["kwargs"].copy()
            group = kwargs.pop("group", None)

            if len(flags) == 1 and not flags[0].startswith("-"):
                # positional arg like "name"
                p.add_argument(*flags, **kwargs)
            else:
                if group == "port_group":
                    port_group.add_argument(*flags, **kwargs)
                else:
                    p.add_argument(*flags, **kwargs)

        return p


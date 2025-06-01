# Timedial.org Simulators

Our simulators are based on the publicly available [SIMH](https://github.com/simh/simh) codebase.

A variety of simulators are available. When you open one, all relevant files are copied to your home directory under `~/simulators` before the simulator is started. This means each simulator is personal to you—you’re free to modify anything, including the `simh.ini` files.

## Creating or Copying Simulators

If you want to create a new simulator from scratch or maintain multiple copies of the same simulator, there are two easy ways to launch them:

1. **From the shell:**  
   Run `timedial-start-sim <sim_name>`.  
   For example, if your simulator is in `~/simulators/mysim`, you would run:  
   ```
   timedial-start-sim mysim
   ```

2. **From the menu:**  
   Add or edit a `simulator.toml` file inside the simulator directory.

Below is a sample configuration file used for one of our existing simulators:
```
[emulator] # Required
label = "PDP-11 with 2.11BSD"
command = "pdp11 pdp11.ini"

[description] # Optional
publisher = "BSD"
original_date = "1978"
version = "2.11"
version_date = "1992"
text = [
    "Digital Equipment Corporation's famous 1975 PDP-11/70, running 2.11BSD!",
    "This mini-computer is fully decked out with 4MiB of memory.",
]
login_information = [
    "Username: root / Password: None",
    "At the boot prompt (:), press Enter to boot.",
    "At the single-user prompt (#), press Ctrl+D to enter multi-user mode.",
]
```

Only the `[emulator]` section is required—the rest is optional and can be customized as needed. Once the `simulator.toml` file is updated, your simulator will appear in the main menu of TimeDial.org.

## Compression

To conserve disk space, all emulator disk images are automatically compressed when you're not using them and uncompressed when you start. This process takes just a few seconds and can reduce image sizes by as much as 98%, depending on the contents. The compression is seamless and does not require any manual intervention.

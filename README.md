# CloudComputingPartII-Individual

## Setup

I have managed the Python environment and dependencies using the uv tool. In order to make it available in `PATH`, please run the command:

```sh
./setup-python.sh
```

## Running

To run the script, run the command, replacing {input_file} with the absolute path to the file to run the static allocation on. The name of the file should have the file size in it, in the form data-XXXMB.txt:

```sh
uv run static_allocation_scheduler.py {input_file}
```

To implement the cuttoff scheduler (an extra scheduler that responds a little more intelligently than the simple minimisation scheduler), run with the flag:

```sh
uv run static_allocation_scheduler.py {input_file} --cutoff_scheduler
```
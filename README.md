      _____  _                   ____   _         _                      
     |_   _|(_) _ __ ___    ___ |  _ \ (_)  __ _ | |    ___   _ __  __ _ 
       | |  | || '_ ` _ \  / _ \| | | || | / _` || |   / _ \ | '__|/ _` |
       | |  | || | | | | ||  __/| |_| || || (_| || | _| (_) || |  | (_| |
       |_|  |_||_| |_| |_| \___||____/ |_| \__,_||_|(_)\___/ |_|   \__, |
                                                                   |___/ 


## Development

### Setting Up Environment

1. Clone the repository and navigate into it:
   ```bash
   git clone <repo-url>
   cd timedial
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the project along with development dependencies:
   ```bash
   pip install -e .[dev]
   ```
4. Pre-commit hooks help maintain code quality:

   ```bash
   pre-commit install
   pre-commit run --all-files
   ```

## License

This project is licensed under the GPL v3 License. See `LICENSE` for details.

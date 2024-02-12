# caxe
Credential Attribute XBRL Extraction

### Development

#### Build from source

* Setup virtual environment:
    ```bash
    python3 -m venv venv
    ```
* Activate virtual environment:
    ```bash
    source venv/bin/activate
    ```
* Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```


## Run CAXE api

- Navigate to `scripts` directory:
    ```bash
    cd scripts
    ```

- Need to source the file `env.sh` into your current shell to set the environment variables

    ```bash
    source ./env.sh;
    ```

- Start `caxe` service

    ```bash
    ./start.sh
    ```